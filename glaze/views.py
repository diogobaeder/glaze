from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from glaze.forms import ProfileForm


def home(request):
    return render(request, 'home.html')


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'glaze/profile.html'


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    template_name = 'glaze/profile_form.html'
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user.profile
