from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db import models
from app_suppliers.forms import SupplierForm
from app_users.models import UserRole
from app_suppliers.models import Supplier
import csv


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