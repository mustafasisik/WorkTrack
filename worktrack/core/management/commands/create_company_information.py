import datetime
from django.core.management.base import BaseCommand
from core.models import CompanyInformation

class Command(BaseCommand):
    help = 'Create default company information'

    def handle(self, *args, **kwargs):
        if not CompanyInformation.objects.exists():
            CompanyInformation.objects.create(
                work_start_time=datetime.time(8, 0),
                work_end_time=datetime.time(18, 0)
            )
            self.stdout.write(self.style.SUCCESS('Default company information created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Default company information already exists.'))
