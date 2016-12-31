from django.conf.urls import url

from recipes import views


urlpatterns = [
    url(r'^ingredients/$', views.IngredientList.as_view(), name='ingredients'),
    url(r'^ingredients/(?P<pk>[0-9]+)/$',
        views.IngredientDetail.as_view(), name='ingredient-detail'),
    url(r'ingredient/add/$',
        views.IngredientCreate.as_view(), name='ingredient-add'),
    url(r'ingredient/(?P<pk>[0-9]+)/$',
        views.IngredientUpdate.as_view(), name='ingredient-update'),
    url(r'ingredient/(?P<pk>[0-9]+)/delete/$',
        views.IngredientDelete.as_view(), name='ingredient-delete'),

    url(r'^recipes/$', views.RecipeList.as_view(), name='recipes'),
    url(r'^recipes/(?P<pk>[0-9]+)/$',
        views.RecipeDetail.as_view(), name='recipe-detail'),
    url(r'recipe/add/$',
        views.RecipeCreate.as_view(), name='recipe-add'),
    url(r'recipe/(?P<pk>[0-9]+)/$',
        views.RecipeUpdate.as_view(), name='recipe-update'),
    url(r'recipe/(?P<pk>[0-9]+)/delete/$',
        views.RecipeDelete.as_view(), name='recipe-delete'),
]
