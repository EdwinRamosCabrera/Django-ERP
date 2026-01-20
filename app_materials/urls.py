from django.urls import path
from .views import material_edit, materials_list, material_create, material_delete, material_bulk_create, download_material_template

app_name = 'materials'

urlpatterns = [
    path('', materials_list, name='materials_list'),
    path('create/', material_create, name='materials_create'),
    path('edit/<int:id>/', material_edit, name='material_edit'),
    path('delete/<int:id>/', material_delete, name='material_delete'),
    path('bulk-create/', material_bulk_create, name='material_bulk_create'),
    path('bulk/template/', download_material_template, name='download_material_template'),
]
