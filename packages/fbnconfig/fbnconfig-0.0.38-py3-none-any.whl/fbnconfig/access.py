from __future__ import annotations
import httpx
import copy
from .resource_abc import Resource
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, field_serializer, model_validator, Field
from enum import Enum


class ActionId(BaseModel):
    """ActionId resource used with IdSelector

    Example
    -------
    >>> from fbnconfig.access import ActionId
    >>> ActionId(scope="myscope", activity="execute", entity="Feature")

    -------



    """
    scope: str
    activity: str
    entity: str


class IdSelector(BaseModel):
    """IdSelector resource used with PolicyResource

    Example
    -------
    >>> from fbnconfig.access import IdSelector, ActionId
    >>> IdSelector(
            name="feature_id_selector",
            description="feature_id_selector",
            identifier={"scope": "myscope", "code": "mycode"},
            actions=[ActionId(scope="myscope", activity="execute", entity="Feature")])
    """
    identifier: Dict[str, str]
    actions: List[ActionId]
    name: Optional[str] = None
    description: Optional[str] = None


class WhenSpec(BaseModel):
    """
    WhenSpec resource used with PolicyResource

    Example
    -------
    >>> from fbnconfig.access import WhenSpec
    >>>WhenSpec(activate="2024-08-31T18:00:00.0000000+00:00")

    Notes
    -------
    When deactivate is not supplied, the policy is valid from time in activate until end of time
    """
    activate: str
    deactivate: Optional[str] = None


class Grant(str, Enum):
    """Type of grant used with PolicyResource

    Available values are: Allow, Deny and Undefined
    """
    ALLOW = "Allow"
    DENY = "Deny"
    UNDEFINED = "Undefined"


# TODO: Needs scope added
class PolicyResource(BaseModel, Resource):
    """Manage a policy

    Attributes
    -------
    id: str
        Resource identifier
    """
    id: str = Field(exclude=True)
    code: str
    description: str
    applications: List[str]
    grant: Grant
    selectors: List[Dict[str, IdSelector]]  # we only handle idselectors so far
    when: WhenSpec
    remote: Dict[str, Any] = Field(
        {}, exclude=True, init=False
    )  # will store the current state of the policy

    def read(self, client, old_state):
        existing_policy = client.request("get", f"/access/api/policies/{self.code}")
        self.remote = (
            existing_policy.json()
        )  # post is just `code` but get is `id: {scope:..., code:...}` and put has no code in the body
        self.remote.pop("id")
        self.remote.pop("links")

    def create(self, client: httpx.Client):
        desired = self.model_dump(mode="json", exclude_none=True)
        client.request("POST", "/access/api/policies", json=desired)
        return {"id": self.id, "code": self.code}

    def update(self, client: httpx.Client, old_state):
        if old_state.code != self.code:
            raise (RuntimeError("Cannot change the code on a policy"))
        self.read(client, old_state)
        remote = copy.deepcopy(self.remote)
        desired = self.model_dump(mode="json", exclude_none=True, exclude={"code"})

        if (
            desired["when"].get("deactivate", None) is None
        ):  # deactivate is defaulted on the server so not a difference unless we set it
            remote["when"].pop("deactivate")
        if desired == remote:
            return None
        client.request("put", f"/access/api/policies/{self.code}", json=desired)
        return {"id": self.id, "code": self.code}

    @staticmethod
    def delete(client, old_state):
        client.request("DELETE", f"/access/api/policies/{old_state.code}")

    def deps(self):
        return []


class PolicyIdRoleResource(BaseModel):
    """Used to refer to a policy resource in a role resource
    """

    policies: Optional[List[PolicyResource]] = []
    policyCollections: Optional[List] = []  # no support for policy collections so far

    @field_serializer("policies", when_used="json")
    def serialize_identifiers(self, policies: List[PolicyResource]):
        # this takes a policy resource as a dep, but it only needs to send the identifiers
        return [{"code": p.code, "scope": "default"} for p in policies]


class Permission(str, Enum):
    """Permission type used on a role resource
    """
    READ = "Read"
    WRITE = "Write"
    EXECUTE = "Execute"


class RoleResource(BaseModel, Resource):
    """Define a role resource
    """
    id: str = Field(exclude=True)
    code: str
    description: Optional[str] = None
    policy_resource: PolicyIdRoleResource
    resource: Optional[Dict[str, Any]] = None
    when: WhenSpec
    permission: Permission
    roleHierarchyIndex: Optional[int] = None
    remote: Dict[str, Any] = Field(None, exclude=True, init=False)

    @model_validator(mode="before")
    @classmethod
    def extract_policy_ids(cls, options: Dict[str, Any]) -> Dict[str, Any]:
        pol = options["policy_resource"].policies
        options["resource"] = {
            "policyIdRoleResource": {"policies": [{"code": p.code, "scope": "default"} for p in pol]}
        }
        return options

    def read(self, client, old_state):
        get = client.request("get", f"/access/api/roles/{self.code}")
        self.remote = get.json()
        self.remote.pop("id")
        self.remote.pop("links")

    def create(self, client):
        body = self.model_dump(mode="json", exclude={"policy_resource"}, exclude_none=True)
        client.request("POST", "/access/api/roles", json=body)
        return {"id": self.id, "code": self.code}

    def update(self, client: httpx.Client, old_state):
        if old_state.code != self.code:
            raise (RuntimeError("Cannot change the code on a role"))
        self.read(client, old_state)
        remote = copy.deepcopy(self.remote)
        desired = self.model_dump(mode="json", exclude={"code", "policy_resource"}, exclude_none=True)
        remote["when"].pop(
            "deactivate"
        )  # deactivate is defaulted on the server so not a difference unless we set it
        remote.pop("roleHierarchyIndex")  # set by the server
        if desired == remote:
            return None
        client.request("put", f"/access/api/roles/{self.code}", json=desired)
        return {"id": self.id, "code": self.code}

    @staticmethod
    def delete(client, old_state):
        client.request("DELETE", f"/access/api/roles/{old_state.code}")

    def deps(self):
        if self.policy_resource is None or self.policy_resource.policies is None:
            return []
        return [value for value in self.policy_resource.policies]
