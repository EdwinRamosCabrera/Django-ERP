from django.shortcuts import get_object_or_404, redirect, render, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
from django.db import models
from app_users.models import UserRole
from app_materials.models import Material
from .forms import MaterialForm, CsvUploadForm
from django.contrib import messages
import io


@login_required
def materials_list(request):

    max_permission = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__materials'))['max_permission'] or 0

    if max_permission == 0:
        return redirect('dashboard')  # Página de no permiso si el usuario no tiene acceso para ver materiales
   
    # Lógica para obtener la lista de materiales
    materials_list = Material.objects.all()
    
    id_material = request.GET.get('id_material')
    name = request.GET.get('name')
    material_type = request.GET.get('material_type')
    status = request.GET.get('status')

    if id_material:
        materials_list = materials_list.filter(id_material__icontains=id_material)
    if name:
        materials_list = materials_list.filter(name__icontains=name)
    if material_type:
        materials_list = materials_list.filter(material_type__icontains=material_type)
    if status is not None and status != '':
        materials_list = materials_list.filter(status=status)

    # Exportar a CSV si se solicita
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="materials.csv"'
        response.write('\ufeff'.encode('utf8'))  # BOM para Excel

        writer = csv.writer(response)
        writer.writerow(['ID Material', 'Name', 'Description', 'Unit', 'Material Type', 'Status', 'Created By', 'Created At', 'Updated At'])

        for material in materials_list:
            writer.writerow([
                material.id_material, 
                material.name, 
                material.description, 
                material.unit, 
                material.material_type, 
                material.status, 
                material.created_by.username if material.created_by else 'N/A', 
                material.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
                material.updated_at.strftime('%Y-%m-%d %H:%M:%S')])
        return response

    paginator = Paginator(materials_list, 10)  # 10 materiales por página
    page_number = request.GET.get('page')
    pag_obj = paginator.get_page(page_number)

    return render(request, 'materials/material_list.html', {'pag_obj': pag_obj})

def material_create(request):
    max_permission = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__materials'))['max_permission'] or 0

    # Verificamos si el usuario tiene permiso para crear o modificar materiales
    if max_permission == 1:
        return redirect('materials:materials_list')  
    if max_permission == 0:
        return redirect('dashboard')  # Página de no permiso si el usuario no tiene acceso para ver materiales
    
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.created_by = request.user
            material.save()
            return redirect('materials:materials_create') # Redirige al formulario vacío después de guardar
    else:
        form = MaterialForm()

    return render(request, 'materials/material_form.html', {'form': form})

@login_required
def material_edit(request, id):
    material = get_object_or_404(Material, pk=id)
    max_permission = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__materials'))['max_permission'] or 0

    # Verificamos si el usuario tiene permiso para crear o modificar materiales
    if max_permission == 1:
        return redirect('materials:materials_list') # Redirige a la lista de materiales si el usuario solo tiene permiso de vista 
    if max_permission == 0:
        return redirect('dashboard')  # Página de no permiso si el usuario no tiene acceso para ver materiales

    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            return redirect('materials:materials_list')
    else:
        form = MaterialForm(instance=material)
        context = {
            'form': form,
            'material': material,
        }

    return render(request, 'materials/material_form.html', context)

@login_required
def material_delete(request, id):
    max_permission = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__materials'))['max_permission'] or 0

    # Verificamos si el usuario tiene permiso para crear o modificar materiales
    if max_permission < 2:
        return redirect('materials:materials_list') # Redirige a la lista de materiales si el usuario no tiene permiso para eliminar
    if max_permission == 0:
        return redirect('dashboard')  # Página de no permiso si el usuario no tiene acceso para ver materiales
    
    material = Material.objects.get(pk=id)
    if request.method == 'POST':
        material.delete()
        return redirect('materials:materials_list')
    
    return redirect('materials:materials_list')

