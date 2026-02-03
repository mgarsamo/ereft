"""
Messaging API Views for conversations and messages
"""
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Conversation, Message, Booking
from .serializers import ConversationSerializer, MessageSerializer


def is_admin(user):
    """Check if user is admin"""
    if not user.is_authenticated:
        return False
    admin_emails = ['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com']
    return user.is_superuser or user.is_staff or (user.email and user.email.lower() in [e.lower() for e in admin_emails])


def get_admin_users():
    """Get all admin users"""
    admin_emails = ['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com']
    return User.objects.filter(
        Q(is_superuser=True) | Q(is_staff=True) | Q(email__in=admin_emails)
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversations_list_create(request):
    """
    GET: List all conversations for current user
    POST: Create a new conversation
    """
    if request.method == 'GET':
        conversations = Conversation.objects.filter(participants=request.user).distinct().order_by('-updated_at')
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })
    
    elif request.method == 'POST':
        participant_id = request.data.get('participant')
        booking_id = request.data.get('booking')
        
        if not participant_id:
            return Response({'detail': 'Participant ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            return Response({'detail': 'Participant not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Enforce admin-user messaging only
        user_is_admin = is_admin(request.user)
        participant_is_admin = is_admin(participant)
        
        # Users can only message admins, admins can message users
        if not user_is_admin and not participant_is_admin:
            return Response({'detail': 'Users can only message admins'}, status=status.HTTP_403_FORBIDDEN)
        
        if user_is_admin and participant_is_admin:
            return Response({'detail': 'Admins cannot message other admins'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if conversation already exists
        existing_conv = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=participant
        ).first()
        
        if existing_conv:
            serializer = ConversationSerializer(existing_conv, context={'request': request})
            return Response(serializer.data)
        
        # Create new conversation
        booking = None
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                pass
        
        conversation = Conversation.objects.create(booking=booking)
        conversation.participants.add(request.user, participant)
        
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, conversation_id):
    """Get all messages in a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is a participant
    if request.user not in conversation.participants.all():
        return Response({'detail': 'You do not have permission to view this conversation'}, status=status.HTTP_403_FORBIDDEN)
    
    messages = conversation.messages.all().order_by('created_at')
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response({
        'results': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """Send a message in a conversation"""
    conversation_id = request.data.get('conversation')
    recipient_id = request.data.get('recipient')
    content = request.data.get('content', '').strip()
    
    if not content:
        return Response({'detail': 'Message content is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return Response({'detail': 'You are not a participant in this conversation'}, status=status.HTTP_403_FORBIDDEN)
        recipient = conversation.get_other_participant(request.user)
        if not recipient:
            return Response({'detail': 'Recipient not found'}, status=status.HTTP_404_NOT_FOUND)
    elif recipient_id:
        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response({'detail': 'Recipient not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Enforce admin-user messaging only
        user_is_admin = is_admin(request.user)
        recipient_is_admin = is_admin(recipient)
        
        # Users can only message admins, admins can message users
        if not user_is_admin and not recipient_is_admin:
            return Response({'detail': 'Users can only message admins'}, status=status.HTTP_403_FORBIDDEN)
        
        if user_is_admin and recipient_is_admin:
            return Response({'detail': 'Admins cannot message other admins'}, status=status.HTTP_403_FORBIDDEN)
        
        # Find or create conversation
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=recipient
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, recipient)
    else:
        return Response({'detail': 'Either conversation or recipient is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create message
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        recipient=recipient,
        content=content
    )
    
    # Update conversation updated_at
    conversation.updated_at = timezone.now()
    conversation.save()
    
    serializer = MessageSerializer(message, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_conversation_read(request, conversation_id):
    """Mark all messages in a conversation as read"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        return Response({'detail': 'You are not a participant in this conversation'}, status=status.HTTP_403_FORBIDDEN)
    
    # Mark all unread messages as read
    unread_messages = conversation.messages.filter(read=False).exclude(sender=request.user)
    unread_messages.update(read=True, read_at=timezone.now())
    
    return Response({'detail': 'Messages marked as read'})


def is_admin(user):
    """Check if user is admin"""
    if not user.is_authenticated:
        return False
    admin_emails = ['admin@ereft.com', 'melaku.garsamo@gmail.com', 'cb.garsamo@gmail.com', 'lydiageleta45@gmail.com']
    return user.is_superuser or user.is_staff or (user.email and user.email.lower() in [e.lower() for e in admin_emails])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Search users by username or email (admin only)"""
    # Only admins can search for users
    if not is_admin(request.user):
        return Response({'detail': 'Only admins can search for users'}, status=status.HTTP_403_FORBIDDEN)
    
    query = request.query_params.get('q', '').strip()
    
    if len(query) < 2:
        return Response({'results': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(email__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    from .serializers import UserSerializer
    serializer = UserSerializer(users, many=True, context={'request': request})
    return Response({
        'results': serializer.data,
        'count': len(serializer.data)
    })
