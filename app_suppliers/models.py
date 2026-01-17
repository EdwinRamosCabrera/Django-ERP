from django.conf import settings
from django.db import models

class Supplier(models.Model):
    id_supplier = models.CharField(max_length=50, unique=True, verbose_name="Supplier ID")
    legal_name = models.CharField(max_length=150, blank=True, verbose_name="Legal Name")
    name = models.CharField(max_length=150, verbose_name="Name")
    tax_id = models.CharField(max_length=30, verbose_name="Tax ID")
    country = models.CharField(max_length=60, verbose_name="Country")
    state_province = models.CharField(max_length=60, verbose_name="State/Province")
    city = models.CharField(max_length=100, verbose_name="City")
    address = models.CharField(max_length=150, verbose_name="Address")
    zip_code = models.IntegerField(verbose_name="ZIP Code")
    phone = models.IntegerField(verbose_name="Phone")
    email = models.EmailField(max_length=150, verbose_name="Email")
    contact_name = models.CharField(max_length=150, verbose_name="Contact Person")
    contact_role = models.CharField(max_length=150, verbose_name="Contact Role")
    category = models.CharField(max_length=150, verbose_name="Category")
    payment_terms = models.CharField(max_length=150, verbose_name="Payment Terms")
    currency = models.CharField(max_length=50, verbose_name="Currency")
    payment_method = models.CharField(max_length=100, verbose_name="Payment Method")
    bank_account = models.CharField(max_length=150, verbose_name="Bank Account")

    status = models.CharField(max_length=50, verbose_name="Status")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Created by", related_name="suppliers_created") # Usuario que este logueado y que creó el registro, se usa SET_NULL para no eliminar el proveedor si el usuario es eliminado, y se completará automaticamente al crear el registro
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Updated by", related_name="suppliers_updated") # Usuario que este logueado y que actualizó el registro
    class Meta:
        db_table = 'suppliers'
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['name']

    def __str__(self):
        return self.name
