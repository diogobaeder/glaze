from django.forms import ModelForm
from django.utils.translation import ugettext as _

from glaze.models import Profile


class LocalizeFieldsMixin:
    def localize_fields(self):
        for field in self.fields.values():
            field.label = _(field.label)


class ProfileForm(ModelForm, LocalizeFieldsMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.localize_fields()

    class Meta:
        model = Profile
        fields = ['currency']
        localized_fields = '__all__'
