from django.apps import AppConfig
from django.utils.translation import ugettext as _


class RecipesConfig(AppConfig):
    name = 'recipes'
    verbose_name = _('Recipes')
