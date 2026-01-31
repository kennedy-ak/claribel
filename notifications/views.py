from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, F
from .models import Conversation, Message


@login_required
def inbox_view(request):
    """Show all conversations for the current user."""
    # Get all conversations where the user is a participant
    from django.db.models import Q

    conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('participant1', 'participant2').order_by('-updated_at')

    # Annotate conversations with additional data
    conversation_data = []
    for conv in conversations:
        other_user = conv.get_other_participant(request.user)
        unread_count = conv.messages.filter(is_read=False).exclude(sender=request.user).count()
        last_msg = conv.messages.last()

        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'unread_count': unread_count,
            'last_message': last_msg
        })

    context = {
        'conversations': conversation_data
    }
    return render(request, 'notifications/inbox.html', context)


@login_required
def conversation_detail_view(request, conversation_id):
    """View and reply to a conversation."""
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Check if user is part of this conversation
    if conversation.participant1 != request.user and conversation.participant2 != request.user:
        messages.error(request, 'You do not have permission to view this conversation.')
        return redirect('notifications:inbox')

    # Mark messages as read if the user is the recipient (not sender)
    from django.db.models import Q
    conversation.messages.filter(~Q(sender=request.user)).update(is_read=True)

    # Get all messages in this conversation
    messages_list = conversation.messages.all()

    other_user = conversation.get_other_participant(request.user)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            messages.success(request, 'Message sent!')
            return redirect('notifications:conversation_detail', conversation_id=conversation_id)
        else:
            messages.error(request, 'Please enter a message.')

    context = {
        'conversation': conversation,
        'messages': messages_list,
        'other_user': other_user
    }
    return render(request, 'notifications/conversation_detail.html', context)


@login_required
def conversation_start_view(request, username):
    """Start a new conversation with another user."""
    other_user = get_object_or_404(User, username=username)

    # Check if users can message each other
    can_message = False

    # Users must be in the same organization
    if (request.user.profile.organization and
        other_user.profile.organization and
        request.user.profile.organization == other_user.profile.organization):

        # Mentees can message mentors
        if request.user.profile.role == 'mentee':
            if other_user.profile.role == 'mentor':
                can_message = True
        # Mentors can message their mentees or other mentors
        elif request.user.profile.role == 'mentor':
            mentees = request.user.profile.get_mentees()
            if (other_user.profile.role == 'mentee' and other_user in [m.user for m in mentees]):
                can_message = True
            elif other_user.profile.role == 'mentor':
                can_message = True

    if not can_message:
        messages.error(request, 'You can only message people in your organization.')
        return redirect('notifications:inbox')

    # Check if conversation already exists
    try:
        # Try to find existing conversation
        conversation = Conversation.objects.get(
            Q(participant1=request.user, participant2=other_user) |
            Q(participant1=other_user, participant2=request.user)
        )
        return redirect('notifications:conversation_detail', conversation_id=conversation.id)
    except Conversation.DoesNotExist:
        # Create new conversation
        conversation = Conversation.objects.create(
            participant1=request.user,
            participant2=other_user
        )

        if request.method == 'POST':
            content = request.POST.get('content', '').strip()
            if content:
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content=content
                )
                messages.success(request, f'Conversation started with {other_user.username}!')
                return redirect('notifications:conversation_detail', conversation_id=conversation.id)
            else:
                messages.error(request, 'Please enter a message.')

        context = {
            'conversation': conversation,
            'other_user': other_user
        }
        return render(request, 'notifications/conversation_start.html', context)


# Keep old URLs working by redirecting
@login_required
def message_send_view(request, username):
    """Redirect to new conversation system."""
    return conversation_start_view(request, username)


@login_required
def message_detail_view(request, message_id):
    """Redirect to conversation detail (for backwards compatibility)."""
    messages.info(request, 'Messages are now organized in conversations.')
    return redirect('notifications:inbox')
