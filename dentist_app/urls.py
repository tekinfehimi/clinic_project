from django.conf.urls import include
from django.urls import re_path as url
from django.shortcuts import redirect
from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from dentist_app.views import PatientAutocomplete, DoctorAutocomplete, ServiceAutocomplete

urlpatterns = [

    # url(r'^$', views.index, name='index'),
    path('', lambda request: redirect('login/')),
    url(r'^patients/$', views.patient_list, name='patient-list'),
    path('appointments/', views.appointment_list, name='appointment-list'),
    path('appointments/create/', views.create_appointment, name='appointment-create'),
    path('report/doctors/', views.doctor_report, name='doctor-report'),
    path('patients/add/', views.add_patient, name='add-patient'),
    path('services/', views.service_list, name='service-list'),
    path('services/add/', views.add_service, name='add-service'),
    path('queue/', views.queue_list, name='queue-list'),
    path('queue/complete/<int:appointment_id>/', views.complete_appointment, name='complete-appointment'),
    path('invoice/render/<int:appointment_id>/', views.generate_invoice_response, name='render_invoice'),

    # path('create-admin/', views.create_admin),

    # search in create appointment form
    path('patient-autocomplete/', PatientAutocomplete.as_view(), name='patient-autocomplete'),
    path('doctor-autocomplete/', DoctorAutocomplete.as_view(), name='doctor-autocomplete'),
    path('service-autocomplete/', ServiceAutocomplete.as_view(), name='service-autocomplete'),
]


urlpatterns += [
    
]
