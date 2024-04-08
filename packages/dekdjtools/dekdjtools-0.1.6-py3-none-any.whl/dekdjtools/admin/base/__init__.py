from django.contrib import admin
from django.utils.html import format_html


class MetaClass(admin.ModelAdmin.__class__):
    def __new__(mcs, name, bases, attrs):
        new_class = super(MetaClass, mcs).__new__(mcs, name, bases, attrs)
        if new_class.model_cls:
            admin.site.register(new_class.model_cls, new_class)
        return new_class


class ModelAdminAbstract(admin.ModelAdmin, metaclass=MetaClass):
    model_cls = None


class ModelAdminBase(ModelAdminAbstract):
    img_width = 50

    def format_img(self, img):
        if img:
            return format_html('<img src="{0}" width="{1}" height="{1}"/>'.format(img, self.img_width))
        else:
            return ""

    def format_a_img(self, img):
        if img:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" width="{1}" height="{1}"/></a>'.
                               format(img, self.img_width))
        else:
            return ""

    @staticmethod
    def format_a(url, text):
        if url:
            return format_html("<a href='{url}'target='_blank'>{text}</a>", url=url, text=text)
        return ""

    def format_img_list(self, img_list):
        return format_html("".join([self.format_img(x) for x in img_list]))

    def format_a_img_list(self, img_list):
        return format_html("".join([self.format_a_img(x) for x in img_list]))


def _auto_list_display(model_cls, up_limit=None):
    result = []
    primary_key = None
    for field in model_cls._meta.get_fields():
        if getattr(field, 'primary_key', False):
            primary_key = field.name
        elif field.is_relation:
            if field.many_to_one:
                result.append(field.name)
        else:
            result.append(field.name)
    if primary_key:
        result.insert(0, primary_key)
    if up_limit:
        result = result[:up_limit]
    return tuple(result)


def admin_register(model_cls, list_display=None):
    type(
        'admin',
        (ModelAdminBase,),
        {'model_cls': model_cls, 'list_display': list_display or _auto_list_display(model_cls)}
    )


def admin_register_batch(model_cls_list):
    for model_cls in model_cls_list:
        admin_register(model_cls)
