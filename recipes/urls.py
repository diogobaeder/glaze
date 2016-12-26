from django.conf.urls import url

from recipes import views


urlpatterns = [
    url(r'^ingredients/$', views.ingredients),
    url(r'^recipes/$', views.recipes),
]
