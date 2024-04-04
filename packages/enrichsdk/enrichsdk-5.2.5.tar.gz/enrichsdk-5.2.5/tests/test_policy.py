import os
import json
import pytest
import tempfile
import shutil
from enrichsdk.package.mock import *
from enrichsdk.policy import *
from enrichsdk.policy.sdk import *
from enrichsdk.lib import Context

invalid_policies = [
    (None, "Invalid specification format"),
    ({}, "Missing policy specification"),
    ({"args": {}}, "Missing policy specification"),
    ({"args": {"policies": {}}}, "Policy specification must be a list"),
    ({"args": {"policies": []}}, "Empty list of policies"),
    ({"args": {"policies": [{}]}}, "Invalid specification"),
    ({"args": {"policies": [{"principal": None}]}}, "Invalid specification"),
    ({"args": {"policies": [{"principal": ""}]}}, "Invalid specification"),
    ({"args": {"policies": [{"principal": "username"}]}}, "Invalid specification"),
    (
        {"args": {"policies": [{"principal": "username", "resource": None}]}},
        "Invalid specification",
    ),
    (
        {"args": {"policies": [{"principal": "username", "resource": "hello"}]}},
        "Invalid specification",
    ),
    (
        {
            "args": {
                "policies": [
                    {"principal": "username", "resource": "hello", "action": None}
                ]
            }
        },
        "Invalid specification",
    ),
    (
        {
            "args": {
                "policies": [
                    {
                        "principal": "username",
                        "resource": "hello",
                        "action": "hello",  # Invalid
                    }
                ]
            }
        },
        "Invalid action",
    ),
    (
        {
            "args": {
                "policies": [
                    {
                        "principal": "username",
                        "resource": "hello",
                        "action": "filter",
                        "args": None,
                    }
                ]
            }
        },
        "Invalid specification",
    ),
]

valid_policies = [
    {
        "args": {
            "policies": [
                {
                    "principal": "username:hello",
                    "resource": "confname::runname",
                    "action": "filter",
                    "args": {
                        "handler": "by_column_value",
                        "params": {"column": "storeid", "value": "attr::storeid"},
                    },
                }
            ]
        }
    }
]

invalid_principals = [
    ((None, None, None), "Invalid identifier specification"),
    (("", None, None), "Invalid identifier specification"),
    (([], None, None), "Invalid identifier specification"),
    (([1], None, None), "Invalid identifier specification"),
    (([None], None, None), "Invalid identifier specification"),
    ((["alpha"], None, None), "Invalid role specification"),
    ((["alpha"], "", None), "Invalid role specification"),
    ((["alpha"], {}, None), "Invalid role specification"),
    ((["alpha"], {1: 1}, None), "Invalid role specification"),
    ((["alpha"], {"a": 1}, None), "Invalid role specification"),
    ((["alpha"], {"a": ["B"]}, None), "Invalid attribute specification"),
    ((["alpha"], {"a": ["B"]}, ""), "Invalid attribute specification"),
    ((["alpha"], {"a": ["b"]}, {}), "Invalid attribute specification"),
    ((["alpha"], {"a": ["b"]}, {1: 1}), "Invalid attribute specification"),
]

invalid_resources = [None, ""]


resources = [BaseResource("alpha"), BaseResource("beta")]

principals = [
    BasePrincipal(
        identifiers=[
            "username:bob",
        ],
        roles={"marketing": ["admin"]},
        attrs={"storeid": 25},
    )
]

accesses = [
    {
        "principal": {
            "identifiers": ["username:hello"],
            "roles": {"marketing": ["admin"]},
            "attrs": {"storeid": 24},
        },
        "resource": {
            "name": "alpha",
        },
        "status": "deny",
    },
    {
        "principal": {
            "identifiers": ["username:hello"],
            "roles": {"marketing": ["admin"]},
            "attrs": {"storeid": 24},
        },
        "resource": {
            "name": "confname::runname",
        },
        "status": "filter",
    },
]


class TestPolicy(object):
    """
    Test the policy implementation
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

    @pytest.mark.parametrize("prefix", invalid_resources)
    def test_invalid_resource(self, prefix):
        """
        Test invalid resources
        """
        with pytest.raises(Exception) as excinfo:
            b = BaseResource(prefix)

    @pytest.mark.parametrize("args,error", invalid_principals)
    def test_invalid_principal(self, args, error):
        """
        Test invalid principal
        """
        with pytest.raises(Exception) as excinfo:
            b = BasePrincipal(*args)

        assert error in str(excinfo)

    @pytest.mark.parametrize("conf,error", invalid_policies)
    def test_policy_invalid_configs(self, conf, error):
        """
        Test invalid policy configurations
        """
        with pytest.raises(Exception) as excinfo:
            policy = SimpleFilterEngine(config=self.config)
            policy.configure(conf)
            policy.validate()

        assert error in str(excinfo)

    def test_policy_valid_configs(self):
        """
        Test Valid configuration
        """
        # => Load the policy
        policy = SimpleFilterEngine(config=self.config)
        policy.configure(valid_policies[0])
        policy.validate()

    @pytest.mark.parametrize("params", accesses)
    def test_policy_execution(self, params):
        """
        Test implementation of the policy
        """

        principal = params["principal"]
        resource = params["resource"]
        status = params["status"]

        # Instantiate the policy engine
        conf = valid_policies[0]
        policy = SimpleFilterEngine(config=self.config)
        policy.configure(conf)

        # Create principal
        principal = BasePrincipal(**principal)

        # Construct resource
        resource = BaseResource(**resource)

        # Now apply the policy
        result = policy.apply(principal, resource)
        assert result["status"] == status
