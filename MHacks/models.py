from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from globals import GroupEnum
from config.settings import AUTH_USER_MODEL
from managers import MHacksQuerySet


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


class Any(models.Model):
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    objects = MHacksQuerySet().as_manager()

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save(using=using, update_fields=['deleted'])
        return 1

    class Meta:
        abstract = True


class Location(Any):
    name = models.CharField(max_length=60)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __unicode__(self):
        return self.name


class Event(Any):
    name = models.CharField(max_length=60)
    info = models.TextField(default='')
    locations = models.ManyToManyField(Location)
    start = models.DateTimeField()
    duration = models.DurationField()
    CATEGORIES = ((0, 'Logistics'), (1, 'Social'), (2, 'Food'), (3, 'Tech Talk'), (4, 'Other'))
    category = models.IntegerField(choices=CATEGORIES)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Announcement(Any):
    title = models.CharField(max_length=60)
    info = models.TextField(default='')
    broadcast_at = models.DateTimeField()
    category = models.PositiveIntegerField(validators=[MinValueValidator(0),
                                                       MaxValueValidator(63)])
    approved = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title


class PushToken(models.Model):
    # 100 is arbitrary, if someone knows what the max length is?
    token = models.CharField(max_length=100, unique=True, primary_key=True, db_index=True)
    is_apns = models.BooleanField()
    preferences = models.IntegerField()

    def __unicode__(self):
        return self.token


class Application(Any):
    from application_lists import GENDERS, RACES, TECH_OPTIONS, COLLEGES, MAJORS, STATES

    # General information
    user = models.OneToOneField(AUTH_USER_MODEL)
    school = models.CharField(max_length=255, default='', choices=zip(COLLEGES, COLLEGES))
    is_high_school = models.BooleanField()
    major = models.CharField(max_length=255, default='', choices=zip(MAJORS, MAJORS))
    grad_date = models.DateField()
    birthday = models.DateField()

    # Demographic
    gender = models.CharField(max_length=16, choices=GENDERS, default='none')
    race = models.CharField(max_length=16, choices=RACES, default='none')

    # External Links
    github = models.URLField()
    devpost = models.URLField()
    personal_website = models.URLField()
    resume = models.FileField()

    # Experience
    num_hackathons = models.IntegerField(default=0)

    # Interests
    cortex = ArrayField(models.CharField(max_length=16, choices=TECH_OPTIONS, default='', blank=True), size=len(TECH_OPTIONS))
    passionate = models.TextField()
    coolest_thing = models.TextField()
    other_info = models.TextField()

    # Logistics
    needs_reimbursement = models.BooleanField(default=False)
    can_pay = models.FloatField(default=0)
    from_city = models.CharField(max_length=255, default='')
    from_state = models.CharField(max_length=5, choices=zip(STATES, STATES), default='')

    # Miscellaneous
    mentoring = models.BooleanField(default=False)
    submitted = models.BooleanField(default=False)

    # Private administrative use
    score = models.FloatField(default=0)
    reimbursement = models.FloatField(default=0)

    def __unicode__(self):
        return self.user.get_full_name() + '\'s Application'
