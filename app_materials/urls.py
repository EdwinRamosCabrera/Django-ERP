from django.urls import path
from .views import material_edit, materials_list, material_create, material_delete

app_name = 'materials'

urlpatterns = [
    path('', materials_list, name='materials_list'),
    path('create/', material_create, name='materials_create'),
    path('edit/<int:id>/', material_edit, name='material_edit'),
    path('delete/<int:id>/', material_delete, name='material_delete'),
]
