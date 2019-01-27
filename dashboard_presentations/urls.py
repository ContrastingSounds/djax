from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_dashboard_presentation', views.generate_dashboard_presentation, name='generate_dashboard_presentation'),
    path('action_form', views.action_form, name='action_form'),
]