import httpx
import os
import json
from types import SimpleNamespace
from typing import NamedTuple, List, Union
from . import log
from .resource_abc import Resource, Ref

# import all resources here, so they are available in globals()
from .drive import FolderResource, FileResource  # noqa: F401
from .scheduler import ImageResource, JobResource, ScheduleResource  # noqa: F401
from .access import PolicyResource, RoleResource  # noqa: F401
from .identity import IdentityRoleResource, UserResource, RoleAssignment  # noqa: F401
from .configuration import SetResource, ItemResource # noqa: F401

Deployment = NamedTuple("Deployment", [("id", str), ("resources", List[Union[Resource, Ref]])])
deployments = []


def deployment(id, resources):
    d = Deployment(id, resources)
    deployments.append(d)


def recurse_resources(resources):
    seen = set()
    ordered = []

    def helper(items):
        for res in items:
            deps = res.deps()
            if len(deps) > 0:
                helper(deps)
            if res.id not in seen:
                seen.add(res.id)
                ordered.append(res)

    helper(resources)
    return ordered


def sort_deployed(entries):
    seen = set()
    ordered = []

    def helper(items):
        for e in items:
            dep_ids = e.dependencies
            if len(dep_ids) > 0:
                deps = [e for e in entries if e.resource_id in dep_ids]
                helper(deps)
            if e.resource_id not in seen:
                seen.add(e.resource_id)
                ordered.append(e)

    helper(entries)
    return ordered


# Throw an exception whenever the response code is 4xx or 5xx
def response_hook(response: httpx.Response) -> None:
    if response.is_error:
        response.read()
        response.raise_for_status()


def create_client(lusid_url: str, token: str) -> httpx.Client:
    if token is None or lusid_url is None:
        raise (
            RuntimeError(
                "Both FBN_ACCESS_TOKEN and LUSID_ENV variables need to be set"
            )
        )

    return httpx.Client(
        base_url=lusid_url,
        timeout=20,
        headers={
            "authorization": "Bearer " + os.getenv("FBN_ACCESS_TOKEN", default=""),
            "accept": "application/json",
            "content-type": "application/json",
        },
        event_hooks={"response": [response_hook]},
    )


def run(client: httpx.Client, deployment):
    resources = deployment.resources
    deploy_state = log.list_resources_for_deployment(client, deployment.id)
    all_resources = recurse_resources(resources)
    for resource in all_resources:
        if isinstance(resource, Ref):
            resource.attach(client)
            print("attach", type(resource).__name__)
            continue
        match = [e for e in deploy_state if e.resource_id == resource.id]
        if len(match) == 0:
            print("deploy: create", type(resource).__name__, resource.id)
            state = resource.create(client)
        else:
            print("deploy: update", type(resource).__name__, resource.id)
            state = resource.update(client, match[0].state)
        if state is not None:
            log.record(client, deployment.id, resource, state)
        else:
            print("deploy: nochange", type(resource).__name__, resource.id)
    for deployed in reversed(sort_deployed(deploy_state)):
        matching_resource = [e for e in all_resources if e.id == deployed.resource_id]
        if len(matching_resource) == 0:
            klas = globals()[deployed.resource_type]
            print("deploy: remove", deployed.resource_type, deployed.resource_id)
            klas.delete(client, deployed.state)
            log.remove(client, deployment.id, deployed.resource_id)

# called as a library
def deploy(deployment: Deployment, lusid_url: str, access_token: str):
    client = create_client(lusid_url, access_token)
    run(client, deployment)


def load_vars(vars_file):
    if vars_file:
        host_vars = SimpleNamespace(**json.load(vars_file))
    else:
        host_vars = SimpleNamespace()
    return host_vars
