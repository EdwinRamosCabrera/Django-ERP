from django.conf import settings
from django.db import models

class Material(models.Model):
    id_material = models.CharField(max_length=50, null=True, unique=True, verbose_name="Material ID")
    name = models.CharField(max_length=100, verbose_name="Name")
    description = models.TextField(max_length=250, blank=True, verbose_name="Description")
    unit = models.CharField(max_length=50, verbose_name="Unit measure")
    material_type = models.CharField(max_length=50, verbose_name="Material type")
    status = models.CharField(max_length=50, verbose_name="Status")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Created by", related_name="materials_created") # Usuario que este logueado y que creó el registro, se usa SET_NULL para no eliminar el material si el usuario es eliminado, y se completará automaticamente al crear el registro
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Updated by", related_name="materials_updated") # Usuario que este logueado y que actualizó el registro
    class Meta:
        db_table = 'materials'
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        ordering = ['name']

    def __str__(self):
        return self.name
