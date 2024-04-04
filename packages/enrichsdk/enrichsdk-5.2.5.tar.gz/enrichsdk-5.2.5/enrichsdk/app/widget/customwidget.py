from enrichsdk.app.widget.basewidget import BaseWidget
from enum import Enum

from enrichsdk.app.widget.customcomponent import BodyComponent, HeaderComponent


class CustomWidget():
    widgets = []

    def add_widget(self, widget):
        if widget:
            self.widgets.append(widget)

    def get_widgets(self):
        return self.widgets

    """ "name": f"Samples from {table_details.get('table')}",
                "description": persona.get('description'),
                "type": rendering_view,
                "results_count": widget_results,
                "structure": "flat",
                "columns": columns,
                "rows": [
                    v
                    for v in rows
                ],
                "search": search,
                "search_columns": search_columns,
                "body_components": body_components,
                "header_components": header_components,
                "td_class": "td-align-left td-width-200 wordwrap" """


class TableStructureType(str, Enum):
    FLAT = 'flat'
    S3 = 'S3'


class TableWidget(BaseWidget):
    def __init__(self, widgetid, name, title, template, description, result_count, table_structure, columns, rows):
        super().__init__(widgetid, name, title, template)
        self.rows = rows
        self.css_class = ''
        self.columns = columns
        self.type = table_structure
        self.result_count = result_count
        self.description = description
        self.search = None

    @property
    def css_class_attr(self):
        return self.css_class

    @css_class_attr.setter
    def css_class_attr(self, value):
        self.css_class = value

    def search_attr(self):
        return self.search

    def search_attr(self, value):
        self.search = value

    # @property
    # def search_columns_prop(self):
    #     return self.search_columns
    #
    # @search_columns_prop.setter
    # def search_columns_prop(self, value):
    #     self.search_columns = value

    """ "url": f"?persona={persona_name}&table={table}&query={querystr}&process=download",
        "id": "download",
        "label": "",
        "title": "Download All Matched Results",
        "alt": "",
        "class": "",
        "template": "action_icon",
        "icon": "download-blue-icon" """


class TextWidget(BaseWidget):
    def __init__(self, widgetid, name, title, template):
        super().__init__(widgetid, name, title, template)
        self.css_class = ''
        self.header_components = None
        self.body_components = None

    @property
    def css_class_attr(self):
        return self.css_class

    @css_class_attr.setter
    def css_class_attr(self, value):
        self.css_class = value

    def get_header_components(self):
        return self.header_components

    def set_header_components(self, value):
        if isinstance(value, HeaderComponent):
            self.header_components = value.get_components()

    def get_body_components(self):
        return self.body_components

    def set_body_components(self, value):
        if isinstance(value, BodyComponent):
            self.body_components = value.get_components()



class ActionItemWidget(BaseWidget):
    def __init__(self, widgetid, name, title, template):
        super().__init__(widgetid, name, title, template)
