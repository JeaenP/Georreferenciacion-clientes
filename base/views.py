import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import Cliente, Visita, Visitador, Cluster, Agencia, Cajero, ComercioAhorita
from django.db.models import Avg, Count, FloatField, Q
from django.db.models.functions import Cast
from django.conf import settings
from django.core.paginator import Paginator
from django.utils.timezone import now
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler


def locations(request):
    search_query = request.GET.get('search', None)
    clientes = Cliente.objects.all()
    clusters = Cluster.objects.all().select_related('cliente')
    productos = Cliente.objects.values_list('producto_principal', flat=True).distinct()

    clientes_list = list(clientes.values(
        'nombre_cliente', 'latitud_domicilio', 'longitud_domicilio', 
        'latitud_trabajo', 'longitud_trabajo', 'producto_principal', 
        'profesion_cliente', 'tipo_vivienda_cliente', 'tipo_direccion_cliente'
    ))
    clusters_list = list(clusters.values(
        'cliente__nombre_cliente', 'cliente__latitud_domicilio', 
        'cliente__longitud_domicilio', 'cluster_direccion'
    ))

    for cluster in clusters_list:
        if cluster['cliente__latitud_domicilio']:
            cluster['cliente__latitud_domicilio'] = float(cluster['cliente__latitud_domicilio'])
        if cluster['cliente__longitud_domicilio']:
            cluster['cliente__longitud_domicilio'] = float(cluster['cliente__longitud_domicilio'])

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

    search_query = request.GET.get('search', '')
    filters = {
        'profesion_cliente': request.GET.get('profesion', ''),
        'tipo_direccion_cliente': request.GET.get('tipo_direccion', ''),
        'producto_principal': request.GET.get('producto_principal', ''),
        'tipo_parroquia_residencia_trabajo_cliente': request.GET.get('tipo_parroquia', '')
    }

    if search_query:
        clientes_query = clientes_query.filter(
            Q(nombre_cliente__icontains=search_query) |
            Q(codigo_cliente__icontains=search_query) |
            Q(profesion_cliente__icontains=search_query) |
            Q(tipo_documento__icontains=search_query)
        )

    for key, value in filters.items():
        if value:
            clientes_query = clientes_query.filter(**{key: value})

    paginator = Paginator(clientes_query, 50)
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
        **filters
    }

    return render(request, 'clients.html', context)


def routes(request):
    clientesDJ = Cliente.objects.all()
    clientes_list = list(clientesDJ.values(
        'id', 'nombre_cliente', 'producto_principal', 'latitud_trabajo', 
        'longitud_trabajo', 'longitud_domicilio', 'latitud_domicilio', 
        'producto_principal', 'profesion_cliente', 'tipo_vivienda_cliente', 
        'tipo_direccion_cliente'
    ))
    visitadores = Visitador.objects.all()
    context = {
        'clientesDJ': clientesDJ,
        'clientes': json.dumps(clientes_list),
        'visitadores': visitadores
    }
    return render(request, 'routes.html', context)



