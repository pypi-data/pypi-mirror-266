"""
Policy firewall for the LLM Agent
"""
import os
import sys
import json
import traceback
import logging
from collections import Counter

logger = logging.getLogger(__file__)

class PolicyBase:

    def __init__(self, *args, **kwargs):
        self.name = "PolicyBase"
        self.description = "Dont use this. Only only the subclass"

    def evaluate(self, text):
        raise Exception("Implement the policy in baseclass")

class DummyPolicy(PolicyBase):
    """
    Do nothing policy
    """

    def __init__(self, *args, **kwargs):
        self.name = "DummyPolicy"
        self.description = "Check for nothing. Always returns success"

    def evaluate(self, text):
        return {
            "status": "success",
            "message": "Dummy policy"
        }

class DuhPolicy(PolicyBase):
    """
    Do nothing policy
    """

    def __init__(self, *args, **kwargs):
        self.name = "DuhPolicy"
        self.description = "Check for duh in evaluation text"

    def evaluate(self, text):
        return {
            "status": "success" if "duh" in text.lower() else "failure",
            "message": "Checks for Duh in the text"
        }


class PolicyManagerBase:
    """

    This has a collection of policysets each of which is a collection of
    policies.

    """
    def __init__(self):
        self.policysets = {}
        self.name = "PolicyManagerBase"

    def add_policy(self, policyset, name, policy):
        """
        """

        if policyset not in self.policysets:
            self.policysets[policyset] = {}

        if name in self.policysets[policyset]:
            logger.warning(f"Policy {name} already present in {policyset} policyset. Updating")

        self.policysets[policyset][name] = policy

    def evaluate(self, name, text):

        if name not in self.policysets:
            return {
                "status": "failure",
                "message": f"Unknown policyset {name}"

            }

        policymap = self.policysets[name]

        results = []
        for name, policy in policymap.items():
            try:
                result = policy.evaluate(text)
                if not isinstance(result, dict):
                    result = {
                        "status": "failure",
                        "message": "Invalid result from verifier",
                        "details": result
                    }
                elif 'status' not in result:
                    result['status'] = 'failure'
                    result['message'] = "Result status is unknown"
            except Exception as e:
                result = {
                    "status": "failure",
                    "message": "Invalid result from verifier",
                    "details":  traceback.format_exc()
                }
            results.append(result)

        if len(results) == 0 and False:
            return {
                "status": "failure",
                "message": "No policies found to evaluate"
            }

        statuses = Counter([r['status'] for r in results])

        if 'failure' in statuses:
            status = 'failure'
            message = "Failed with the following statues: "
            for k, c in statuses.items():
                message += f"{k} ({c}) "
        else:
            status = 'success'
            message = 'Passed all policy checks'

        return {
            'status': status,
            'message': message,
            'details': results
        }

class SimplePolicyManager(PolicyManagerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SimplePolicyManager"

if __name__ == "__main__":

    p = DummyPolicy()
    mgr = SimplePolicyManager()

    mgr.add_policy("default", "dummy", p)
    result = mgr.evaluate("default", "Check this dummy text")
    print(json.dumps(result, indent=4))

    mgr.add_policy("default", "duh", DuhPolicy())
    result = mgr.evaluate("default", "Check this dummy text")
    print(json.dumps(result, indent=4))

    result = mgr.evaluate("default", "Check this duh text")
    print(json.dumps(result, indent=4))
