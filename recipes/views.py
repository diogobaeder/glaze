from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from recipes.models import Ingredient


@login_required
def ingredients(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'ingredients.html', {
        'ingredients': ingredients,
    })
