from django.conf import settings
from django.db import models
from app_core.models import Status

class UnitMeasure(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Unit Name")
    symbol = models.CharField(max_length=10, verbose_name="Symbol")

    class Meta:
        db_table = 'unit_measures'
        verbose_name = 'Unit Measure'
        verbose_name_plural = 'Unit Measures'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
class MaterialType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Material Type Name")
    symbol = models.CharField(max_length=250, blank=True, verbose_name="Symbol")

    class Meta:
        db_table = 'material_types'
        verbose_name = 'Material Type'
        verbose_name_plural = 'Material Types'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
class Material(models.Model):
    id_material = models.CharField(max_length=50, null=True, unique=True, verbose_name="Material ID")
    name = models.CharField(max_length=100, verbose_name="Name")
    description = models.TextField(max_length=250, blank=True, verbose_name="Description")
    unit = models.ForeignKey(UnitMeasure, default=1, on_delete=models.PROTECT, verbose_name="Unit Measure")
    material_type = models.ForeignKey(MaterialType, default=1, on_delete=models.PROTECT, verbose_name="Material Type")
    status = models.ForeignKey(Status, default=1, on_delete=models.PROTECT, verbose_name="Status")

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
    

