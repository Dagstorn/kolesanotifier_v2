from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('kolesafilters/', views.kolesafilters, name='kolesafilters'),
    path('updatelastcar/', views.updatelastcar, name='updatelastcar'),
    path('cars/<str:f_key>/', views.get_cars, name='get_cars'),
    path('addcar/<str:f_key>/', views.add_car, name='add_car'),

]