def registrar_visita(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        visitador_id = request.POST.get('visitador_id')
        exitosa = request.POST.get('exitosa') == 'true'
        
        cliente = Cliente.objects.get(id=cliente_id)
        visitador = Visitador.objects.get(id=visitador_id)
        
        Visita.objects.create(cliente=cliente, visitador=visitador, exitosa=exitosa)

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


def statistics(request):
    mapbox_access_token = 'pk.eyJ1IjoiamVhZW4iLCJhIjoiY2x4d2d0aWE1MjM3ZzJrcTNtZ3F4cWswYyJ9.Z114ZAl2fwrL5oxgsrEGog'

    chart_type = request.GET.get('chart_type', 'heatmap')
    time_period_str = request.GET.get('time_period', '1')
    start_month_str = request.GET.get('start_month', str(now().month))

    try:
        time_period = int(time_period_str)
    except ValueError:
        time_period = 1 

    try:
        start_month = int(start_month_str)
    except ValueError:
        start_month = now().month 

    requires_time_filters = chart_type in ['visitas_efectivas', 'visitas_colaborador']

    if chart_type == 'heatmap':
        heatmap_data = Cliente.objects.filter(latitud_domicilio__isnull=False, longitud_domicilio__isnull=False).values('latitud_domicilio', 'longitud_domicilio')
        heatmap_data = [
            {
                'latitud_domicilio': float(cliente['latitud_domicilio']),
                'longitud_domicilio': float(cliente['longitud_domicilio']),
                'count': 1
            }
            for cliente in heatmap_data
            if cliente['latitud_domicilio'] and cliente['longitud_domicilio']
        ]
        fig = px.density_mapbox(
            heatmap_data,
            lat='latitud_domicilio',
            lon='longitud_domicilio',
            z='count',
            radius=10,
            center=dict(lat=-3.99512, lon=-79.20136),
            zoom=15,
            mapbox_style="streets"
        )
        fig.update_layout(
            mapbox_accesstoken=mapbox_access_token,
            height=700
        )
        
    elif chart_type == 'visitas_efectivas':
        today = now()
        start_date = today.replace(month=start_month, day=1)
        end_date = start_date + relativedelta(months=time_period) - relativedelta(days=1)
        visitas_mes = Visita.objects.filter(fecha_hora__gte=start_date, fecha_hora__lte=end_date)

        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        efectivas = [visitas_mes.filter(exitosa=True, fecha_hora__day=day.day, fecha_hora__month=day.month).count() for day in dates]
        no_efectivas = [visitas_mes.filter(exitosa=False, fecha_hora__day=day.day, fecha_hora__month=day.month).count() for day in dates]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=efectivas,
            mode='lines', name='Efectivas',
            line=dict(color='#5ccb5f')
        ))
        fig.add_trace(go.Scatter(
            x=dates,
            y=no_efectivas,
            mode='lines', name='No Efectivas',
            line=dict(color='#ef2947')
        ))
        fig.update_layout(title='Evolución de Visitas Efectivas y No Efectivas', xaxis_title='Fecha', yaxis_title='Número de Visitas', height=700)
    
    elif chart_type == 'visitas_colaborador':
        today = now()
        start_date = today.replace(month=start_month, day=1)
        end_date = start_date + relativedelta(months=time_period) - relativedelta(days=1)
        visitas_mes = Visita.objects.filter(fecha_hora__gte=start_date, fecha_hora__lte=end_date)

        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        colaboradores = Visitador.objects.all()

        colors = px.colors.sequential.Aggrnyl

        fig = go.Figure()
        for i, colaborador in enumerate(colaboradores):
            color = colors[i % len(colors)]
            visitas_colaborador = [visitas_mes.filter(visitador=colaborador, fecha_hora__day=day.day, fecha_hora__month=day.month).count() for day in dates]
            fig.add_trace(go.Scatter(
                x=dates,
                y=visitas_colaborador,
                mode='lines',
                name=colaborador.nombre,
                line=dict(color=color)
            ))

        fig.update_layout(title='Visitas por Colaborador', xaxis_title='Fecha', yaxis_title='Número de Visitas', height=700)
    elif chart_type == 'pie_producto':
        productos = Cliente.objects.values('producto_principal').annotate(count=Count('id'))
        fig = px.pie(productos, values='count', names='producto_principal', title='Distribución por Producto', height=700)
    elif chart_type == 'pie_sector':
        sectores = Cliente.objects.values('parroquia_residencia_trabajo_cliente').annotate(count=Count('id'))
        fig = px.pie(sectores, values='count', names='parroquia_residencia_trabajo_cliente', title='Distribución por Sector', height=700)
    elif chart_type == 'scatter_visitas_productos':
        productos_visitas = Visita.objects.values('cliente__producto_principal').annotate(count=Count('id'))
        productos = [p['cliente__producto_principal'] for p in productos_visitas]
        counts = [p['count'] for p in productos_visitas]
        fig = px.scatter(x=productos, y=counts, text=counts, title='Relación Visitas y Productos', height=700)
        fig.update_traces(mode='markers+text', textposition='top center')
    elif chart_type == 'bar_productos_clientes':
        productos_clientes = Cliente.objects.values('producto_principal').annotate(count=Count('id'))
        fig = px.bar(productos_clientes, x='producto_principal', y='count', title='Productos por Clientes', height=700)
    elif chart_type == 'bar_visitas_efectivas_productos':
        visitas = Visita.objects.all()
        productos_efectivas = visitas.filter(exitosa=True).values('cliente__producto_principal').annotate(count=Count('id'))
        productos_no_efectivas = visitas.filter(exitosa=False).values('cliente__producto_principal').annotate(count=Count('id'))

        productos = list(set([p['cliente__producto_principal'] for p in productos_efectivas] + [p['cliente__producto_principal'] for p in productos_no_efectivas]))
        efectivas_counts = [next((item['count'] for item in productos_efectivas if item['cliente__producto_principal'] == producto), 0) for producto in productos]
        no_efectivas_counts = [next((item['count'] for item in productos_no_efectivas if item['cliente__producto_principal'] == producto), 0) for producto in productos]

        fig = go.Figure(data=[
            go.Bar(name='Efectivas', x=productos, y=efectivas_counts, marker_color='#5ccb5f', text=efectivas_counts, textposition='outside'),
            go.Bar(name='No Efectivas', x=productos, y=no_efectivas_counts, marker_color='#ef2947', text=no_efectivas_counts, textposition='outside')
        ])
        fig.update_layout(barmode='group', title='Visitas Efectivas y No Efectivas por Producto', xaxis_title='Producto', yaxis_title='Número de Visitas', height=700)
    else:
        fig = None

    context = {
        'fig': fig.to_html(full_html=False) if fig else None,
        'chart_type': chart_type,
        'time_period': time_period,
        'start_month': start_month,
        'requires_time_filters': requires_time_filters
    }

    return render(request, 'statistics.html', context)


