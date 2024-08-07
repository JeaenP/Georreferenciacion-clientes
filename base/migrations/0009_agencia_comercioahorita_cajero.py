# Generated by Django 5.0.6 on 2024-07-03 23:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_create_superuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=255, unique=True)),
                ('nombre', models.CharField(max_length=255)),
                ('direccion', models.CharField(max_length=255)),
                ('latitud', models.CharField(blank=True, max_length=255, null=True)),
                ('longitud', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ComercioAhorita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_comercio', models.CharField(max_length=255)),
                ('tipo_negocio', models.CharField(max_length=255)),
                ('direccion', models.CharField(max_length=255)),
                ('latitud', models.CharField(blank=True, max_length=255, null=True)),
                ('longitud', models.CharField(blank=True, max_length=255, null=True)),
                ('tiene_branding', models.BooleanField(choices=[(True, 'Sí'), (False, 'No')])),
            ],
        ),
        migrations.CreateModel(
            name='Cajero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_cajero', models.CharField(max_length=255, unique=True)),
                ('nombre', models.CharField(max_length=255)),
                ('direccion', models.CharField(max_length=255)),
                ('latitud', models.CharField(blank=True, max_length=255, null=True)),
                ('longitud', models.CharField(blank=True, max_length=255, null=True)),
                ('agencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.agencia')),
            ],
        ),
    ]
