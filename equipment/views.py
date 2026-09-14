from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import BookingForm, EquipmentForm, FaultForm, FaultStatusForm, MaintenanceForm, RegisterForm, ReturnForm
from .models import Booking, Equipment, FaultReport, MaintenanceRecord

staff_required = user_passes_test(lambda u: u.is_staff)

def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user()); return redirect('dashboard')
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request): logout(request); return redirect('login')

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(); login(request, user); messages.success(request, 'Welcome to EquipCare.'); return redirect('dashboard')
    return render(request, 'equipment/form.html', {'form': form, 'title': 'Create account'})

@login_required
def dashboard(request):
    now = timezone.now()
    return render(request, 'equipment/dashboard.html', {
        'equipment_count': Equipment.objects.count(), 'available_count': Equipment.objects.filter(status='available').exclude(condition='damaged').count(),
        'open_faults': FaultReport.objects.exclude(status='resolved').count(),
        'upcoming': Booking.objects.filter(user=request.user, status__in=['pending','approved'], end_at__gte=now).order_by('start_at')[:5],
        'maintenance_due': MaintenanceRecord.objects.filter(status='scheduled').order_by('scheduled_for')[:5],
    })

@login_required
def equipment_list(request):
    items = Equipment.objects.all().order_by('name')
    query = request.GET.get('q', '')
    lab = request.GET.get('lab', '')
    if query: items = items.filter(name__icontains=query) | items.filter(asset_tag__icontains=query) | items.filter(category__icontains=query)
    if lab: items = items.filter(laboratory=lab)
    return render(request, 'equipment/equipment_list.html', {'items': items, 'query': query, 'labs': Equipment.objects.values_list('laboratory', flat=True).distinct(), 'lab': lab})

@login_required
def equipment_detail(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    return render(request, 'equipment/equipment_detail.html', {'item': item, 'upcoming': item.bookings.filter(status__in=['pending','approved'], end_at__gte=timezone.now()).order_by('start_at')})

@login_required
@staff_required
def equipment_create(request): return save_form(request, EquipmentForm, 'Add equipment')

@login_required
@staff_required
def equipment_edit(request, pk): return save_form(request, EquipmentForm, 'Edit equipment', get_object_or_404(Equipment, pk=pk))

def save_form(request, form_class, title, instance=None):
    form = form_class(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid(): form.save(); messages.success(request, f'{title} saved.'); return redirect('equipment_list')
    return render(request, 'equipment/form.html', {'form': form, 'title': title})

@login_required
def booking_create(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if not item.is_bookable: messages.error(request, 'This equipment is not currently bookable.'); return redirect('equipment_detail', pk=pk)
    form = BookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        booking = form.save(commit=False); booking.equipment = item; booking.user = request.user
        try: booking.full_clean(); booking.save(); messages.success(request, 'Booking request submitted.'); return redirect('booking_list')
        except Exception as error: form.add_error(None, error)
    return render(request, 'equipment/form.html', {'form': form, 'title': f'Book {item.name}'})

@login_required
def booking_list(request):
    bookings = Booking.objects.select_related('equipment', 'user').order_by('-start_at')
    if not request.user.is_staff: bookings = bookings.filter(user=request.user)
    return render(request, 'equipment/booking_list.html', {'bookings': bookings})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method != 'POST':
        return redirect('booking_list')
    if booking.user != request.user and not request.user.is_staff:
        return redirect('booking_list')
    if booking.status in ['pending', 'approved'] and booking.start_at > timezone.now():
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled and the time slot released.')
    else:
        messages.error(request, 'Only future active bookings can be cancelled.')
    return redirect('booking_list')

@login_required
@staff_required
def approve_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST' and booking.status == 'pending':
        booking.status = 'approved'
        booking.save()
        messages.success(request, 'Booking approved.')
    return redirect('booking_list')

@login_required
def return_equipment(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user != request.user and not request.user.is_staff: return redirect('booking_list')
    if booking.status == 'returned': return redirect('booking_list')
    form = ReturnForm(request.POST or None, instance=booking)
    if request.method == 'POST' and form.is_valid():
        b = form.save(commit=False); b.status = 'returned'; b.returned_at = timezone.now(); b.save()
        if b.return_condition == 'damaged': b.equipment.condition = 'damaged'; b.equipment.status = 'maintenance'; b.equipment.save()
        messages.success(request, 'Return recorded.'); return redirect('booking_list')
    return render(request, 'equipment/form.html', {'form': form, 'title': f'Return {booking.equipment.name}'})

@login_required
def fault_create(request, pk):
    item = get_object_or_404(Equipment, pk=pk); form = FaultForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        fault = form.save(commit=False); fault.equipment = item; fault.reported_by = request.user; fault.save()
        item.status = 'maintenance'; item.save(); messages.success(request, 'Fault reported; equipment marked under maintenance.'); return redirect('fault_list')
    return render(request, 'equipment/form.html', {'form': form, 'title': f'Report fault: {item.name}'})

@login_required
def fault_list(request):
    faults = FaultReport.objects.select_related('equipment', 'reported_by').order_by('status', '-created_at')
    return render(request, 'equipment/fault_list.html', {'faults': faults})

@login_required
@staff_required
def fault_status(request, pk):
    fault = get_object_or_404(FaultReport, pk=pk)
    form = FaultStatusForm(request.POST or None, instance=fault)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Fault status updated.')
        return redirect('fault_list')
    return render(request, 'equipment/form.html', {'form': form, 'title': f'Update fault: {fault.title}'})

@login_required
@staff_required
def maintenance_create(request):
    form = MaintenanceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False); record.performed_by = request.user; record.save()
        if record.status == 'completed':
            record.equipment.status = 'available'; record.equipment.save()
            if record.fault: record.fault.status = 'resolved'; record.fault.save()
        messages.success(request, 'Maintenance record saved.'); return redirect('maintenance_list')
    return render(request, 'equipment/form.html', {'form': form, 'title': 'Log maintenance'})

@login_required
def maintenance_list(request): return render(request, 'equipment/maintenance_list.html', {'records': MaintenanceRecord.objects.select_related('equipment', 'fault').order_by('status', 'scheduled_for')})

@login_required
@staff_required
def reports(request):
    top = Equipment.objects.annotate(total_bookings=Count('bookings')).order_by('-total_bookings', 'name')
    return render(request, 'equipment/reports.html', {'top': top, 'by_status': Equipment.objects.values('status').annotate(total=Count('id')), 'returns': Booking.objects.filter(status='returned').count()})
