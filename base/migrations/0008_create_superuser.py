from django.db import migrations

def create_superuser(apps, schema_editor):
    from django.contrib.auth.models import User
    User.objects.create_superuser(
        username='jeaen',
        email='jpvpvalarezo@gmail.com',
        password='jp2583462'
    )

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_visitador_remove_visita_visitas_and_more'),  # Cambia esto si tienes migraciones previas
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]