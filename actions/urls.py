from django.urls import include, path
from . import views


urlpatterns = [
    path('actions_list', views.actions_list, name='actions_list'),
    path('', views.index, name='index'),
]
