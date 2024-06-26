import json
from django.shortcuts import render
from django.http import HttpResponse
from .models import Cliente, Visita, Visitador, Cluster
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Avg, Count, FloatField
from django.db.models.functions import Cast
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q

def locations(request):
    
    search_query = request.GET.get('search', None)
    clientes = Cliente.objects.all()
    clusters = Cluster.objects.all().select_related('cliente')
    productos = Cliente.objects.values_list('producto_principal', flat=True).distinct()

    clientes_list = list(clientes.values('nombre_cliente', 'latitud_domicilio', 'longitud_domicilio', 'latitud_trabajo', 'longitud_trabajo', 'producto_principal', 'profesion_cliente', 'tipo_vivienda_cliente', 'tipo_direccion_cliente'))
    clusters_list = list(clusters.values('cliente__nombre_cliente', 'cliente__latitud_domicilio', 'cliente__longitud_domicilio', 'cluster_direccion'))

    # Calcular los centroides de los clusters
    for cluster in clusters_list:
        if cluster['cliente__latitud_domicilio']:
            cluster['cliente__latitud_domicilio'] = float(cluster['cliente__latitud_domicilio'])
        if cluster['cliente__longitud_domicilio']:
            cluster['cliente__longitud_domicilio'] = float(cluster['cliente__longitud_domicilio'])

    # Calcular los centroides de los clusters
    centroids = clusters.annotate(
        latitud_float=Cast('cliente__latitud_domicilio', FloatField()),
        longitud_float=Cast('cliente__longitud_domicilio', FloatField())
    ).values('cluster_direccion').annotate(
        avg_latitud=Avg('latitud_float'),
        avg_longitud=Avg('longitud_float'),
        count_clients=Count('id')
    )
    centroids_list = list(centroids)

    context = {
        'clientes_json': json.dumps(clientes_list),
        'clusters_json': json.dumps(clusters_list),
        'centroids_json': json.dumps(centroids_list),
        'productos': productos,
        'search_query': search_query,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }

    return render(request, 'locations.html', context)

def clients(request):
    clientes_query = Cliente.objects.all()

    # Capturar los valores de los filtros desde el request
    search_query = request.GET.get('search', '')
    profesion_filter = request.GET.get('profesion', '')
    tipo_direccion_filter = request.GET.get('tipo_direccion', '')
    producto_principal_filter = request.GET.get('producto_principal', '')
    tipo_parroquia_filter = request.GET.get('tipo_parroquia', '')

    # Aplicar filtros
    if search_query:
        clientes_query = clientes_query.filter(
            Q(nombre_cliente__icontains=search_query) |
            Q(codigo_cliente__icontains=search_query) |
            Q(profesion_cliente__icontains=search_query) |
            Q(tipo_documento__icontains=search_query)
        )

    if profesion_filter:
        clientes_query = clientes_query.filter(profesion_cliente=profesion_filter)

    if tipo_direccion_filter:
        clientes_query = clientes_query.filter(tipo_direccion_cliente=tipo_direccion_filter)

    if producto_principal_filter:
        clientes_query = clientes_query.filter(producto_principal=producto_principal_filter)

    if tipo_parroquia_filter:
        clientes_query = clientes_query.filter(tipo_parroquia_residencia_trabajo_cliente=tipo_parroquia_filter)

    # Paginación de resultados después de aplicar filtros
    paginator = Paginator(clientes_query, 10)  # Muestra 10 clientes por página
    page_number = request.GET.get('page')
    clientes = paginator.get_page(page_number)

    profesiones = Cliente.objects.values_list('profesion_cliente', flat=True).exclude(profesion_cliente__exact='').distinct()
    tipos_direccion = Cliente.objects.values_list('tipo_direccion_cliente', flat=True).distinct()
    productos_principales = Cliente.objects.values_list('producto_principal', flat=True).distinct()
    tipos_parroquia = Cliente.objects.values_list('tipo_parroquia_residencia_trabajo_cliente', flat=True).exclude(tipo_parroquia_residencia_trabajo_cliente__exact='').distinct()

    context = {
        'clientes': clientes,
        'profesiones': profesiones,
        'tipos_direccion': tipos_direccion,
        'productos_principales': productos_principales,
        'tipos_parroquia': tipos_parroquia,
        'search_query': search_query,
        'profesion_filter': profesion_filter,
        'tipo_direccion_filter': tipo_direccion_filter,
        'producto_principal_filter': producto_principal_filter,
        'tipo_parroquia_filter': tipo_parroquia_filter,
    }

    return render(request, 'clients.html', context)

def routes(request):
    clientesDJ = Cliente.objects.all()
    clientes_list = list(clientesDJ.values('id', 'nombre_cliente', 'producto_principal', 'latitud_trabajo', 'longitud_trabajo', 'longitud_domicilio', 'latitud_domicilio', 'producto_principal', 'profesion_cliente', 'tipo_vivienda_cliente', 'tipo_direccion_cliente'))
    visitadores = Visitador.objects.all()
    context = {
        'clientesDJ': clientesDJ,
        'clientes': json.dumps(clientes_list),
        'visitadores': visitadores
    }
    return render(request, 'routes.html', context)

@csrf_exempt
def registrar_visita(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        visitador_id = request.POST.get('visitador_id')
        exitosa = request.POST.get('exitosa') == 'true'
        
        cliente = Cliente.objects.get(id=cliente_id)
        visitador = Visitador.objects.get(id=visitador_id)
        
        visita = Visita(cliente=cliente, visitador=visitador, exitosa=exitosa)
        visita.save()

        return JsonResponse({'status': 'success', 'message': 'Visita registrada correctamente.'})

    return JsonResponse({'status': 'fail', 'message': 'Método no permitido.'})


def visits(request):
    cliente_id = request.GET.get('cliente_id')
    cliente = Cliente.objects.get(id=cliente_id)
    visitas = Visita.objects.filter(cliente=cliente)

    context = {
        'cliente': cliente,
        'visitas': visitas
    }

    return render(request, 'visits.html', context)