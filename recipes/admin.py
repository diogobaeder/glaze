from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipePart


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'kind_name')


class RecipePartInline(admin.TabularInline):
    model = RecipePart


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipePartInline,
    ]
