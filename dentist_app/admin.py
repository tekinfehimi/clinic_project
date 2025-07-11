# from django.contrib import admin
# from dentist_app.models import *

# admin.site.register(DoctorType)
# admin.site.register(Doctor)
# admin.site.register(Service)
# # admin.site.register(Patient)
# # admin.site.register(Appointment)
# admin.site.register(DoctorEarnings)

from django.contrib import admin
from dentist_app.models import *

@admin.register(DoctorType)
class DoctorTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'fin_code', 'phone']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    autocomplete_fields = ['patient', 'doctor', 'service']
    list_display = ('patient', 'doctor', 'service', 'appointment_date', 'appointment_time', 'is_completed')

@admin.register(DoctorEarnings)
class DoctorEarningsAdmin(admin.ModelAdmin):
    pass
