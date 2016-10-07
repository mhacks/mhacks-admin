from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from MHacks.models import MHacksUser


class Command(BaseCommand):
    help = 'Run with an arbitrary number of emails as arguments to add scan permission for'

    def add_arguments(self, parser):
        parser.add_argument('-emails', nargs='*', dest='emails', help="List of all emails to add as scanners")

    def handle(self, *args, **options):
        all_emails = options.get('emails', [])
        scan_permission = Permission.objects.get(codename='can_perform_scan')
        for email in all_emails:
            try:
                user = MHacksUser.objects.get(email=email)
                if not user.has_perm(scan_permission):
                    user.user_permissions.add(scan_permission)
                self.stdout.write('User {} got scan permission'.format(user.get_full_name()))
            except MHacksUser.DoesNotExist:
                self.stderr.write('No user found for {}'.format(email))
