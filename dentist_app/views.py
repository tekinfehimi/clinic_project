from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import AppointmentForm, PatientForm, ServiceForm, AppointmentSessionForm
from django.utils import timezone
from dal import autocomplete
from django.db.models import Sum, Count, Q
from datetime import date
from collections import defaultdict, OrderedDict
from .utils import generate_invoice_pdf 
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404
from reportlab.pdfgen import canvas
from django.conf import settings
import io
import os
from .models import Appointment
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from django.db.models import Exists, OuterRef
from .utils import split_text_words

def generate_invoice_response(request, appointment_id):
    try:
        appointment = Appointment.objects.get(pk=appointment_id)
    except Appointment.DoesNotExist:
        raise Http404("Görüş tapılmadı")

    buffer = io.BytesIO()

    font_regular_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans.ttf')
    font_bold_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans-Bold.ttf')

    pdfmetrics.registerFont(TTFont('DejaVuSans', font_regular_path))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_bold_path))

    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    section_width = width / 3
    margin = 10 * mm
    text_max_width = section_width - 2 * margin - 20 * mm


    for i in range(3):
        left = i * section_width + margin
        top = height - 40 * mm
        

        logo_width = 70 * mm
        logo_height = 45 * mm
        logo_x = left + (section_width - logo_width) / 2 - 30
        logo_y = top -5 * mm
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
        c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')


        # c.setFont('DejaVuSans-Bold', 28)
        # c.drawString(left, top + 5 * mm, "MedXDent")
        top = logo_y + 10*mm
        label_x = left
        value_x = left + 30 * mm

        c.setFont('DejaVuSans-Bold', 16)
        c.drawString(label_x, top - 30 * mm, "Pasiyent:")
        c.drawString(label_x, top - 45 * mm, "Xidmət:")

        c.setFont('DejaVuSans', 16)
        c.drawString(value_x, top - 30 * mm, str(appointment.patient))

        # Xidmət çox sətrə düşəndə
        service_lines = split_text_words(appointment.service.name, text_max_width, 'DejaVuSans', 14)
        y_pos = top - 45 * mm
        line_height = 20
        for idx, line in enumerate(service_lines):
            c.drawString(value_x , y_pos - idx * line_height, line )

        service_block_height = len(service_lines) * line_height
        patient_y = y_pos - service_block_height - 25
        date_y = patient_y - 30
        amount_y = date_y - 30

        c.setFont('DejaVuSans-Bold', 16)
        c.drawString(label_x, patient_y, "Həkim:")
        c.drawString(label_x, date_y, "Tarix:")
        c.drawString(label_x, amount_y, "Məbləğ:")

        c.setFont('DejaVuSans', 16)
        c.drawString(value_x, patient_y, str(appointment.doctor))

        date_str = appointment.appointment_date.strftime('%d.%m.%Y')
        time_str = appointment.appointment_time.strftime('%H:%M') if hasattr(appointment, 'appointment_time') and appointment.appointment_time else ''
        datetime_str = f"{date_str} {time_str}".strip()
        c.drawString(value_x, date_y, datetime_str)

        c.drawString(value_x, amount_y, f"{appointment.paid_amount} AZN")

        c.setFont('DejaVuSans-Bold', 16)
        c.drawString(left, 35 * mm, "İmza:")

        if i < 2:
            x_cut = (i + 1) * section_width
            c.setLineWidth(1)
            c.line(x_cut, 15 * mm, x_cut, height - 15)

    c.showPage()
    c.save()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/pdf')


# from django.contrib.auth.models import User
# from django.http import HttpResponse

# def create_admin(request):
#     if not User.objects.filter(username='admin').exists():
#         User.objects.create_superuser('admin', 'admin@example.com', 'admin1234')
#         return HttpResponse("Admin yaradıldı")
#     return HttpResponse("Artıq mövcuddur")


