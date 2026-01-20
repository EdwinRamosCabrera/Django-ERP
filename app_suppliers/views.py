from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db import models
from app_suppliers.forms import SupplierForm, CsvUploadForm
from app_users.models import UserRole
from app_suppliers.models import Supplier
from django.contrib import messages
import csv
import io
import re



@login_required
def suppliers_list(request):

    result = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__suppliers'))
    
    max_permission = result['max_permission'] or 0

    if max_permission == 0:
        return redirect('dashboard')  # Página de no permiso si el usuario no tiene acceso para ver materiales
   
    # Lógica para obtener la lista de provedores
    supplier_list = Supplier.objects.all()
    
    id_supplier = request.GET.get('id_supplier')
    name = request.GET.get('name')
    country = request.GET.get('country')
    status = request.GET.get('status')

    if id_supplier:
        supplier_list = supplier_list.filter(id_supplier__icontains=id_supplier)
    if name:
        supplier_list = supplier_list.filter(name__icontains=name)
    if country:
        supplier_list = supplier_list.filter(country__icontains=country)
    if status is not None and status != '':
        supplier_list = supplier_list.filter(status=status)

    # Exportar a CSV si se solicita
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="suppliers.csv"'
        response.write('\ufeff'.encode('utf8'))  # BOM para Excel

        writer = csv.writer(response)
        writer.writerow(['ID Supplier', 'Legal Name', 'Name', 'Tax ID', 'Country', 'State/Province', 'City', 'Address', 'Zip Code', 'Phone', 'Email', 'Contact name', ' Contact role', 'Category', 'Payment terms', 'Currency', 'Payment method', 'Bank Account', 'Status', 'Created By', 'Created At', 'Updated At'])
        for supplier in supplier_list:
            writer.writerow([
                supplier.id_supplier, 
                supplier.legal_name, 
                supplier.name, 
                supplier.tax_id, 
                supplier.country, 
                supplier.state_province, 
                supplier.city,
                supplier.address,
                supplier.zip_code,
                supplier.phone,
                supplier.email,
                supplier.contact_name,
                supplier.contact_role,
                supplier.category,
                supplier.payment_terms,
                supplier.currency,
                supplier.payment_method,
                supplier.bank_account,
                supplier.status, 
                supplier.created_by.username if supplier.created_by else 'N/A', 
                supplier.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
                supplier.updated_at.strftime('%Y-%m-%d %H:%M:%S')])
        return response

    paginator = Paginator(supplier_list, 10)  # 10 proveedores por página
    page_number = request.GET.get('page')
    pag_obj = paginator.get_page(page_number)

    return render(request, 'suppliers/supplier_list.html', {'pag_obj': pag_obj})


def supplier_create(request):
    max_permission = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__suppliers'))['max_permission'] or 0

    # Verificamos si el usuario tiene permiso para crear o modificar proveedores
    if max_permission == 1:
        return redirect('suppliers:suppliers_list')  
    if max_permission == 0:
        return redirect('dashboard')  # Página de no permiso si el usuario no tiene acceso para ver proveedores
    
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()
            return redirect('suppliers:suppliers_create') # Redirige al formulario vacío después de guardar
    else:
        form = SupplierForm()

    return render(request, 'suppliers/supplier_form.html', {'form': form})

@login_required
def supplier_edit(request, id):
    supplier = get_object_or_404(Supplier, pk=id)
    result = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__materials'))
    
    max_permission = result['max_permission'] or 0

    # Verificamos si el usuario tiene permiso para crear o modificar proveedores
    if max_permission == 1:
        return redirect('suppliers:suppliers_list') # Redirige a la lista de proveedores si el usuario solo tiene permiso de vista 
    if max_permission == 0:
        return redirect('dashboard')  # Página de no permiso si el usuario no tiene acceso para ver proveedores
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('suppliers:suppliers_list')
    else:
        form = SupplierForm(instance=supplier)
        context = {
            'form': form,
            'supplier': supplier,
        }

    return render(request, 'suppliers/supplier_form.html', context)

@login_required
def supplier_delete(request, id):
    result = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__suppliers'))
    max_permission = result['max_permission'] or 0

    # Verificamos si el usuario tiene permiso para crear o modificar proveedores
    if max_permission < 2:
        return redirect('suppliers:suppliers_list') # Redirige a la lista de proveedores si el usuario no tiene permiso para eliminar
    if max_permission == 0:
        return redirect('dashboard')  # Página de no permiso si el usuario no tiene acceso para ver proveedores
    
    supplier = Supplier.objects.get(pk=id)
    if request.method == 'POST':
        supplier.delete()
        return redirect('suppliers:suppliers_list')
    
    return redirect('suppliers:suppliers_list')


def supplier_bulk_create(request):
    max_permission = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__suppliers'))['max_permission'] or 0

    # Verificamos si el usuario tiene permiso para crear o modificar proveedores
    if max_permission < 2:
        return redirect('suppliers:suppliers_list')  
    
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
                    return render(request, 'suppliers/supplier_bulk_upload.html', {'form': form})
        
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
            suppliers_to_create = []

            
            for i, row in enumerate(reader):  # Iniciamos el bucle principal que lee cada fila como un diccionario
                row_number = i + 2 # Empezamos en 2 para contar la cabecera, asumimos que la fila 1 es el encabezado
                form_data = {}

                for key, value in row.items():
                    cleaned_value = value.strip() if isinstance(value, str) else value # Limpiamos los valores de espacios en blanco, usando strip()
                    form_data[key] = cleaned_value # Creamos un diccionario con los datos limpios

                form = SupplierForm(form_data) # Validamos a traves del formulario de Django
                    
                if form.is_valid():
                    supplier = form.save(commit=False) # Creamos el objeto pero no lo guardamos aun
                    supplier.created_by = request.user # Asignamos el usuario que crea el proveedor
                    print(supplier)
                    suppliers_to_create.append(supplier) # Agregamos el proveedor a la lista de proveedores a crear
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

            if suppliers_to_create: # Si hay proveedores para crear, los guardamos en la base de datos
                Supplier.objects.bulk_create(suppliers_to_create) # Usamos bulk_create para crear todos los proveedores de una vez en la base de datos
            messages.success(request, f'Process finished with {len(successful_records)} suppliers created successfully.')

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
            return render(request, 'suppliers/supplier_bulk_upload.html', context)
            # Si el formulario no es válido, retornamos al formulario con errores y sin ningun cambio realizado
        return render(request, 'suppliers/supplier_bulk_upload.html', {'form': form})
    
    else:
        form = CsvUploadForm()
        return render(request, 'suppliers/supplier_bulk_upload.html', {'form': form})
    
# Descarga de plantilla CSV para carga masiva de proveedores
def download_supplier_template(request):
    # Definimos los campos de encabezado que coinciden con los campos del modelo Supplier
    header_fields = ['id_supplier','legal_name', 'name', 'tax_id', 'country', 'state_province', 'city', 'address', 'zip_code', 'phone', 'email', 'contact_name', 'contact_role', 'category', 'payment_terms', 'currency', 'payment_method', 'bank_account', 'status']
    # Crear la respuesta HTTP con el tipo de contenido adecuado para CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="supplier_template.csv"'
    response.write('\ufeff'.encode('utf8'))  # BOM para Excel

    writer = csv.writer(response) # Crear el escritor CSV
    # Escribir la fila de encabezados que coinciden con los campos del modelo Supplier
    writer.writerow(header_fields)
    
    return response