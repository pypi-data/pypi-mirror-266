import os
import json
import pytest


class TestImport(object):
    """
    Test imports of modules
    """

    @pytest.mark.parametrize(
        "cls",
        [
            ("Node"),
            ("Transform"),
            ("Skin"),
            ("Compute"),
            ("Integration"),
            ("NotificationIntegration"),
            ("DatabaseIntegration"),
            ("SearchSkin"),
            ("GenericSkin"),
        ],
    )
    def test_cls(self, cls):
        """
        Test each cls
        """

        stmt = "from enrichsdk import {0}".format(cls)
        exec(stmt)

    def test_cls_list(self):
        """
        Test whether Node is capturing all classes
        """

        from enrichsdk import Node

        print(Node.implementation_list())
