from .models import Notification
from django.utils import timezone


def send_notification(user, notification_type, title, message, related_book=None, related_user=None):
    """
    Helper function to send notifications to users
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        related_book=related_book,
        related_user=related_user,
    )
    return notification
