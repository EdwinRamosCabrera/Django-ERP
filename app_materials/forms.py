from django import forms
from app_materials.models import Material

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['id_material','name', 'description', 'unit', 'material_type','status']