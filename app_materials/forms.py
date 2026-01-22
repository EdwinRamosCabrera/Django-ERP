from django import forms
from app_materials.models import Material

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['id_material','name', 'description', 'unit', 'material_type', 'status'] # Campos que se van a mostrar en el formulario

class CsvUploadForm(forms.Form):
    csv_file = forms.FileField( # FileField es un formulario para subir archivos
        label='Select a CSV file',
        help_text='The file must contain headers that match the model fields. Max. 42 megabytes'
    )