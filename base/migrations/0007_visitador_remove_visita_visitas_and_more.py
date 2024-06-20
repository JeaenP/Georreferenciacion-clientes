# Generated by Django 5.0.6 on 2024-06-20 04:41

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_cluster'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visitador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=10, unique=True)),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='visita',
            name='visitas',
        ),
        migrations.RemoveField(
            model_name='visita',
            name='visitasExitosas',
        ),
        migrations.RemoveField(
            model_name='visita',
            name='visitasNoExitosas',
        ),
        migrations.AddField(
            model_name='visita',
            name='exitosa',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='visita',
            name='fecha_hora',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='visita',
            name='visitador',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='base.visitador'),
        ),
    ]