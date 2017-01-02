from enum import IntEnum

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from enumfields import EnumIntegerField
from sorl.thumbnail import ImageField


class Kind(IntEnum):
    BASE = 0
    ADDITION = 1


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

    path_prefix = 'ingredient'
    path_prefix_plural = 'ingredients'

    @property
    def kind_name(self):
        return self.kind.name.capitalize()


class Recipe(UserBoundModel):
    ingredients = models.ManyToManyField(Ingredient, through='RecipePart')
    description = models.TextField(blank=True, null=True)
    image = ImageField(blank=True, null=True)

    path_prefix = 'recipe'
    path_prefix_plural = 'recipes'

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
        price = 0

        for part in self.parts:
            price += (part.ingredient.price * part.quantity)

        return price


class RecipePart(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=4,
                                   verbose_name='Amount')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
