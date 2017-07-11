from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.fields import CharField
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from globals import GroupEnum
from utils import serialized_user
from models import MHacksModelSerializer


class MHacksUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, first_name, last_name, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        if not self.model:
            self.model = MHacksUser
        try:
            request = extra_fields.pop('request')
        except KeyError:
            request = None
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        from django.contrib.auth.models import Group
        user.groups.add(Group.objects.get(name=GroupEnum.HACKER))
        user.save(using=self._db)
        from utils import send_verification_email
        if request:
            send_verification_email(user, request)
        return user

    def create_user(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, first_name, last_name, **extra_fields)


class MHacksUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, db_index=True)
    email_verified = models.BooleanField(default=False)

    objects = MHacksUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        default_permissions = ()

    @property
    def is_active(self):
        return self.email_verified

    @property
    def is_staff(self):
        return self.is_superuser

    @property
    def is_sponsor(self):
        return self.groups.filter(name='sponsor').exists()

    @property
    def is_application_reader(self):
        return self.groups.filter(name='application_reader').exists()

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def __unicode__(self):
        return self.get_full_name()


@api_view(http_method_names=['GET'])
@permission_classes((IsAuthenticated,))
def update_user_profile(request):
    return Response(data=serialized_user(request.user))


class MHacksUserSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)

    class Meta:
        model = MHacksUser
        fields = ('id', 'first_name', 'last_name', 'email')
