from django.contrib.auth.decorators import login_required
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

from recipes.forms import IngredientForm, RecipeForm, RecipePartFormset
from recipes.models import Ingredient, Recipe


class UserBound:
    context_object_name = 'instance'

    def get_queryset(self):
        return self.model.objects.for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['model_name'] = self.model._meta.verbose_name.title()
        context['model_name_plural'] = (
            self.model._meta.verbose_name_plural.title())
        context['path_prefix'] = self.model.path_prefix
        context['path_prefix_plural'] = self.model.path_prefix_plural

        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.instance.user = self.request.user
        return form

    def get_success_url(self):
        return reverse_lazy(self.model.path_prefix_plural)


class IngredientBound(UserBound):
    model = Ingredient
    form_class = IngredientForm


class RecipeBound(UserBound):
    model = Recipe
    form_class = RecipeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['recipe_part_form'] = RecipePartFormset(self.request.POST)
        else:
            context['recipe_part_form'] = RecipePartFormset()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        recipe_part_form = context['recipe_part_form']
        if recipe_part_form.is_valid():
            self.object = form.save()
            recipe_part_form.instance = self.object
            recipe_part_form.save()
            return super().form_valid(form=form)
        else:
            return super().form_invalid(form=form)


@method_decorator(login_required, name='dispatch')
class IngredientList(IngredientBound, ListView):
    pass


@method_decorator(login_required, name='dispatch')
class IngredientDetail(IngredientBound, DetailView):
    pass


@method_decorator(login_required, name='dispatch')
class IngredientCreate(IngredientBound, CreateView):
    pass


@method_decorator(login_required, name='dispatch')
class IngredientUpdate(IngredientBound, UpdateView):
    pass


@method_decorator(login_required, name='dispatch')
class IngredientDelete(IngredientBound, DeleteView):
    pass


@method_decorator(login_required, name='dispatch')
class RecipeList(RecipeBound, ListView):
    pass


@method_decorator(login_required, name='dispatch')
class RecipeDetail(RecipeBound, DetailView):
    pass


@method_decorator(login_required, name='dispatch')
class RecipeCreate(RecipeBound, CreateView):
    pass


@method_decorator(login_required, name='dispatch')
class RecipeUpdate(RecipeBound, UpdateView):
    pass


@method_decorator(login_required, name='dispatch')
class RecipeDelete(RecipeBound, DeleteView):
    pass
