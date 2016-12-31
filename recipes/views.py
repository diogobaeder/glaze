from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    DetailView,
    ListView,
)
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)

from recipes.models import Ingredient, Recipe


class UserBound:
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return self.model.objects.for_user(self.request.user)


@method_decorator(login_required, name='dispatch')
class IngredientList(UserBound, ListView):
    model = Ingredient


@method_decorator(login_required, name='dispatch')
class IngredientDetail(UserBound, DetailView):
    model = Ingredient
    context_object_name = 'ingredient'


@method_decorator(login_required, name='dispatch')
class IngredientCreate(UserBound, CreateView):
    model = Ingredient
    fields = ['name', 'kind', 'price']


@method_decorator(login_required, name='dispatch')
class IngredientUpdate(UserBound, UpdateView):
    model = Ingredient
    fields = ['name', 'kind', 'price']


@method_decorator(login_required, name='dispatch')
class IngredientDelete(UserBound, DeleteView):
    model = Ingredient
    success_url = reverse_lazy('ingredients')


@login_required
def recipes(request):
    recipes = Recipe.objects.for_user(request.user)
    return render(request, 'recipes.html', {
        'recipes': recipes,
    })
