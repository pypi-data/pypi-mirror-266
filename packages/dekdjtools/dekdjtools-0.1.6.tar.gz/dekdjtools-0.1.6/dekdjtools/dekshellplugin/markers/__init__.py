import re
from django_extensions.management.commands.shell_plus import Command
from dektools.file.operation import read_text
from dekshell.core.markers.base import MarkerBase, MarkerWithEnd


def django_setup(env):
    if not env.context.get('__django__'):
        import sys, os
        sys.path[:] = sys.path[:] + [os.getcwd()]

        project_name = re.search(
            r"""os.environ.setdefault\(['"]{1}DJANGO_SETTINGS_MODULE['"]{1}, ['"]{1}([0-9a-zA-Z_]+).settings['"]{1}\)""",
            read_text('./manage.py')
        ).groups()[0]

        import os, django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"{project_name}.settings")
        django.setup()
        env.context['__django__'] = True


class DjangoMarker(MarkerBase):
    tag_head = "@django"

    def exec(self, env, command, marker_node, marker_set):
        args = self.split_raw(command, 1)
        django_setup(env)

        vars_plus = Command().get_imported_objects(dict(quiet_load=True))
        vars_extra = {
            'User': vars_plus['get_user_model']()
        }

        self.eval(env, args[1], vars_plus | vars_extra)


class DjangoBlockMarker(MarkerWithEnd):
    tag_head = "@django-block"

    def exec(self, env, command, marker_node, marker_set):
        args = self.split_raw(command, 1)
        django_setup(env)

        vars_plus = Command().get_imported_objects(dict(quiet_load=True))
        vars_extra = {
            'User': vars_plus['get_user_model']()
        }

        self.eval_multi(
            env,
            '\n'.join([child.command for child in marker_node.children]),
            vars_plus | vars_extra
        )

        return []
