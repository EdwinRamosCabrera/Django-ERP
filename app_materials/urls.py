from django.urls import path
from app_materials import views

urlpatterns = [
    path('', views.materials_list, name='material-list'),
    path('create/', views.material_create, name='material-create'),
]
