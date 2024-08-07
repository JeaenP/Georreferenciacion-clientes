from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Cliente, Visita, Visitador, Cluster, Agencia, ComercioAhorita, Cajero
# Register your models here.
class ClienteResource(resources.ModelResource):
    class Meta:
        model = Cliente
        import_id_fields = ['codigo_cliente']
class ClienteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ClienteResource

class ClusterResource(resources.ModelResource):
    class Meta:
        model = Cluster
        import_id_fields = ['cliente']

class ClusterAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ClusterResource

admin.site.register(Cliente, ImportExportModelAdmin)
admin.site.register(Visita)
admin.site.register(Visitador)
admin.site.register(Cluster, ImportExportModelAdmin)
admin.site.register(Agencia)
admin.site.register(ComercioAhorita)
admin.site.register(Cajero)