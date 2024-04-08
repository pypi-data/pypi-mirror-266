from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToOneRel, ManyToManyRel, OneToOneRel
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation, GenericRel


class ModelFields:
    def __init__(self, model_cls):
        self.model_cls = model_cls
        self.common = set()
        self.auto = set()
        self.ct = {}
        self.ct_pk = {}
        self.ct_query = {}
        self.o2o = {}
        self.o2m = {}
        self.m2m = {}
        self.o2o_r = {}
        self.m2m_r = {}
        self.m2o_r = {}
        self.o2m_r = {}
        self.attname = {}
        self.parse()
        self.attrs = self.common | self.auto | set(self.ct) | \
                     set(self.o2o) | set(self.o2m) | set(self.m2m) | \
                     set(self.o2o_r) | set(self.o2m_r) | set(self.m2m_r) | set(self.m2o_r)

    def parse(self):
        ct__ct_field = {}
        ct__fk_field = set()
        for field in self.model_cls._meta.private_fields:
            if isinstance(field, GenericForeignKey):
                ct__ct_field[field.ct_field] = field.name
                ct__fk_field.add(field.fk_field)
                self.ct[field.name] = None
                self.ct_pk[field.name] = field.fk_field
                self.attname[field.name] = field.fk_field
            elif isinstance(field, GenericRelation):
                self.o2m_r[field.name] = field.related_model
            else:
                raise LookupError
        for field in self.model_cls._meta.related_objects:
            if isinstance(field, ManyToOneRel):
                self.m2o_r[field.get_accessor_name()] = field.related_model
            elif isinstance(field, ManyToManyRel):
                self.m2m_r[field.get_accessor_name()] = field.related_model
            elif isinstance(field, OneToOneRel):
                self.o2o_r[field.get_accessor_name()] = field.related_model
            elif isinstance(field, GenericRel):
                gr = ct__ct_field[field.remote_field.content_type_field_name]
                self.ct[gr] = field.related_model
                self.ct_query[gr] = field.name
                self.attname[field.name] = self.attname.pop(gr)
            else:
                raise LookupError
        for field in self.model_cls._meta.many_to_many:
            self.m2m[field.name] = field.related_model
        for field in self.model_cls._meta.fields:
            if field.name in ct__fk_field or field.name in ct__ct_field:
                continue
            if field.auto_created:
                self.auto.add(field.name)
            elif isinstance(field, ForeignKey):
                self.o2m[field.name] = field.related_model
            elif isinstance(field, OneToOneField):
                self.o2o[field.name] = field.related_model
            else:
                self.common.add(field.name)
            self.attname[field.name] = field.attname
