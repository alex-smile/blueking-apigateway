# Generated by Django 3.2.18 on 2023-11-07 03:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_gateway__developers'),
    ]

    operations = [
        migrations.CreateModel(
            name='GatewayAppBinding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_time', models.DateTimeField(auto_now=True, null=True)),
                ('created_by', models.CharField(blank=True, max_length=32, null=True)),
                ('updated_by', models.CharField(blank=True, max_length=32, null=True)),
                ('bk_app_code', models.CharField(db_index=True, max_length=32)),
                ('gateway', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.gateway')),
            ],
            options={
                'db_table': 'core_gateway_app_binding',
                'unique_together': {('gateway', 'bk_app_code')},
            },
        ),
    ]
