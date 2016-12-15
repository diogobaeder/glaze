from django.contrib.auth.models import User
from django.db import models


class UserBoundModel(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        unique_together = (('user', 'name'),)


class Ingredient(UserBoundModel):
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Recipe(UserBoundModel):
    ingredients = models.ManyToManyField(Ingredient, through='RecipePart')

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
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
