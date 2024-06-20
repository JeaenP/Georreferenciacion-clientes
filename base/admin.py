from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Cliente, Visita, Visitador, Cluster
# Register your models here.
class ClienteResource(resources.ModelResource):
    class Meta:
        model = Cliente
        import_id_fields = ['codigo_cliente']
class ClienteAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ClienteResource
admin.site.register(Cliente, ImportExportModelAdmin)
admin.site.register(Visita)
admin.site.register(Visitador)
admin.site.register(Cluster)