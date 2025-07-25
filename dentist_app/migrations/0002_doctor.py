# Generated by Django 4.2.1 on 2025-06-21 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dentist_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('experience_years', models.IntegerField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='doctors/')),
                ('doctor_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dentist_app.doctortype')),
            ],
        ),
    ]
