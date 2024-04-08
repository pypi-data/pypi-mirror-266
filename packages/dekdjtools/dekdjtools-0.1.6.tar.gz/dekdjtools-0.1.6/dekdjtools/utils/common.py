import re
import functools
from django.db import models


def length_of_string(s):
    return len(s) + functools.reduce(lambda x, y: x + len(y), re.findall("[\u2E80-\u9FFF]+", s), 0)


def update_instance(instance, data):
    empty = object()
    instance_list = [instance]
    for k, v in data.items():
        x = getattr(instance, k, empty)
        if x is not empty:
            if isinstance(x, models.Model):
                instance_list.extend(update_instance(x, v))
            else:
                setattr(instance, k, v)
    return instance_list
