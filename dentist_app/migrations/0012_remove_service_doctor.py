# Generated by Django 4.2.1 on 2025-07-10 04:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dentist_app', '0011_service_detail_alter_service_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='doctor',
        ),
    ]
