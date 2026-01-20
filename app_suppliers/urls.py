from django.urls import path
from app_suppliers import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.suppliers_list, name='suppliers_list'),
    path('create/', views.supplier_create, name='supplier_create'),
    path('edit/<int:id>/', views.supplier_edit, name='supplier_edit'),
    path('delete/<int:id>/', views.supplier_delete, name='supplier_delete'),
    path('bulk-create/', views.supplier_bulk_create, name='supplier_bulk_create'),
    path('bulk/template/', views.download_supplier_template, name='download_supplier_template'),
]
