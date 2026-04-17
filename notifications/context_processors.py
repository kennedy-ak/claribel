from .models import Message


def unread_message_count(request):
    if not request.user.is_authenticated:
        return {'unread_message_count': 0}
    count = Message.objects.filter(
        conversation__in=request.user.conversations_as_p1.all() | request.user.conversations_as_p2.all(),
        is_read=False
    ).exclude(sender=request.user).count()
    return {'unread_message_count': count}
