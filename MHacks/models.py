from __future__ import unicode_literals

from django.db import models
from config.settings import AUTH_USER_MODEL
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from managers import MHacksQuerySet

from application_lists import MAJORS, COLLEGES


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

        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        from django.contrib.auth.models import Group
        user.groups.add(Group.objects.get(name='hacker'))
        user.save(using=self._db)
        from utils import send_verification_email
        try:
            request = extra_fields.pop('request')
            send_verification_email(user, request)
        except KeyError:
            pass
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
    # Constants
    GENDERS = [('m', 'Male'), ('f', 'Female'), ('non-binary', 'Non Binary'), ('none', 'Prefer not to answer')]
    RACES = [('white', 'White'),
             ('black', 'Black'),
             ('native', 'American Indian or Alaskan Native'),
             ('asian', 'Asian or Pacific Islander'),
             ('hispanic', 'Hispanic'),
             ('none', 'Prefer not to answer')]
    TECH_OPTIONS = [('ios', 'iOS'),
                    ('android', 'Android'),
                    ('web_dev', 'Web Dev'),
                    ('vr', 'Virtual/Augmented Reality'),
                    ('game_dev', 'Game Development'),
                    ('hardware', 'Hardware')]
    MAJORS = MAJORS  # imported from application_lists.py
    COLLEGES = COLLEGES  # imported from application_lists.py

    # General Information
    user = models.OneToOneField(AUTH_USER_MODEL)
    is_high_school = models.BooleanField()
    school = models.CharField(max_length=255, default='', choices=zip(range(0, len(COLLEGES)), COLLEGES))
    major = models.CharField(max_length=255, default='', choices=zip(range(0, len(MAJORS)), MAJORS))
    grad_date = models.DateField()
    age = models.IntegerField(default=18)

    # Demographic
    gender = models.CharField(choices=GENDERS, max_length=16)
    race = models.CharField(max_length=16, choices=RACES)
    pronouns = models.CharField(max_length=255)

    # Previous Experience
    num_hackathons = models.IntegerField(default=0)
    github = models.URLField()  # TODO: Add validator for github hostname
    linkedin = models.URLField()  # TODO: Add validator for linkedin hostname
    devpost = models.URLField()  # TODO: Add validator for devpost hostname
    personal_page = models.URLField()
    resume = models.FileField()
    other_link = models.URLField()

    # Interests
    cortex = ArrayField(models.CharField(max_length=16, choices=TECH_OPTIONS))
    proud_of = models.TextField()
    coolest_thing = models.TextField()
    other_info = models.TextField()

    # Logistics
    needs_reimbursement = models.BooleanField(default=False)
    can_pay = models.FloatField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)  # state abbreviations
    mentoring = models.BooleanField(default=False)
    submitted = models.BooleanField(default=False)

    # Private administrative use
    score = models.FloatField()
    reimbursement = models.FloatField()

    def __unicode__(self):
        return self.user.get_full_name() + '\'s Application'
