from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Equipment, FaultReport, MaintenanceRecord

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ('name', 'asset_tag', 'category', 'laboratory', 'description', 'condition', 'status', 'purchase_date')
        widgets = {'purchase_date': forms.DateInput(attrs={'type': 'date'})}

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('start_at', 'end_at', 'purpose')
        widgets = {'start_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 'end_at': forms.DateTimeInput(attrs={'type': 'datetime-local'})}

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('return_condition', 'return_notes')

class FaultForm(forms.ModelForm):
    class Meta:
        model = FaultReport
        fields = ('title', 'description', 'priority')

class FaultStatusForm(forms.ModelForm):
    class Meta:
        model = FaultReport
        fields = ('status',)

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ('equipment', 'fault', 'maintenance_type', 'scheduled_for', 'completed_on', 'notes', 'cost', 'status')
        widgets = {'scheduled_for': forms.DateInput(attrs={'type': 'date'}), 'completed_on': forms.DateInput(attrs={'type': 'date'})}
