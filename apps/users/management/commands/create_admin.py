from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an admin user for the BookShare system'

    def handle(self, *args, **options):
        if User.objects.filter(role='admin').exists():
            self.stdout.write(self.style.WARNING('An admin user already exists!'))
            return

        self.stdout.write('Creating admin user for BookShare...')
        
        username = input('Username: ')
        email = input('Email: ')
        password = input('Password: ')
        password_confirm = input('Confirm Password: ')
        first_name = input('First Name: ')
        last_name = input('Last Name: ')

        if password != password_confirm:
            self.stdout.write(self.style.ERROR('Passwords do not match!'))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User with username "{username}" already exists!'))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User with email "{email}" already exists!'))
            return

        admin_user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        admin_user.role = 'admin'
        admin_user.is_approved = True
        admin_user.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {username}'))
        self.stdout.write('\nYou can now log in at /users/login/ or /admin/')

