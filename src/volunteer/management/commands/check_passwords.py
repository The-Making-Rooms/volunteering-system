# example: core/management/commands/check_passwords.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

class Command(BaseCommand):
    help = "Find users with unusable passwords. Optionally reset to random passwords."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Replace unusable passwords with a random 32-character alphanumeric value.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        affected = []
        unaffected = []
        for user in User.objects.all():
            if not user.has_usable_password():
                affected.append(user)
            else:
                unaffected.append(user)

        self.stdout.write(
            f"Affected (unusable password): {len(affected)}\nUnaffected: {len(unaffected)}"
        )

        if options["fix"]:
            for user in affected:
                random_pw = get_random_string(32)
                user.set_password(random_pw)
                user.save()
            self.stdout.write(
                f"Set random passwords for {len(affected)} affected accounts."
            )
