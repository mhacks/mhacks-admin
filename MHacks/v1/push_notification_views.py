from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from push_notifications.api.rest_framework import APNSDeviceSerializer, GCMDeviceSerializer
from push_notifications.models import APNSDevice, GCMDevice
from MHacks.models import Announcement


class PushNotificationView(generics.CreateAPIView):
    model_class = None
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        preference = request.data.get('preference', 0)
        if not preference:
            preference = request.data.get('name', str(Announcement.max_category()))

        try:
            if int(preference) <= 0:
                preference = str(Announcement.max_category())
        except ValueError:
            preference = str(Announcement.max_category())

        copied_data = request.data.copy()
        copied_data['name'] = preference

        serializer = self.get_serializer(data=copied_data)
        created = False
        try:
            serializer.is_valid(raise_exception=True)
            created = True
        except ValidationError as e:
            try:
                instance = self.model_class.objects.filter(registration_id=copied_data.get('registration_id', None))[0]
            except (self.model_class.DoesNotExist, IndexError):
                raise e
            serializer = self.get_serializer(instance=instance, data=copied_data)
            serializer.is_valid(raise_exception=True)

        serializer.validated_data['user_id'] = request.user.pk if request.user and request.user.is_authenticated() else None
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK, headers=headers)


class APNSTokenView(PushNotificationView):
    serializer_class = APNSDeviceSerializer
    model_class = APNSDevice


class GCMTokenView(PushNotificationView):
    serializer_class = GCMDeviceSerializer
    model_class = GCMDevice

