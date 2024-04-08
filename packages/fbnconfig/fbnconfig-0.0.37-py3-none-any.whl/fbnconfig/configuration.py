from __future__ import annotations
import httpx
from .resource_abc import Resource, Ref
from pydantic import BaseModel, Field, computed_field
from enum import Enum
from typing import Dict, Any

class SetType(str, Enum):
    PERSONAL = "personal"
    SHARED = "shared"

class SetRef(BaseModel, Ref):
    """ Refer to an existing configuration set """
    id: str = Field(None, exclude=True, init=True)
    scope: str = Field(exclude=True, init=True)
    code: str = Field(exclude=True, init=True)
    type: SetType

    def attach(self, client):
        # just check it exists
        scope = self.scope
        code = self.code
        type = self.type.value
        try:
            client.get(f"/configuration/api/sets/{type}/{scope}/{code}").json()
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError(f"Config set {type}/{scope}/{code} not found")
            else:
                raise ex


class SetResource(BaseModel, Resource):
    """ Manage a configuration set """
    id: str = Field(None, exclude=True, init=True)
    scope: str = Field(exclude=True, init=True)
    code: str = Field(exclude=True, init=True)
    description: str
    type: SetType
    _remote: Dict[str, Any]|None = None

    @computed_field(alias="id")
    def setId(self) -> Dict[str, str]:
        return {"scope": self.scope, "code": self.code}

    def read(self, client, old_state):
        scope = self.scope
        code = self.code
        type = old_state.type
        get = client.get(f"/configuration/api/sets/{type}/{scope}/{code}")
        self._remote = get.json()

    def create(self, client: httpx.Client) -> Dict[str, Any]:
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        client.request("post", "/configuration/api/sets", json=desired)
        return {"scope": self.scope, "code": self.code, "type": self.type.value}

    @staticmethod
    def delete(client, old_state):
        type = old_state.type
        scope = old_state.scope
        code = old_state.code
        client.request("delete", f"/configuration/api/sets/{type}/{scope}/{code}")

    def update(self, client, old_state) -> Dict[str, Any]|None:
        if [old_state.scope, old_state.code, old_state.type] != [self.scope, self.code, self.type.value]:
            raise RuntimeError("Cannot change the scope, code or type on a config set")
        self.read(client, old_state)
        assert self._remote is not None
        current = {"description": self._remote["description"]}
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        desired.pop("id")
        desired.pop("type")
        if(desired == current):
            return None
        client.put(f"/configuration/api/sets/{self.type.value}/{self.scope}/{self.code}", json=desired)
        return {"scope": self.scope, "code": self.code, "type": self.type.value}

    def deps(self):
        return []

class ItemRef(BaseModel, Ref):
    """ Reference an existing configuration item with a set """
    id: str = Field(None, exclude=True, init=True)
    set: SetRef|SetResource
    key: str
    ref: str = Field(None, exclude=False, init=False)

    def attach(self, client):
        type = self.set.type.value
        scope = self.set.scope
        code = self.set.code
        key = self.key
        try:
            get = client.get(f"/configuration/api/sets/{type}/{scope}/{code}/items/{key}")
            self.ref = get.json()["ref"]
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 404:
                raise RuntimeError("Config item not found")
            else:
                raise ex

class ValueType(str, Enum):
    TEXT = "text"

class ItemResource(BaseModel, Resource):
    """ Manage a configuration item with a set """
    id: str = Field(None, exclude=True, init=True)
    set: SetRef|SetResource = Field(exclude=True, init=True)
    key: str
    ref: str = Field(None, exclude=False, init=False)
    value: Any
    valueType: ValueType
    isSecret: bool
    description: str
    _remote: Dict[str, Any] = {}

    def read(self, client, old_state):
        type = old_state.type
        scope = old_state.scope
        code = old_state.code
        key = old_state.key
        get = client.get(f"/configuration/api/sets/{type}/{scope}/{code}/items/{key}")
        self._remote = get.json()

    def create(self, client):
        desired = self.model_dump(mode="json", exclude_none=True)
        type = self.set.type.value
        scope = self.set.scope
        code = self.set.code
        post = client.post(
            f"/configuration/api/sets/{type}/{scope}/{code}/items",
            json=desired
        )
        match = next((item for item in post.json()["items"] if item["key"] == self.key), None)
        if match is None:
            raise RuntimeError("Something wrong creating config item")
        self.ref = match["ref"]
        return {"scope": scope, "code": code, "type": type, "key": self.key}

    @staticmethod
    def delete(client, old_state):
        type = old_state.type
        scope = old_state.scope
        code = old_state.code
        key = old_state.key
        client.delete(f"/configuration/api/sets/{type}/{scope}/{code}/items/{key}")

    def update(self, client, old_state):
        type = self.set.type.value
        scope = self.set.scope
        code = self.set.code
        key = self.key
        # if the location has changed we remove the old one
        if [old_state.scope, old_state.code, old_state.type] != [scope, code, type]:
            self.delete(client, old_state)
            return self.create(client)
        self.read(client, old_state)
        # can't update these using PUT
        if self.isSecret != self._remote["isSecret"] or self.valueType != self._remote["valueType"]:
            self.delete(client, old_state)
            return self.create(client)
        self.ref = self._remote["ref"]
        current = {k: v for k,v in self._remote.items() if k in ["description", "value"]}
        desired = self.model_dump(mode="json", exclude_none=True, by_alias=True)
        desired = {k: v for k,v in desired.items() if k in ["description", "value"]}
        if desired == current:
            return None
        client.put(f"/configuration/api/sets/{type}/{scope}/{code}/items/{key}", json=desired)
        return {"scope": scope, "code": code, "type": type, "key": self.key}

    def deps(self):
        return [self.set]