def material_bulk_create(request):
    max_permission = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__materials'))['max_permission'] or 0

    # Verificamos si el usuario tiene permiso para crear o modificar materiales
    if max_permission < 2:
        return redirect('materials:materials_list')  
    
    if request.method == 'POST':
        form = CsvUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            csv_file = form.cleaned_data['csv_file']

            try:
                data_set = csv_file.read().decode('utf-8') # Decodificamos el archivo CSV a UTF-8
            except UnicodeDecodeError:
                try:
                    csv_file.seek(0)  # Reiniciamos el puntero del archivo
                    data_set = csv_file.read().decode('ISO-8859-1')  # Si no se puede con UTF-8 intentamos con otra codificación
                except Exception as e:
                    messages.error(request, 'Error decoding file. Please ensure it is a valid UTF-8 encoded CSV file.')
                    # Sino se puede decodificar mostramos un mensaje de error y retornamos al formulario
                    return render(request, 'materials/material_bulk_upload.html', {'form': form})
        
            # Mediante la libreria io leemos y cargamos en memoria el archivo CSV
            io_string = io.StringIO(data_set)
            reader = csv.DictReader(io_string)

            if reader.fieldnames:
                if reader.fieldnames[0].startswith('\ufeff'): # Eliminamos el caracter \ufeff que es invisble y nos da problemas en la cabecera
                    reader.fieldnames[0] = reader.fieldnames[0].lstrip('\ufeff')

                # Limpiamos los nombres de las columnas de espacios en blanco y convertimos a minusculas    
                cleaned_fieldnames = [key.strip().lower() for key in reader.fieldnames]
                reader.fieldnames = cleaned_fieldnames
            
            # Inicializamos listas para registrar los resultados del procesamiento
            successful_records = []
            error_records = []
            materials_to_create = []

            
            for i, row in enumerate(reader):  # Iniciamos el bucle principal que lee cada fila como un diccionario
                row_number = i + 2 # Empezamos en 2 para contar la cabecera, asumimos que la fila 1 es el encabezado
                form_data = {}

                for key, value in row.items():
                    cleaned_value = value.strip() if isinstance(value, str) else value # Limpiamos los valores de espacios en blanco, usando strip()
                    form_data[key] = cleaned_value # Creamos un diccionario con los datos limpios

                form = MaterialForm(form_data) # Validamos a traves del formulario de Django
                    
                if form.is_valid():
                    material = form.save(commit=False) # Creamos el objeto pero no lo guardamos aun
                    material.created_by = request.user # Asignamos el usuario que crea el material
                    print(material)
                    materials_to_create.append(material) # Agregamos el material a la lista de materiales a crear
                    successful_records.append({'row':row_number, 'data': form_data}) # Agregamos al registro de creados exitosamente
                else:
                    errors= {
                        field: ', '.join(err)
                        for field, err in form.errors.items()
                    }
                    error_records.append({ # Agregamos al registro de errores
                        'row': row_number,
                        'data': form_data,
                        'errors': errors
                    })

            if materials_to_create: # Si hay materiales para crear, los guardamos en la base de datos
                Material.objects.bulk_create(materials_to_create) # Usamos bulk_create para crear todos los materiales de una vez en la base de datos
            messages.success(request, f'Process finished with {len(successful_records)} materials created successfully.')

            # Creamos el contexto para enviar a la plantilla los resultados del procesamiento
            context = {
                'form': form,
                'successful_count': len(successful_records),
                'error_count': len(error_records),
                'total_rows': len(successful_records) + len(error_records),
                'successful_records': successful_records,
                'error_records': error_records,
                'report_generated': True
            }
                # Devolvemos el contexto en la misma plantilla de carga para mostrar los resultados
            return render(request, 'materials/material_bulk_upload.html', context)
            # Si el formulario no es válido, retornamos al formulario con errores y sin ningun cambio realizado
        return render(request, 'materials/material_bulk_upload.html', {'form': form})
    
    else:
        form = CsvUploadForm()
        return render(request, 'materials/material_bulk_upload.html', {'form': form})
    
# Descarga de plantilla CSV para carga masiva de proveedores
def download_material_template(request):
    # Definimos los campos de encabezado que coinciden con los campos del modelo Material
    header_fields = ['id_material','name', 'description', 'unit', 'material_type','status']
    # Crear la respuesta HTTP con el tipo de contenido adecuado para CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="material_template.csv"'
    response.write('\ufeff'.encode('utf8'))  # BOM para Excel

    writer = csv.writer(response) # Crear el escritor CSV
    # Escribir la fila de encabezados que coinciden con los campos del modelo Material
    writer.writerow(header_fields)
    
    return response