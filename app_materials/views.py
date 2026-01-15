from django.shortcuts import get_object_or_404, redirect, render, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv
from django.db import models
from app_users.models import UserRole
from app_materials.models import Material
from .forms import MaterialForm

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