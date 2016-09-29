from django.views.decorators.csrf import csrf_exempt

from push_notifications.models import APNSDevice, GCMDevice
from rest_framework.response import Response
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication

from MHacks.v1.serializers import AuthSerializer
from MHacks.v1.util import serialized_user


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class Authentication(views.ObtainAuthToken):
    """
    An easy convenient way to log a user in to get his/her token and the groups they are in.
    It also returns other basic information about the user like their name, etc.
    """
    authentication_classes = (CsrfExemptSessionAuthentication,)
    serializer_class = AuthSerializer

    @staticmethod
    def save_device(push_notification, user):
        # It's kinda dumb that we are shoving the preference down the 'name' field
        # But we don't want to create a whole new table just to store that!
        if push_notification['is_gcm']:
            GCMDevice.objects.update_or_create(
                registration_id=push_notification['registration_id'],
                defaults={
                    'name': push_notification['name'],
                    'registration_id': push_notification['registration_id'],
                    'user': user
                }
            )
        else:
            APNSDevice.objects.update_or_create(
                registration_id=push_notification['registration_id'],
                defaults={
                    'name': push_notification['name'],
                    'registration_id': push_notification['registration_id'],
                    'user': user
                }
            )

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        push_notification = serializer.validated_data.get('push_notification', None)
        if push_notification:
            self.save_device(push_notification, user)
        return Response({'token': token.key, 'user': serialized_user(user)})
