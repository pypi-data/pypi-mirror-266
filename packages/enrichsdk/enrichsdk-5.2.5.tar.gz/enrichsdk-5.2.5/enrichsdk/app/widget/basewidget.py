from enrichsdk.app.utils import generate_id
import json
import logging


class BaseWidget:
    def __init__(self, widgetid, name, title, template):

        if name is None:
            raise Exception("{} can't be null for the widget".format("Name"))

        if template is None:
            raise Exception("{} can't be null for the widget".format("Template"))

        self.name = name
        self.title = title
        self.type = template

        if widgetid is None:
            self.id = generate_id(self.name)
        else:
            self.id = widgetid


    def to_json(self):
        return json.dumps(self.__dict__)



