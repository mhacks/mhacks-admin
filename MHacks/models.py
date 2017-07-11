# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from rest_framework.serializers import ModelSerializer

from managers import MHacksQuerySet


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


class MHacksModelSerializer(ModelSerializer):
    def to_representation(self, instance):
        if getattr(instance, 'deleted', False):
            # noinspection PyProtectedMember
            return {instance._meta.pk.name: str(instance.pk), 'deleted': True}
        return super(MHacksModelSerializer, self).to_representation(instance)
