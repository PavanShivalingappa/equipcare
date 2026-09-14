from datetime import timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from .models import Booking, Equipment

class BookingRulesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('student', password='safe-pass-123')
        self.item = Equipment.objects.create(name='Oscilloscope', asset_tag='EL-001', category='Electronics', laboratory='Lab A')

    def test_overlapping_bookings_are_rejected(self):
        start = timezone.now() + timedelta(days=1)
        Booking.objects.create(equipment=self.item, user=self.user, start_at=start, end_at=start + timedelta(hours=2), purpose='Experiment')
        second = Booking(equipment=self.item, user=self.user, start_at=start + timedelta(hours=1), end_at=start + timedelta(hours=3), purpose='Experiment')
        with self.assertRaises(ValidationError):
            second.full_clean()

    def test_cancelled_booking_does_not_block_slot(self):
        start = timezone.now() + timedelta(days=1)
        Booking.objects.create(equipment=self.item, user=self.user, start_at=start, end_at=start + timedelta(hours=2), purpose='Experiment', status='cancelled')
        second = Booking(equipment=self.item, user=self.user, start_at=start, end_at=start + timedelta(hours=2), purpose='Experiment')
        second.full_clean()
