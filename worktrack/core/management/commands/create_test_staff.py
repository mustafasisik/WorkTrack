from django.core.management.base import BaseCommand
from core.models import User
from faker import Faker

class Command(BaseCommand):
    help = 'Create random staff users using Faker (max total users: 100)'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of staff users to create')

    def handle(self, *args, **options):
        fake = Faker()
        requested_count = options['count']
        current_user_count = User.objects.count()
        
        if current_user_count >= requested_count:
            self.stdout.write(
                self.style.WARNING(
                    f'Cannot create new users: Maximum user limit (100) reached. Current count: {current_user_count}'
                )
            )
            return
            
        # Calculate how many users we can still create
        
        for i in range(requested_count):
            username = fake.user_name()
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = fake.user_name()
            
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password=fake.password(length=12),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                user_type='staff',
                is_staff=False,  # They are staff type but not admin staff
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created staff user: {username}'
                )
            )
        
        if requested_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                f'Successfully created {requested_count} staff users'
                )
            )