class CustomLoginView(auth_views.LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'login.html'
    success_url = reverse_lazy('service-list')


@login_required
def index(request):
    return render(request, "base.html")

@login_required
def patient_list(request):
    patients = Patient.objects.all()
    context = {
        'patients': patients
    }
    return render(request, "patients.html", context=context)


# def appointment_list(request):
#     appointments = Appointment.objects.select_related('patient', 'doctor', 'service').order_by('-appointment_date', '-appointment_time')
#     return render(request, 'appointments.html', {'appointments': appointments})

@login_required
def appointment_list(request):
    appointments = Appointment.objects.prefetch_related('sessions').select_related('patient', 'doctor', 'service')
    return render(request, 'appointments.html', {'appointments': appointments})


@login_required
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            if not appointment.paid_amount:
                appointment.paid_amount = 0.0
            appointment.save()

            AppointmentSession.objects.create(
                appointment=appointment,
                session_date=appointment.appointment_date,
                session_time=appointment.appointment_time
            )

            return redirect('appointment-list')
    else:
        form = AppointmentForm()
    return render(request, 'create_appointment.html', {'form': form})

@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            appointment.sessions.filter(is_active=True).update(is_active=False)
            AppointmentSession.objects.create(
                appointment=appointment,
                session_date=appointment.appointment_date,
                session_time=appointment.appointment_time,
                is_active=True
            )

            return redirect('appointment-list')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'create_appointment.html', {
        'form': form,
        'appointment': appointment
    })



def edit_appoint_in_queue(request, app_id):
    appointment = get_object_or_404(Appointment, id=app_id)
    session = get_object_or_404(AppointmentSession, pk=appointment.id)
    if request.method == 'POST':
        form = AppointmentSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            return redirect('queue-list')
    else:
        form = AppointmentSessionForm(instance=session)

    return render(request, 'edit_session.html', {'form': form, 'session': session})
    




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
@login_required
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

@login_required
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

@login_required
def service_list(request):
    services = Service.objects.all().order_by('-id')
    return render(request, 'services.html', {'services': services})

@login_required
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service-list')  
    else:
        form = ServiceForm()
    return render(request, 'add_service.html', {'form': form, 'title': 'Yeni Xidmət Əlavə Et'})

@login_required
@login_required
def queue_list(request):
    today = timezone.localdate()
    sessions = AppointmentSession.objects.filter(
        is_completed=False,
        is_active=True,
        session_date__gte=today
    ).select_related('appointment__patient', 'appointment__doctor', 'appointment__service') \
     .order_by('session_date', 'session_time')

    grouped_queue = defaultdict(list)
    for session in sessions:
        appointment = session.appointment
        grouped_queue[session.session_date].append({
            'id': session.id,
            'patient': appointment.patient,
            'doctor': appointment.doctor,
            'service': appointment.service,
            'time': session.session_time,
            'type': 'session'
        })

    grouped_queue = dict(sorted(grouped_queue.items()))

    return render(request, 'queue_list.html', {'grouped_queue': grouped_queue})


# @login_required
# def complete_appointment(request, appointment_id):
#     appointment = get_object_or_404(Appointment, id=appointment_id)
#     if request.method == 'POST':
#         action = request.POST.get('action')
#         if action == 'complete':
#             appointment.is_completed = True
#             appointment.save()
#     return redirect('queue-list')

    #     elif action == 'continue':
    #         return redirect('add-session', appointment_id=appointment.id)

    # return render(request, 'confirm_complete.html', {'appointment': appointment})

@login_required
def add_session(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.appointment = appointment
            session.save()
            return redirect('queue-list') 
    else:
        form = AppointmentSessionForm()

    return render(request, 'add_session.html', {'form': form, 'appointment': appointment})

@login_required
def complete_session(request, pk):
    session = get_object_or_404(AppointmentSession, pk=pk)
    if request.method == 'POST':
        session.is_completed = True 
        session.is_active = False
        session.save()

        appointment = session.appointment
        appointment.is_completed = True
        appointment.save()
    return redirect('queue-list')

@login_required
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.is_completed = True
    appointment.save()
    return redirect('queue-list')

@login_required
def edit_session(request, pk):
    old_session = get_object_or_404(AppointmentSession, pk=pk)

    if request.method == 'POST':
        form = AppointmentSessionForm(request.POST)
        if form.is_valid():
            # Köhnə session-u deaktiv edirik
            old_session.is_active = False
            old_session.save()

            # Yeni session yarat
            new_session = form.save(commit=False)
            new_session.appointment = old_session.appointment  # əlaqəni saxla
            new_session.is_active = True
            new_session.save()

            return redirect('queue-list')
    else:
        # Formu əvvəlki session məlumatları ilə doldur (instance istifadə etmə!)
        form = AppointmentSessionForm(initial={
            'session_date': old_session.session_date,
            'session_time': old_session.session_time,
            'notes': old_session.notes,
            'is_completed': old_session.is_completed,
        })

    return render(request, 'edit_session.html', {
        'form': form,
        'session': old_session,
    })
