from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Equipment(models.Model):
    CONDITION = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('damaged', 'Damaged')]
    STATUS = [('available', 'Available'), ('maintenance', 'Under maintenance'), ('retired', 'Retired')]
    name = models.CharField(max_length=120)
    asset_tag = models.CharField(max_length=40, unique=True)
    category = models.CharField(max_length=80)
    laboratory = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    condition = models.CharField(max_length=12, choices=CONDITION, default='good')
    status = models.CharField(max_length=15, choices=STATUS, default='available')
    purchase_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f'{self.name} ({self.asset_tag})'

    @property
    def is_bookable(self): return self.status == 'available' and self.condition != 'damaged'


class Booking(models.Model):
    STATUS = [('pending', 'Pending'), ('approved', 'Approved'), ('returned', 'Returned'), ('cancelled', 'Cancelled')]
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    purpose = models.CharField(max_length=240)
    status = models.CharField(max_length=12, choices=STATUS, default='pending')
    returned_at = models.DateTimeField(null=True, blank=True)
    return_condition = models.CharField(max_length=12, choices=Equipment.CONDITION, blank=True)
    return_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValidationError('End time must be after the start time.')
        if self.equipment_id and self.start_at and self.end_at:
            overlap = Booking.objects.filter(equipment=self.equipment, status__in=['pending', 'approved'], start_at__lt=self.end_at, end_at__gt=self.start_at)
            if self.pk: overlap = overlap.exclude(pk=self.pk)
            if overlap.exists(): raise ValidationError('This equipment is already booked for part of that period.')

    def __str__(self): return f'{self.equipment} — {self.user.username}'


class FaultReport(models.Model):
    PRIORITY = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')]
    STATUS = [('open', 'Open'), ('in_progress', 'In progress'), ('resolved', 'Resolved')]
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name='faults')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY, default='medium')
    status = models.CharField(max_length=15, choices=STATUS, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title


class MaintenanceRecord(models.Model):
    TYPE = [('preventive', 'Preventive'), ('corrective', 'Corrective'), ('inspection', 'Inspection')]
    STATUS = [('scheduled', 'Scheduled'), ('completed', 'Completed')]
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name='maintenance')
    fault = models.ForeignKey(FaultReport, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_records')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    maintenance_type = models.CharField(max_length=15, choices=TYPE)
    scheduled_for = models.DateField()
    completed_on = models.DateField(null=True, blank=True)
    notes = models.TextField()
    cost = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS, default='scheduled')

    def __str__(self): return f'{self.equipment}: {self.maintenance_type}'

# Create your models here.
