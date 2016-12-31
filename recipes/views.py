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


class IngredientBound(UserBound):
    model = Ingredient
    fields = ['name', 'kind', 'price']


@method_decorator(login_required, name='dispatch')
class IngredientList(IngredientBound, ListView):
    pass


@method_decorator(login_required, name='dispatch')
class IngredientDetail(IngredientBound, DetailView):
    context_object_name = 'ingredient'


@method_decorator(login_required, name='dispatch')
class IngredientCreate(IngredientBound, CreateView):
    pass


@method_decorator(login_required, name='dispatch')
class IngredientUpdate(IngredientBound, UpdateView):
    pass


@method_decorator(login_required, name='dispatch')
class IngredientDelete(IngredientBound, DeleteView):
    success_url = reverse_lazy('ingredients')


@login_required
def recipes(request):
    recipes = Recipe.objects.for_user(request.user)
    return render(request, 'recipes.html', {
        'recipes': recipes,
    })
