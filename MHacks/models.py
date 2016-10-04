# coding=utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
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

    def application_or_none(self):
        try:
            return Application.objects.get(user=self, deleted=False)
        except Application.DoesNotExist:
            return None

    def registration_or_none(self):
        try:
            return Registration.objects.get(user=self, deleted=False)
        except Registration.DoesNotExist:
            return None

    def cleaned_school_name(self, application=None):
        if not application:
            application = self.application_or_none()
        return application.school.replace('-', ' – ') if application else 'Unknown'

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


class Any(models.Model):
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    objects = MHacksQuerySet().as_manager()

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        from datetime import datetime
        from pytz import utc
        self.last_updated = datetime.now(tz=utc)
        self.save(using=using, update_fields=['deleted', 'last_updated'])
        return 1

    class Meta:
        abstract = True


class Floor(Any):
    name = models.CharField(max_length=60)
    index = models.IntegerField(unique=True)
    image = models.URLField()
    description = models.TextField(blank=True)
    offset_fraction = models.FloatField(default=1.0)
    aspect_ratio = models.FloatField(default=1.0)

    def __unicode__(self):
        return '{} displayed at index {}'.format(self.name, str(self.index))


class Location(Any):
    name = models.CharField(max_length=60)
    floor = models.ForeignKey(Floor, on_delete=models.PROTECT, null=True, blank=True)

    def __unicode__(self):
        if self.floor:
            return "{} on the {}".format(self.name, str(self.floor.name))
        return self.name


class Event(Any):
    name = models.CharField(max_length=60)
    info = models.TextField(default='')
    locations = models.ManyToManyField(Location)
    start = models.DateTimeField()
    duration = models.DurationField()
    CATEGORIES = ((0, 'General'), (1, 'Logistics'), (2, 'Food'), (3, 'Learn'), (4, 'Social'))
    category = models.IntegerField(choices=CATEGORIES)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Announcement(Any):
    title = models.CharField(max_length=60)
    info = models.TextField(default='')
    broadcast_at = models.DateTimeField()
    category = models.PositiveIntegerField(validators=[MinValueValidator(0),
                                                       MaxValueValidator(31)])
    approved = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    @staticmethod
    def max_category():
        return 31

    def __unicode__(self):
        return self.title


class Application(Any):
    from application_lists import TECH_OPTIONS, APPLICATION_DECISION

    # General information
    user = models.OneToOneField(AUTH_USER_MODEL)
    is_high_school = models.BooleanField(default=False)
    is_international = models.BooleanField(default=False)
    school = models.CharField(max_length=255, default='')
    major = models.CharField(max_length=255, default='', blank=True)
    grad_date = models.DateField(null=True, blank=True)
    birthday = models.DateField()

    # Demographic
    gender = models.CharField(max_length=32, default='')
    race = models.CharField(max_length=64, default='')

    # External Links
    github = models.URLField()
    devpost = models.URLField()
    personal_website = models.URLField()
    resume = models.FileField(max_length=(10 * 1024 * 1024))  # 10 MB max file size

    # Experience
    num_hackathons = models.IntegerField(default=0, validators=[
        MinValueValidator(limit_value=0, message='You went to negative hackathons? Weird...')])
    mentoring = models.BooleanField(default=False)

    # Interests
    cortex = ArrayField(models.CharField(max_length=16, choices=TECH_OPTIONS, default='', blank=True),
                        size=len(TECH_OPTIONS))
    passionate = models.TextField()
    coolest_thing = models.TextField()
    other_info = models.TextField()

    # Logistics
    needs_reimbursement = models.BooleanField(default=False)
    can_pay = models.FloatField(default=0, validators=[MinValueValidator(limit_value=0.0)])
    from_city = models.CharField(max_length=255, default='')
    from_state = models.CharField(max_length=64, default='')

    # Miscellaneous
    submitted = models.BooleanField(default=False)

    # Private administrative use
    score = models.FloatField(default=0)
    reimbursement = models.FloatField(default=0, validators=[MinValueValidator(limit_value=0.0)])
    decision = models.CharField(max_length=16, choices=zip(APPLICATION_DECISION, APPLICATION_DECISION),
                                default='Decline')

    def __unicode__(self):
        return self.user.get_full_name() + '\'s Application'

    def user_is_minor(self):
        from datetime import date
        return self.birthday >= date(year=1998, month=10, day=7)


