from django.urls import path
from .views import materials_list, material_create

app_name = 'materials'

urlpatterns = [
    path('', materials_list, name='materials_list'),
    path('create/', material_create, name='materials_create'),
]
