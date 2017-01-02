from django.forms import ModelForm

from glaze.models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['currency']
