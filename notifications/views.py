from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from friends.models import Friend
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated


class NotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        notifs = Notification.objects.filter(receiver=user, accepted__isnull=True).order_by('-created_at')
        serializer = NotificationSerializer(notifs, many=True)
        return Response(serializer.data)

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        if not receiver_id:
            return Response({'error': 'receiver_id is required'}, status=400)

        if request.user.id == int(receiver_id):
            return Response({'error': 'You cannot friend yourself.'}, status=400)

        if Notification.objects.filter(sender=request.user, receiver_id=receiver_id, type='FRIEND', accepted=None).exists():
            return Response({'error': 'Friend request already sent.'}, status=400)

        sender_name = request.user.username
        notif = Notification.objects.create(
            sender=request.user,
            receiver_id=receiver_id,
            type='FRIEND',
            message=f"{sender_name} send You friend request"
        )
        return Response(NotificationSerializer(notif).data, status=201)


class ManageNotifications(APIView):
    def post(self, request, notification_id):
        try:
            notif = Notification.objects.get(id=notification_id, receiver=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found.'}, status=404)

        if notif.accepted is not None:
            return Response({'error': 'Notification already responded.'}, status=400)

        notif.accepted = True
        notif.save()

        if notif.type == 'FRIEND':
            Friend.objects.create(user1=notif.sender, user2=notif.receiver)

        return Response({'message': 'Accepted successfully.'})

    def delete(self, request, notification_id):
        try:
            notif = Notification.objects.get(id=notification_id, receiver=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found.'}, status=404)

        if notif.accepted is not None:
            return Response({'error': 'Notification already responded.'}, status=400)

        notif.delete()
        return Response({'message': 'Declined successfully.'})