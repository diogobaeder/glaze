from django.contrib import admin
from django.utils.translation import ugettext as _

from recipes.models import Ingredient, Recipe, RecipePart


def price(instance):
    return '{:.2f}/{}'.format(instance.price, str(instance.weight_unit))


price.admin_order_field = 'price'
price.short_description = _('price')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', price, 'kind')


class RecipePartInline(admin.TabularInline):
    model = RecipePart


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipePartInline,
    ]
