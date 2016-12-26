from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from recipes.models import Ingredient, Recipe


@login_required
def ingredients(request):
    ingredients = Ingredient.objects.for_user(request.user)
    return render(request, 'ingredients.html', {
        'ingredients': ingredients,
    })


@login_required
def recipes(request):
    recipes = Recipe.objects.for_user(request.user)
    return render(request, 'recipes.html', {
        'recipes': recipes,
    })
