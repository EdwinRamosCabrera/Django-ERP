from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
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

    paginator = Paginator(materials_list, 10)  # 10 materiales por página
    page_number = request.GET.get('page')
    pag_obj = paginator.get_page(page_number)

    return render(request, 'materials/material_list.html', {'pag_obj': pag_obj})

def material_create(request):
    max_permission = UserRole.objects.filter(user_id=request.user).aggregate(max_permission=models.Max('role__materials'))['max_permission'] or 0

    if max_permission == 1:
        return redirect('materials')  
    if max_permission == 0:
        return redirect('dashboard')  # Página de no permiso si el usuario no tiene acceso para ver materiales
    
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.created_by = request.user
            material.save()
            return redirect('materials: material_create') # Redirige a la lista de materiales después de crear uno nuevo
        else:
            form = MaterialForm()

    return render(request, 'materials/material_form.html', {'form': form})