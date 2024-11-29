from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):
    help = 'Create admin user if not exists'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

            user = User.objects.get(username='admin')
            user.user_type = 'executive'
            user.save()
            self.stdout.write(self.style.SUCCESS('Admin user created successfully.'))

        if not User.objects.filter(username='staff').exists():
            User.objects.create_user('staff', 'staff@example.com', 'staff123')
            user = User.objects.get(username='staff')
            user.user_type = 'staff'
            user.save()
            self.stdout.write(self.style.SUCCESS('Staff user created successfully.'))
