from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

fin_validator = RegexValidator(
    regex='^[A-Z0-9]{7}$',
    message='FİN kod yalnız böyük hərflər və rəqəmlərdən ibarət 7 simvol olmalıdır.'
)

PHONE_PREFIXES = (
    ('Aze1', '050'),
    ('Aze2', '051'),
    ('Aze3', '010'),
    ('Bak1', '055'),
    ('Bak2', '099'),
    ('Nar1', '070'),
    ('Nar2', '077'),
)

class DoctorType(models.Model):
    name = models.CharField(max_length=100) 

    def __str__(self):
        return self.name

class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    doctor_type = models.ForeignKey(DoctorType, on_delete=models.CASCADE)
    experience_years = models.IntegerField()
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Service(models.Model):
    name = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    detail = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.price} AZN"

class Patient(models.Model):
    fin_code = models.CharField(max_length=7, unique=True, validators=[fin_validator],primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_regex = RegexValidator(regex=r'^\d{7}$', message="Mobil nömrə 7 rəqəmli olmalıdır. Məs: 1234567")
    phone_prefix = models.CharField(max_length=5, choices=PHONE_PREFIXES, default='Aze1')
    phone_number = models.CharField(validators=[phone_regex], max_length=7, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment_date = models.DateField(default=timezone.now)
    appointment_time = models.TimeField(default=timezone.now)
    is_completed = models.BooleanField(default=False)
    paid_amount = models.FloatField(blank=True)
    paid_date = models.DateField(default=timezone.now)
    qaime = models.FileField(upload_to='pdf/', default="/pdf/qaime.pdf")

    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.appointment_date}"

class DoctorEarnings(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.doctor} - {self.date} - {self.total_earnings}"