class MentorApplication(Any):
    from application_lists import SKILLS, APPLICATION_DECISION

    user = models.OneToOneField(AUTH_USER_MODEL)

    # Mentor Info
    first_time_mentor = models.BooleanField(default=False)

    # Short Response
    what_importance = models.TextField()
    why_mentor = models.TextField()
    mentorship_ideas = models.TextField()

    # Skill Review
    skills = ArrayField(models.CharField(max_length=32, choices=zip(SKILLS, SKILLS), blank=True), size=len(SKILLS))
    other_skills = models.CharField(max_length=255, default='', blank=True)
    github = models.URLField(blank=True)

    # Commitment
    agree_tc = models.BooleanField(default=False)

    # Internal
    submitted = models.BooleanField(default=False)
    score = models.FloatField(default=0)
    reimbursement = models.FloatField(default=0, validators=[MinValueValidator(limit_value=0.0)])
    decision = models.CharField(max_length=16, choices=zip(APPLICATION_DECISION, APPLICATION_DECISION),
                                default='Decline')

    def __unicode__(self):
        return self.user.get_full_name() + '\'s Mentor Application'


class Registration(Any):
    from application_lists import ACCEPTANCE, TRANSPORTATION, TECH_OPTIONS, T_SHIRT_SIZES, DIETARY_RESTRICTIONS, \
        DEGREES, EMPLOYMENT, EMPLOYMENT_SKILLS

    # User
    user = models.OneToOneField(AUTH_USER_MODEL)

    # Acceptance
    acceptance = models.CharField(max_length=32, choices=ACCEPTANCE)

    # Logistics
    transportation = models.CharField(max_length=32, choices=TRANSPORTATION)

    # Mentorship
    want_help = ArrayField(models.CharField(max_length=16, choices=TECH_OPTIONS, blank=True), size=len(TECH_OPTIONS),
                           blank=True)
    other_want_help = models.CharField(max_length=64, blank=True)
    can_help = ArrayField(models.CharField(max_length=16, choices=TECH_OPTIONS, blank=True), size=len(TECH_OPTIONS),
                          blank=True, null=True)
    other_can_help = models.CharField(max_length=64, blank=True)

    # Day-of Specifics
    t_shirt_size = models.CharField(max_length=4, choices=zip(T_SHIRT_SIZES, T_SHIRT_SIZES))
    dietary_restrictions = models.CharField(max_length=32, choices=zip(DIETARY_RESTRICTIONS, DIETARY_RESTRICTIONS),
                                            blank=True)
    accommodations = models.TextField(blank=True)
    medical_concerns = models.TextField(blank=True)
    anything_else = models.TextField(blank=True)
    phone_number = models.CharField(max_length=16,
                                    validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                                               message="Phone number must be entered in the format: \
                                                               '+#########'. Up to 15 digits allowed.")])

    # Sponsor & Employment Information
    employment = models.CharField(max_length=64, choices=EMPLOYMENT)
    degree = models.CharField(max_length=16, choices=zip(DEGREES, DEGREES))
    technical_skills = ArrayField(
        models.CharField(max_length=32, choices=zip(EMPLOYMENT_SKILLS, EMPLOYMENT_SKILLS), blank=True),
        size=len(EMPLOYMENT_SKILLS), blank=True)

    # Waivers and Code of Conduct
    code_of_conduct = models.BooleanField(default=False)
    waiver_signature = models.CharField(max_length=128)
    mlh_code_of_conduct = models.BooleanField(default=False)

    # Internal
    submitted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.get_full_name() + '\'s Registration'


class ScanEvent(Any):
    name = models.CharField(max_length=60, unique=True)
    number_of_allowable_scans = models.IntegerField(default=1, validators=[MinValueValidator(limit_value=0)])
    scanned_users = models.ManyToManyField(AUTH_USER_MODEL, related_name="scan_event_users", blank=True, through='ScanEventUser')
    expiry_date = models.DateTimeField(blank=True, null=True)
    custom_verification = models.CharField(blank=True, max_length=255)

    class Meta:
        permissions = (("can_perform_scan", "Can perform a scan"),)

    def __unicode__(self):
        return self.name


# A custom proxy used for the Many To Many field below
class ScanEventUser(models.Model):
    scan_event = models.ForeignKey(ScanEvent, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)

    def __unicode__(self):
        return self.user.get_full_name() + '\'s ' + self.scan_event.name + ' Scan (' + str(self.count) + ')'
