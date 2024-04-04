import json
from collections import OrderedDict

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from jsonfield import JSONField
from django.utils.translation import gettext_lazy as _

from enrichsdk.utils import SafeEncoder

class AppPolicyBase(models.Model):
    """
    Common policy document
    """

    class Meta:
        abstract = True

    appname    = models.CharField(max_length=64,
                                  default="default",
                                  verbose_name="App Name")

    namespace    = models.CharField(max_length=64,
                                    default="default",
                                    verbose_name="Namespace (to support multiple instances)")


    name         = models.CharField(max_length=256,
                                    blank=False,
                                    verbose_name="Name")
    desc         = models.CharField(max_length=1024,
                                    blank=False,
                                    verbose_name="Description")
    notes        = models.CharField(max_length=1024,
                                    blank=True,
                                    verbose_name="Additional Notes",
                                    help_text="")
    tags         = models.CharField(max_length=128,
                                    blank=True,
                                    default="",
                                    verbose_name="Tags")
    active       = models.BooleanField(default=True,
                                  verbose_name="Active",
                                  help_text="Enable/Disable")

    config = JSONField(verbose_name="Configuration", default={})
    # Hygiene
    created_at   = models.DateTimeField(auto_now_add=True)
    created_by   = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_creator', on_delete=models.PROTECT)
    modified_by  = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_modifier', on_delete=models.PROTECT)
    modified_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.desc

    def export(self, spec):

        response = OrderedDict([
            ('schema', self.__class__.__name__),
            ('id', self.pk),
            ('app', self.appname),
            ('name', self.name),
            ('namespace', self.namespace),
            ('desc', self.desc),
            ('notes', self.notes),
            ('tags', self.tags),
            ('active', self.active),
            ('created_at', self.created_at.isoformat()),
            ('created_by', self.created_by.username),
            ('modified_at', self.modified_at.isoformat()),
            ('modified_by', self.modified_by.username),
            ('config', self.config)
        ])

        return response


