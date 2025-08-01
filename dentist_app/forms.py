# forms.py
from django import forms
from dal import autocomplete
from .models import Appointment, Patient, Service, AppointmentSession
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'İstifadəçi adı', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Parol', 'class': 'form-control'})
    )
    
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'service', 'appointment_date', 'appointment_time', 'paid_amount']

        widgets = {
            'patient': autocomplete.ModelSelect2(url='patient-autocomplete'),
            'doctor': autocomplete.ModelSelect2(url='doctor-autocomplete'),
            'service': autocomplete.ModelSelect2(url='service-autocomplete'),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control bootstrap-timepicker', 'type': 'text'}),        

        }
        labels = {
            'patient': 'Pasiyent',
            'doctor': 'Həkim',
            'service': 'Xidmət',
            'appointment_date': 'Görüş Tarixi',
            'appointment_time': 'Görüş Vaxtı',
            'paid_amount': 'Ödənilən Məbləğ',
        }
        help_texts = {
            'paid_amount': 'Əgər ödəniş olunubsa, məbləği daxil edin.',
        }

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['fin_code', 'first_name', 'last_name', 'phone_prefix', 'phone_number']
        widgets = {
            'fin_code': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_prefix': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'fin_code': 'FIN kod',
            'first_name': 'Ad',
            'last_name': 'Soyad',
            'phone_prefix': 'Mobil nömrə',
            'phone_number': '',
        }
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'detail']
        widgets = {
            'detail': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'name': 'Xidmətin adı',
            'detail': 'Ətraflı',
            'price': 'Qiymət',

        }

class AppointmentSessionForm(forms.ModelForm):
    class Meta:
        model = AppointmentSession
        fields = ['session_date', 'session_time', 'notes']
        widgets = {
            'session_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'session_time': forms.TimeInput(attrs={'class': 'form-control timepicker-session', 'type': 'text'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
