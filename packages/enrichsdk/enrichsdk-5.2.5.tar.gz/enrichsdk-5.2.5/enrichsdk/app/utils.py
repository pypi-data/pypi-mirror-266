"""
Utilities meant for the dashboard apps
"""
import sys
import inspect
import copy
import random
import re
import string
from ..lib.customer import find_usecase
from django.apps import AppConfig

def get_default_configuration():
    """
    Default description for any app
    """
    return """
    This app requires low code configuration implemented using the app
    sdk or other means. Please get in touch with the platform manager.
    """

def get_default_resources():
    """
    Default resources for any app
    """
    return """
    """

class EnrichAppConfig(AppConfig):
    """
    Base class for Dashboard Apps. Each is an instance of Django App.
    """

    name="default"
    """
    Name of the app
    """

    category = "default"
    """
    Category to which the app belongs
    """

    version = "v1"
    verbose_name = "default"
    description = "default"
    filename = None
    enable = False
    multiple = False
    composition = False
    status = "active"
    entry = "index"
    include_custom_urls = False
    tags = ["store"]
    _readme = ""
    _configuration = ""
    _resources = ""

    @classmethod
    def get_readme(cls):
        return cls._readme

    @classmethod
    def get_resources(cls):
        return cls._resources

    @property
    def readme(cls):
        if hasattr(cls, 'get_readme'):
            return cls.get_readme()
        elif cls._readme == "":
            return cls.description
        else:
            return cls._readme

    @property
    def configuration(cls):
        if hasattr(cls, 'get_configuration'):
            return cls.get_configuration()
        elif cls._configuration == "":
            return get_default_configuration()
        else:
            return cls._configuration

    @property
    def resources(cls):
        """
        Attribute to return the resources (a html text string)
        """
        if hasattr(cls, 'get_resources'):
            return cls.get_resources()
        elif cls._resources == "":
            return get_default_resources()
        else:
            return cls._resources

    @property
    def instanceid(self):
        """
        Unique id associated with the app
        """
        return str(id(self))

    def get_usecase(self):
        """
        Usecase to which the app belongs
        """
        if self.filename is None:
            return {}

        usecase = find_usecase(self.filename)
        self.usecase = copy.copy(usecase)
        return self.usecase

    def is_composition(self):
        return self.composition

    def get_name(self):
        return self.name

    def get_verbose_name(self):
        return self.verbose_name

    def get_description(self):
        return self.description

    def is_enabled(self):
        return self.enable

    def __str__(self):
        return f"{self.name}: {self.verbose_name}"

##################################################
# App helpers
##################################################
def generate_id(name):
    if len(name) > 0:
        slug = "".join([c if c.isalnum() else "_" for c in name]).lower()
    else:
        chars = string.ascii_uppercase + string.digits
        slug = ''.join(random.choices(chars, k=10))

    # remove multiple underscores..
    slug = re.sub(r'[\s_-]+', '_', slug)
    slug = re.sub(r"^[0-9_]+", "", slug)
    return slug

def clean_and_validate_widgets(widgets):

    for w in widgets:
        if 'id' not in w:
            w['id'] = generate_id(w['name'])


