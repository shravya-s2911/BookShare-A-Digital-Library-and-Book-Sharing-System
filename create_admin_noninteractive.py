"""Create a default admin user non-interactively.

Usage:
  - Set environment variables ADMIN_USERNAME and ADMIN_PASSWORD to override defaults
  - Run: python create_admin_noninteractive.py
"""
import os
import django
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    username = os.environ.get('ADMIN_USERNAME', 'admin')
    password = os.environ.get('ADMIN_PASSWORD', 'admin123')

    if User.objects.filter(username=username).exists():
        print(f'User "{username}" already exists. No changes made.')
        return 0

    # create superuser
    try:
        user = User.objects.create_superuser(username=username, email='', password=password)
        user.first_name = 'Admin'
        user.last_name = ''
        user.role = 'admin'
        user.is_approved = True
        user.save()
        print(f'Created admin user: {username}')
        print('NOTE: This account has no email set. Change password after first login if needed.')
        return 0
    except Exception as e:
        print('Failed to create admin user:', e)
        return 2


if __name__ == '__main__':
    sys.exit(main())
