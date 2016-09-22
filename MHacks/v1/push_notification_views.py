from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from push_notifications.api.rest_framework import APNSDeviceSerializer, GCMDeviceSerializer
from push_notifications.models import APNSDevice, GCMDevice


class PushNotificationView(generics.CreateAPIView):
    model_class = None

    def create(self, request, *args, **kwargs):
        preference = request.data.get('preference', None)
        if preference:
            request.data['name'] = preference
        if not request.data.get('name', None):
            request.data['name'] = '63'

        serializer = self.get_serializer(data=request.data)
        created = False
        try:
            serializer.is_valid(raise_exception=True)
            created = True
        except ValidationError:
            try:
                instance = self.model_class.objects.filter(registration_id=request.data.get('registration_id', None))[0]
            except (self.model_class.DoesNotExist, IndexError):
                raise ValidationError('Invalid request')
            serializer = self.get_serializer(instance=instance, data=request.data)
            serializer.is_valid(raise_exception=True)
        serializer.instance.user_id = request.user.pk if request.user and request.user.is_authenticated else None
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK, headers=headers)


class APNSTokenView(PushNotificationView):
    serializer_class = APNSDeviceSerializer
    model_class = APNSDevice


class GCMTokenView(PushNotificationView):
    serializer_class = GCMDeviceSerializer
    model_class = GCMDevice

