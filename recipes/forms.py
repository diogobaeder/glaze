from django.core.exceptions import ObjectDoesNotExist
from django.forms import (
    ModelForm,
    ValidationError,
    inlineformset_factory,
)

from glaze.forms import LocalizeFieldsMixin
from recipes.models import Ingredient, Recipe, RecipePart


class UserBoundForm(ModelForm, LocalizeFieldsMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.localize_fields()

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            duplicate_instance = self.Meta.model.objects.get(
                name=name, user=self.instance.user)
        except ObjectDoesNotExist:
            return name
        if duplicate_instance.pk != self.instance.pk:
            raise ValidationError('Name already exists for this user')

        return name


class IngredientForm(UserBoundForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'kind', 'weight_unit', 'price']
        localized_fields = '__all__'


class RecipeForm(UserBoundForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'image']
        localized_fields = '__all__'


class RecipePartForm(ModelForm, LocalizeFieldsMixin):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].queryset = Ingredient.objects.for_user(user)
        self.localize_fields()

    class Meta:
        model = RecipePart
        fields = ['ingredient', 'percentage']
        localized_fields = '__all__'


RecipePartFormset = inlineformset_factory(
    Recipe, RecipePart, RecipePartForm, extra=5, localized_fields='__all__')
