# Generated by Django 5.0.6 on 2024-05-30 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_cliente_referencia_residencia_trabajo_cliente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='latitud_domicilio',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='longitud_domicilio',
            field=models.CharField(blank=True, null=True),
        ),
    ]
