from django.contrib import admin

from app_materials.models import Material, UnitMeasure, MaterialType

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_material', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('name', 'id_material')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

@admin.register(UnitMeasure)
class UnitMeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    search_fields = ('name', 'symbol')

@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    search_fields = ('name', 'symbol')
