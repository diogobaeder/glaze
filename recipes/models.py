from decimal import Decimal
from enum import IntEnum

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext as _
from enumfields import EnumIntegerField
from sorl.thumbnail import ImageField


ZERO = Decimal('0')
PERCENT = Decimal('100')


class PrettyIntEnum(IntEnum):
    def __str__(self):
        return _(self.name)


class Kind(PrettyIntEnum):
    Base = 0
    Addition = 1


_('Base')
_('Addition')


class WeightUnit(PrettyIntEnum):
    g = 0
    Kg = 1

    def weighted_in(self, weight_unit):
        if self is self.Kg and weight_unit is self.g:
            return Decimal('1000')
        if self is self.g and weight_unit is self.Kg:
            return Decimal('0.001')
        return Decimal('1')


REFERENCE_WEIGHT_UNIT = WeightUnit.Kg


class UserBoundManager(models.Manager):
    def for_user(self, user):
        return self.filter(user=user)


class DateBoundModel(models.Model):
    created = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True


class UserBoundModel(DateBoundModel):
    user = models.ForeignKey(User)
    name = models.CharField(_('Name'), max_length=200)

    objects = UserBoundManager()

    class Meta:
        abstract = True
        unique_together = (('user', 'name'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('{}-detail'.format(self.path_prefix),
                       kwargs={'pk': self.pk})


class Ingredient(UserBoundModel):
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    kind = EnumIntegerField(Kind, verbose_name=_('Kind'))
    weight_unit = EnumIntegerField(WeightUnit, verbose_name=_('Weight unit'))

    path_prefix = 'ingredient'
    path_prefix_plural = 'ingredients'

    class Meta:
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')
        ordering = ['name']

    @property
    def kind_string(self):
        return str(self.kind)


class Recipe(UserBoundModel):
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipePart', verbose_name=_('Ingredients'))
    description = models.TextField(_('Description'), blank=True, null=True)
    image = ImageField(_('Image'), blank=True, null=True)

    path_prefix = 'recipe'
    path_prefix_plural = 'recipes'

    class Meta:
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')

    def add_part(self, ingredient, percentage):
        RecipePart.objects.create(
            recipe=self,
            ingredient=ingredient,
            percentage=percentage,
        )

    @property
    def parts(self):
        return RecipePart.objects.filter(recipe=self)

    @property
    def price(self):
        price = ZERO
        final_percentage = ZERO

        for part in self.parts:
            i = part.ingredient
            price += (
                i.price * part.percentage
                * REFERENCE_WEIGHT_UNIT.weighted_in(i.weight_unit)
            )
            final_percentage += part.percentage

        if final_percentage == ZERO:
            return ZERO

        return price / final_percentage

    def clone(self):
        parts = self.parts
        self.name = '{} (Copy of {})'.format(self.name, self.pk)
        self.pk = None
        self.id = None
        self.save()

        for part in parts:
            part.pk = None
            part.id = None
            part.recipe = self
            part.save()

        return self


class RecipePart(DateBoundModel):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name=_('Recipe'))
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name=_('Ingredient'))
    percentage = models.DecimalField(
        _('Percentage'), max_digits=10, decimal_places=4)

    @property
    def relative_price(self):
        return (
            self.ingredient.price * self.percentage *
            REFERENCE_WEIGHT_UNIT.weighted_in(self.ingredient.weight_unit)
            / PERCENT
        )

    class Meta:
        verbose_name = _('Recipe part')
        verbose_name_plural = _('Recipe parts')
