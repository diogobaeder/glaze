from django.conf.urls import url

from recipes import views


urlpatterns = [
    url(r'^ingredients/(?P<pk>[0-9]+)/$',
        views.IngredientDetail.as_view(), name='ingredient-detail'),
    url(r'ingredient/add/$',
        views.IngredientCreate.as_view(), name='ingredient-add'),
    url(r'ingredient/(?P<pk>[0-9]+)/$',
        views.IngredientUpdate.as_view(), name='ingredient-update'),
    url(r'ingredient/(?P<pk>[0-9]+)/delete/$',
        views.IngredientDelete.as_view(), name='ingredient-delete'),
    url(r'^ingredients/$', views.IngredientList.as_view(), name='ingredients'),

    url(r'^recipes/$', views.recipes),
]