def pois(request):
    search_query = request.GET.get('search', None)

    agencias = Agencia.objects.all()
    comercios = ComercioAhorita.objects.all()
    cajeros = Cajero.objects.all()

    agencias_list = list(agencias.values('nombre', 'latitud', 'longitud', 'direccion'))
    comercios_list = list(comercios.values('nombre_comercio', 'latitud', 'longitud', 'direccion', 'tipo_negocio', 'tiene_branding'))
    cajeros_list = list(cajeros.values('nombre', 'latitud', 'longitud', 'direccion', 'codigo_cajero', 'agencia__nombre'))

    context = {
        'agencias_json': json.dumps(agencias_list),
        'comercios_json': json.dumps(comercios_list),
        'cajeros_json': json.dumps(cajeros_list),
        'search_query': search_query,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }

    return render(request, 'pois.html', context)


def actualizar_clusters(request):
    if request.method == 'POST':
        clientes = Cliente.objects.exclude(latitud_domicilio__isnull=True, longitud_domicilio__isnull=True).values('id', 'latitud_domicilio', 'longitud_domicilio')

        valid_clientes = []
        for cliente in clientes:
            try:
                lat = float(cliente['latitud_domicilio'])
                lng = float(cliente['longitud_domicilio'])
                valid_clientes.append({'id': cliente['id'], 'latitud_float': lat, 'longitud_float': lng})
            except ValueError:
                continue

        df = pd.DataFrame(valid_clientes)

        if df.empty:
            return JsonResponse({'status': 'fail', 'message': 'No valid clients found'})

        X = df[['latitud_float', 'longitud_float']].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        n_clusters = 20
        hierarchical_clustering = AgglomerativeClustering(n_clusters=n_clusters)
        cluster_labels = hierarchical_clustering.fit_predict(X_scaled)

        df['cluster_domicilio'] = cluster_labels

        for index, row in df.iterrows():
            Cluster.objects.update_or_create(
                cliente_id=row['id'],
                defaults={'cluster_direccion': row['cluster_domicilio']}
            )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})
