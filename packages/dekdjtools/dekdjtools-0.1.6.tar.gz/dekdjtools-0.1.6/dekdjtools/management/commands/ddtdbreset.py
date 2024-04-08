from django.core.management import call_command
from ..base import CommandBasic


class Command(CommandBasic):
    just_for_debug_mode = True

    def handle(self):
        call_command('reset_db', interactive=False)
        call_command('djdelmigrations')
        call_command('makemigrations')
        call_command('migrate')
