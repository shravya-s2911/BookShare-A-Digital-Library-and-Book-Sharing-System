def user_notifications(request):
    """
    Context processor to add user notifications to all templates
    """
    notifications = []
    unread_count = 0
    
    if request.user.is_authenticated:
        notifications = request.user.notifications.all()[:5]
        unread_count = request.user.notifications.filter(is_read=False).count()
    
    return {
        'user_notifications': notifications,
        'unread_notifications_count': unread_count,
    }
