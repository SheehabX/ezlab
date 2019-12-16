from django.urls import path

from . import views

app_name = 'bacteria-classifier'
urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.index, name='results'),
    
]