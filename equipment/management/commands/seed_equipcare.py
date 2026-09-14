from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from equipment.models import Booking, Equipment, FaultReport, MaintenanceRecord


class Command(BaseCommand):
    help = 'Creates sample users and realistic lab-management data for EquipCare.'

    def handle(self, *args, **options):
        users = [
            ('admin', 'admin12345', 'Aisha', 'Khan', 'admin@equipcare.local', True, True),
            ('labstaff', 'staff12345', 'Ravi', 'Patel', 'ravi.patel@equipcare.local', True, False),
            ('maya.student', 'student12345', 'Maya', 'Sharma', 'maya.sharma@equipcare.local', False, False),
            ('noah.student', 'student12345', 'Noah', 'Williams', 'noah.williams@equipcare.local', False, False),
        ]
        people = {}
        for username, password, first, last, email, staff, superuser in users:
            user, created = User.objects.get_or_create(username=username, defaults={
                'first_name': first, 'last_name': last, 'email': email,
                'is_staff': staff, 'is_superuser': superuser,
            })
            if created:
                user.set_password(password)
                user.save()
            people[username] = user

        inventory = [
            ('Digital Oscilloscope', 'ELEC-101', 'Electronics', 'Engineering Lab A', 'Four-channel oscilloscope for signal analysis.', 'excellent', 'available'),
            ('Thermal Imaging Camera', 'MECH-205', 'Imaging', 'Innovation Lab', 'Portable camera for thermal diagnostics.', 'good', 'available'),
            ('3D Printer', 'FAB-018', 'Fabrication', 'Prototype Studio', 'FDM printer for approved student prototypes.', 'fair', 'maintenance'),
            ('Digital Microscope', 'BIO-044', 'Optics', 'Biology Lab B', 'High-resolution microscope with digital capture.', 'excellent', 'available'),
            ('Arduino Sensor Kit', 'IOT-312', 'Embedded systems', 'Engineering Lab A', 'Shared kit with common sensors and jump leads.', 'good', 'available'),
            ('Centrifuge', 'CHEM-071', 'Chemistry', 'Chemistry Lab', 'Bench-top centrifuge for sample preparation.', 'damaged', 'maintenance'),
        ]
        items = {}
        for name, tag, category, lab, description, condition, status in inventory:
            item, _ = Equipment.objects.get_or_create(asset_tag=tag, defaults={
                'name': name, 'category': category, 'laboratory': lab,
                'description': description, 'condition': condition, 'status': status,
            })
            items[tag] = item

        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        Booking.objects.get_or_create(
            equipment=items['ELEC-101'], user=people['maya.student'], start_at=now + timedelta(days=1, hours=2),
            defaults={'end_at': now + timedelta(days=1, hours=4), 'purpose': 'Signals and systems practical', 'status': 'approved'},
        )
        Booking.objects.get_or_create(
            equipment=items['BIO-044'], user=people['noah.student'], start_at=now + timedelta(days=2, hours=1),
            defaults={'end_at': now + timedelta(days=2, hours=3), 'purpose': 'Cell morphology observation', 'status': 'pending'},
        )
        Booking.objects.get_or_create(
            equipment=items['IOT-312'], user=people['maya.student'], start_at=now - timedelta(days=4),
            defaults={'end_at': now - timedelta(days=4, hours=-2), 'purpose': 'Environmental monitoring prototype', 'status': 'returned', 'returned_at': now - timedelta(days=4, hours=-2), 'return_condition': 'good'},
        )

        fault, _ = FaultReport.objects.get_or_create(
            equipment=items['CHEM-071'], title='Unusual vibration during spin',
            defaults={'reported_by': people['noah.student'], 'description': 'The centrifuge vibrates noticeably at medium speed and should be inspected before use.', 'priority': 'high', 'status': 'open'},
        )
        FaultReport.objects.get_or_create(
            equipment=items['FAB-018'], title='Extruder temperature fluctuation',
            defaults={'reported_by': people['maya.student'], 'description': 'Temperature display drops intermittently during longer prints.', 'priority': 'medium', 'status': 'in_progress'},
        )
        MaintenanceRecord.objects.get_or_create(
            equipment=items['CHEM-071'], fault=fault, scheduled_for=now.date() + timedelta(days=1),
            defaults={'performed_by': people['labstaff'], 'maintenance_type': 'corrective', 'notes': 'Inspect rotor balance and drive assembly.', 'status': 'scheduled'},
        )
        MaintenanceRecord.objects.get_or_create(
            equipment=items['FAB-018'], scheduled_for=now.date() + timedelta(days=3),
            defaults={'performed_by': people['labstaff'], 'maintenance_type': 'preventive', 'notes': 'Calibrate nozzle and inspect heating element.', 'status': 'scheduled'},
        )
        self.stdout.write(self.style.SUCCESS('EquipCare sample data is ready.'))
