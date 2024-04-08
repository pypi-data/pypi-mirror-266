import os
from django.conf import settings
from django.apps import apps
from dektools.file import normal_path

project_dir = normal_path(settings.BASE_DIR)

project_dir_prefix = project_dir + os.path.sep


def list_migrations():
    result = set()
    for app in apps.get_app_configs():
        app_path = app.path
        if app_path.startswith(project_dir_prefix):
            migrations_path = os.path.join(app_path, 'migrations')
            if os.path.isdir(migrations_path):
                for item in os.listdir(migrations_path):
                    item_path = os.path.join(migrations_path, item)
                    if os.path.isfile(item_path) and item != '__init__.py' and os.path.splitext(item)[-1] == '.py':
                        result.add(item_path)
    return project_dir, result
