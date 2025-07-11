from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import AppointmentForm, PatientForm, ServiceForm
from django.utils import timezone
from dal import autocomplete
from django.db.models import Sum, Count, Q
from datetime import date
from .utils import generate_invoice_pdf 
from .models import *

# from django.contrib.auth.models import User
# from django.http import HttpResponse

# def create_admin(request):
#     if not User.objects.filter(username='admin').exists():
#         User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
#         return HttpResponse("Admin yaradıldı")
#     return HttpResponse("Artıq mövcuddur")

# Create your views here.
def index(request):
    return render(request, "base.html")

def patient_list(request):
    patients = Patient.objects.all()
    context = {
        'patients': patients
    }
    return render(request, "patients.html", context=context)

def appointment_list(request):
    appointments = Appointment.objects.select_related('patient', 'doctor', 'service').order_by('-appointment_date', '-appointment_time')
    return render(request, 'appointments.html', {'appointments': appointments})

def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            if appointment.paid_amount:
                # if appointment.paid_amount >= appointment.service.price:
                #     appointment.is_completed = True
                appointment.paid_date = timezone.now()
                pdf_path = generate_invoice_pdf(appointment)
                appointment.qaime.name = pdf_path
            appointment.save()
            return redirect('appointment-list')
    else:
        form = AppointmentForm()
    return render(request, 'create_appointment.html', {'form': form})

# Yeni görüş yadılma formunda xəstə, həkim, xidmət axtarışı üçün
class PatientAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Patient.objects.all()
        if self.q:
            qs = qs.filter(
                first_name__icontains=self.q
            ) | qs.filter(
                last_name__icontains=self.q
            ) | qs.filter(
                fin_code__icontains=self.q
            )
        return qs

class DoctorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Doctor.objects.all()
        if self.q:
            qs = qs.filter(full_name__icontains=self.q)
        return qs

class ServiceAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Service.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
# axtarışın sonu

def doctor_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        today = date.today()
        start_date = date(today.year, today.month, 1).isoformat()
        end_date = today.isoformat()

    appointments = Appointment.objects.filter(
        appointment_date__range=[start_date, end_date]
    ).select_related('doctor', 'service', 'patient')

    doctor_data = []
    for doctor in Doctor.objects.all():
        doc_appointments = appointments.filter(doctor=doctor)

        patient_count = doc_appointments.values('patient').distinct().count()
        total_income = doc_appointments.aggregate(total=Sum('paid_amount'))['total'] or 0


        doctor_data.append({
            'doctor': doctor,
            'patient_count': patient_count,
            'income': total_income,
            'appointments': doc_appointments.order_by('-appointment_date', '-appointment_time')
        })

    return render(request, 'doctor_report.html', {
        'doctor_data': doctor_data,
        'start_date': start_date,
        'end_date': end_date,
    })

def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            # messages.success(request, 'Pasiyent uğurla əlavə olundu!')
            return redirect('appointment-create')  
    else:
        form = PatientForm()
    
    return render(request, 'add_patient.html', {'form': form})

def service_list(request):
    services = Service.objects.all().order_by('-id')
    return render(request, 'services.html', {'services': services})

def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service-list')  
    else:
        form = ServiceForm()
    return render(request, 'add_service.html', {'form': form, 'title': 'Yeni Xidmət Əlavə Et'})

def queue_list(request):
    today = timezone.localdate()  # bu günün tarixi
    queue = Appointment.objects.filter(
        appointment_date=today,
        is_completed=False
    ).order_by('appointment_time')

    return render(request, 'queue_list.html', {'queue': queue})

def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.is_completed = True
    appointment.save()
    return redirect('queue-list')