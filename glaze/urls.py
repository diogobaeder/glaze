"""glaze URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import re

import debug_toolbar
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve

from . import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^recipes/', include('recipes.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^accounts/profile/update/$',
        views.ProfileUpdateView.as_view(), name='profile-update'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^$', views.home),
]
if settings.DEBUG or settings.TESTING:
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')),
            serve, kwargs={
                'document_root': settings.MEDIA_ROOT,
            })
    ]
