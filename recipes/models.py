from decimal import Decimal
from enum import IntEnum

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from enumfields import EnumIntegerField
from sorl.thumbnail import ImageField


class PrettyIntEnum(IntEnum):
    def __str__(self):
        return self.name


class Kind(PrettyIntEnum):
    Base = 0
    Addition = 1


class WeightUnit(PrettyIntEnum):
    g = 0
    Kg = 1

    def weighted_in(self, weight_unit):
        if self is self.Kg and weight_unit is self.g:
            return Decimal('1000')
        if self is self.g and weight_unit is self.Kg:
            return Decimal('0.001')
        return Decimal('1')


class UserBoundManager(models.Manager):
    def for_user(self, user):
        return self.filter(user=user)


class UserBoundModel(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    kind = EnumIntegerField(Kind)
    weight_unit = EnumIntegerField(WeightUnit)

    path_prefix = 'ingredient'
    path_prefix_plural = 'ingredients'


class Recipe(UserBoundModel):
    ingredients = models.ManyToManyField(Ingredient, through='RecipePart')
    description = models.TextField(blank=True, null=True)
    image = ImageField(blank=True, null=True)

    path_prefix = 'recipe'
    path_prefix_plural = 'recipes'

    REFERENCE_WEIGHT_UNIT = WeightUnit.Kg

    def add_part(self, ingredient, quantity):
        RecipePart.objects.create(
            recipe=self,
            ingredient=ingredient,
            quantity=quantity,
        )

    @property
    def parts(self):
        return RecipePart.objects.filter(recipe=self)

    @property
    def price(self):
        price = Decimal('0')

        for part in self.parts:
            i = part.ingredient
            price += (
                i.price * part.quantity
                * self.REFERENCE_WEIGHT_UNIT.weighted_in(i.weight_unit)
            )

        return price


class RecipePart(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=4,
                                   verbose_name='Amount')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
