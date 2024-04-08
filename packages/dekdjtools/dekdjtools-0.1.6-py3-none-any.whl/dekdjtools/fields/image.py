import os
from django.db import models
from ..snowflake import SnowflakeGenerator


class ImageField(models.ImageField):
    def __init__(self, *args, **kwargs):
        self.snowflake_generator = SnowflakeGenerator.new_instance()
        super().__init__(*args, **kwargs)

    def generate_filename(self, instance, filename):
        filename = str(self.snowflake_generator.get_next_id()) + os.path.splitext(filename)[-1]
        return super().generate_filename(instance, filename)
