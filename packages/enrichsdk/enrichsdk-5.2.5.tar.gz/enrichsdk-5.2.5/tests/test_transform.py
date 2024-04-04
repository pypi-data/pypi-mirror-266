import os
import json
import copy
import shutil
import imp
import tempfile
import pytest

from enrichsdk.package.mock import MockConfig, MockState
from enrichsdk.lib import Context

basic_configs = [
    {"conf": None, "exceptions": {"config": lambda e: "valid dictionary" in str(e)}},
    {"conf": "", "exceptions": {"config": lambda e: "valid dictionary" in str(e)}},
    {"conf": {}, "exceptions": {"config": lambda e: "valid dictionary" in str(e)}},
    {
        "conf": {},
        "exceptions": {
            "config": lambda e: "valid dictionary" in str(e),
        },
        "check": [lambda instance: instance.is_enabled()],
    },
    {
        "conf": {"version": 2.0},
        "exceptions": {"config": lambda e: "Version mismatch" in str(e)},
    },
    {
        "conf": {"args": {}},
        "exceptions": {"validation": lambda e: "Invalid name" in str(e)},
    },
]

node_configs = [
    {
        "conf": {"name": "Hello", "args": {}},
        "exceptions": {"validation": lambda e: "Invalid node type" in str(e)},
    }
]

compute_configs = [
    {
        "conf": {"name": "Hello", "dependencies": None, "args": {}},
        "exceptions": {"validation": lambda e: "Dependencies" in str(e)},
    },
]


class TestClass:
    """
    Test whether I can instantiate a module
    """

    @classmethod
    def setup_class(cls):
        cls.enrich_root = tempfile.mkdtemp()
        context = Context({"ENRICH_ROOT": cls.enrich_root})
        cls.config = MockConfig(context.asdict())
        cls.state = MockState(config=cls.config)

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls.enrich_root):
            shutil.rmtree(cls.enrich_root)

    def load_module(self, dirname):
        """
        Helper routine..
        """
        root = os.path.join(os.path.dirname(__file__), "fixtures", "transforms")
        modpath = os.path.join(root, dirname)

        modname = os.path.basename(modpath)
        dirname = os.path.dirname(modpath)

        file_, path_, desc_ = imp.find_module(modname, [dirname])
        package = imp.load_module(modname, file_, path_, desc_)

        return package.provider

    @pytest.mark.parametrize(
        "dirname, configs",
        [
            ("node_test", basic_configs + node_configs),
            ("compute_test", basic_configs + compute_configs),
            ("transform_test", basic_configs + compute_configs),
            ("model_test", basic_configs + compute_configs),
            ("skin_test", basic_configs + compute_configs),
        ],
    )
    def test_config(self, dirname, configs):
        """
        Test raw node
        """

        provider = self.load_module(dirname)

        with pytest.raises(Exception) as excinfo:
            cls = provider()

        # This should not raise an exception
        for c in configs:
            # print(c)
            exceptions = c.get("exceptions", {})
            instance = provider(config=self.config)

            # Configuration check
            check = exceptions.get("config", None)
            if check is not None:
                with pytest.raises(Exception) as excinfo:
                    instance.configure(c["conf"])
                # print("Received error", str(excinfo))
                assert check(excinfo)
                continue
            else:
                instance.configure(c["conf"])

            # => Validation step...
            check = exceptions.get("validation", None)
            if check:
                with pytest.raises(Exception) as excinfo:
                    instance.validate("conf", self.state)
                # print(excinfo)
                # print("Invalid name" in str(excinfo))
                assert check(excinfo)
            else:
                instance.validate("conf", self.state)

            # Run the checks on this node
            for check in c.get("checks", []):
                assert check(instance)

    def test_transform(self):
        """
        Test transform
        """
        provider = self.load_module("transform_test")
        conf = {"dependencies": None, "args": {}}

        t = provider(config=self.config)
        t.configure(conf)

        assert t.is_transform()
