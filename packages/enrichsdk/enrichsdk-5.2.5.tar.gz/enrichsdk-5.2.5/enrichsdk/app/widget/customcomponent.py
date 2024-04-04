import json
from enum import Enum
from enrichsdk.app.utils import generate_id
import logging

logger= logging.getLogger('app')


class BaseComponent():
    def __init__(self, name, ctype, desc):
        self.name = name
        self.ctype = ctype
        self.description = desc
        self.id = generate_id(self.name)

    def get_component_type(self):
        return self.ctype


    def to_json(self):
        return json.dumps(self.__dict__)


class CustomComponentTypes(str, Enum):
    Notes = 'Notes'
    Headers = 'Headers'
    Body = 'Body'
    Media = 'Media'

    def get_name(self):
        return str(self.value)


class CustomComponent(BaseComponent):
    def __init__(self, name, custom_component_type):
        super().__init__(name, custom_component_type)


""" {   "search_params":
        {
            "persona": persona_name,
            "table": table_name
        },
        "search_query": request.GET.get('query', None),
        "search_column_names": search_columns_names,
        "url": f"?persona={persona_name}&table={table_name}&query="
    } """


class SearchComponent(BaseComponent):
    def __init__(self, name):
        self.ctype = 'Search'
        super().__init__(name, self.ctype)
        self.search_columns_names = []
        self.persona_name = ''
        self.url = ''
        self.table_name = ''
        self.search_query = ''

    def set_search_column_names(self, value):
        self.search_columns_names = value

    def get_search_column_names(self):
        return self.search_columns_names

    @property
    def search_query_attr(self):
        return self.search_query

    @search_query_attr.setter
    def search_query_attr(self, value):
        self.search_query = value

    @property
    def persona_name_attr(self):
        return

    """
    {
        "id": "notes",
        "label": "",
        "description": notes,
        "type": ctype,
        "icon": "",
        "class": "",
        "template": "notes"
    }
    """


class NotesType(str, Enum):
    LIST = 'list'
    PARAGRAPH = 'notes'


class NotesComponent(BaseComponent):
    def __init__(self, name, label, desc, icon, template):
        super().__init__(name, CustomComponentTypes.Notes, desc)
        self.label = label
        self.type = NotesType.LIST
        self.icon = icon
        self.css_class = ''
        self.template = template

    @property
    def css_class_attr(self):
        return self.css_class

    @css_class_attr.setter
    def css_class_attr(self, value):
        self.css_class = value

    # @property
    # def label_attr(self):
    #     return self.css_class
    #
    # @label_attr.setter
    # def label_attr(self, value):
    #     self.label = value
    #
    # @property
    # def desc_attr(self):
    #     return self.desc
    #
    # @desc_attr.setter
    # def desc_attr(self, value):
    #     self.desc = value
    #
    # @property
    # def icon_attr(self):
    #     return self.icon
    #
    # @icon_attr.setter
    # def icon_attr(self, value):
    #     self.icon = value
    #
    # @property
    # def template_attr(self):
    #     return self.template
    #
    # @template_attr.setter
    # def template_attr(self, value):
    #     self.template = value

    def type_attr(self):
        return self.type

    def type_attr(self, value):
        self.type = value



class MediaType(str, Enum):
    IMAGE = 'image'
    VIDEO = 'video'


class MediaComponent(BaseComponent):
    def __init__(self, name):
        super().__init__(name)
        self.label = ''
        self.description = ''
        self.type = MediaType.IMAGE
        self.icon = ''
        self.css_class = ''
        self.template = ''


class HeaderComponent(BaseComponent):
    def __init__(self, name):
        super().__init__(name, CustomComponentTypes.Headers, CustomComponentTypes.Headers.get_name())
        self.components = {}

    def add_component(self, component_type, component):
        if isinstance(component_type, CustomComponentTypes):
            self.components[component_type.get_name()] = component
        else:
            logger.error("Provide correct type of Custom Component")

    def get_components(self):
        return self.components


class BodyComponent(BaseComponent):
    def __init__(self, name):
        super().__init__(name, CustomComponentTypes.Body, CustomComponentTypes.Body.get_name())
        self.components = {}

    def add_component(self, component):

        if component:
            component_type = component.get_component_type()
            component_name = component_type.get_name().lower()
            if isinstance(component_type, CustomComponentTypes):

                if component_name in self.components:
                    self.components[component_name].append(component)

                else:
                    components = [component]
                    self.components[component_name] = components

            else:
                logger.error("Invalid component type")
        else:
            logger.error("Component can't be null")

    def get_components(self):
        return self.components
