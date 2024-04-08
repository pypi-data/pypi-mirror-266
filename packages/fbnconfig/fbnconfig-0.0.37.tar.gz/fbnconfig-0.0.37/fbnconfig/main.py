import click
import os
import functools
from .deploy import load_vars, create_client
from . import deploy
from . import log as deployment_log
from httpx import RequestError, HTTPStatusError
from json import dumps
from .load_module import load_module

help_footer = "environment defaults to $LUSID_ENV and token defaults to $FBN_ACCESS_TOKEN"

def http_exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RequestError as exc:
            msg = f"An error occurred while requesting {exc.request.url!r} before we got a response"
            raise click.ClickException(msg)
        except HTTPStatusError as exc:
            status = exc.response.status_code
            base_msg = " ".join([
                f"The server responded with {exc.response.status_code}",
                f"while requesting {exc.request.method} {exc.request.url!r}",
            ])
            if exc.response.is_server_error:
                detail = [ exc.response.text ]
            elif exc.response.json().get("name", "") == "AccessDenied":
                detail = [
                    exc.response.json().get("detail"),
                    exc.response.json().get("instance")
                ]
            elif status == 400:
                detail = [ exc.response.text ]
            else:
                detail = [ exc.response.text ]
            msg_str = "\n".join([base_msg] + detail)
            raise click.ClickException(msg_str)

    return wrapper

def runtime_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as exc:
            raise click.ClickException("Runtime Error: " + str(exc))

    return wrapper

@click.group()
@click.version_option(message="%(version)s")
def cli():
    pass


@cli.command(epilog=help_footer)
@click.option("-e", "--environment", type=str, envvar="LUSID_ENV")
@click.option("-t", "--access-token", type=str, envvar="FBN_ACCESS_TOKEN")
@click.pass_context
@http_exception_handler
@runtime_error_handler
def setup(ctx, environment, access_token):
    """ Perform initial setup of the environment """
    client = create_client(environment, access_token)
    deployment_log.setup(client)


@click.group()
def log():
    """Commands for interacting with the deployment log"""
    pass


@log.command(name="list", epilog=help_footer)
@click.argument("deployment", type=click.STRING, default=None, required=0)
@click.option("-e", "--environment", envvar="LUSID_ENV")
@click.option("-t", "--access-token", type=str, envvar="FBN_ACCESS_TOKEN")
@click.pass_context
@http_exception_handler
@runtime_error_handler
def list_deployments(ctx, deployment, environment, access_token):
    """List deployments.
    If no deployment id passed, returns all deployment ids ordered by last modified"""
    client = create_client(environment, access_token)
    if deployment:
        for line in deployment_log.list_resources_for_deployment(client, deployment_id=deployment):
            click.echo(deployment_log.format_log_line(line))
    else:
        for line in deployment_log.list_deployments(client):
            click.echo(f"   * {line}")


@log.command(epilog=help_footer)
@click.option("-e", "--environment", envvar="LUSID_ENV")
@click.option("-t", "--access-token", type=str, envvar="FBN_ACCESS_TOKEN")
@click.argument("deployment", type=click.STRING)
@click.argument("resource_id", type=click.STRING)
@click.pass_context
@http_exception_handler
@runtime_error_handler
def get(ctx, environment, access_token, deployment, resource_id):
    client = create_client(environment, access_token)
    for r in deployment_log.get_resource(client, deployment, resource_id):
        click.echo(f"    {r.resource_type}")
        click.echo(dumps(r.state.__dict__, indent=4))


@log.command(epilog=help_footer)
@click.option("-e", "--environment", envvar="LUSID_ENV")
@click.argument("deployment", type=click.STRING)
@click.argument("resource_id", type=click.STRING)
@click.option("-e", "--environment", type=str, envvar="LUSID_ENV")
@click.option("-t", "--access-token", type=str, envvar="FBN_ACCESS_TOKEN")
@click.pass_context
@http_exception_handler
@runtime_error_handler
def deps(ctx, deployment, resource_id, environment, access_token):
    client = create_client(environment, access_token)
    (index, dependencies) = deployment_log.get_dependencies_map(client, deployment)
    deployment_log.print_tree(index, dependencies, resource_id, "=>")


@log.command(epilog=help_footer)
@click.option("-e", "--environment", envvar="LUSID_ENV")
@click.argument("deployment", type=click.STRING)
@click.argument("resource_id", type=click.STRING)
@click.option("-e", "--environment", type=str, envvar="LUSID_ENV")
@click.option("-t", "--access-token", type=str, envvar="FBN_ACCESS_TOKEN")
@click.pass_context
@http_exception_handler
@runtime_error_handler
def depd(ctx, deployment, resource_id, environment, access_token):
    client = create_client(environment, access_token)
    (index, rdeps) = deployment_log.get_dependents_map(client, deployment)
    deployment_log.print_tree(index, rdeps, resource_id, "<=")


@log.command(epilog=help_footer)
@click.option("-e", "--environment", envvar="LUSID_ENV")
@click.argument("deployment", type=click.STRING)
@click.argument("resource_id", type=click.STRING)
@click.option("-f", "--force", is_flag=True, required=False, default=False, show_default=True,
              help="Remove the entry even if there are dependencies on given resource id")
@click.option("-r", "--recursive", is_flag=True, required=False, default=False, show_default=True,
              help="Remove the entry and any resources that  depend on it")
@click.option("-e", "--environment", type=str, envvar="LUSID_ENV")
@click.option("-t", "--access-token", type=str, envvar="FBN_ACCESS_TOKEN")
@click.pass_context
@http_exception_handler
@runtime_error_handler
def rm(ctx, deployment, resource_id, force, recursive, environment, access_token):
    client = create_client(environment, access_token)
    _, dependents = deployment_log.get_dependents_map(client, deployment)
    resource_depd = dependents.get(resource_id, None)
    if resource_depd and force is False:
        ctx.fail(f"   Cannot remove entry for '{resource_id}' as {resource_depd} depend on it")
    elif recursive is True and resource_depd:
        for id in resource_depd:
            deployment_log.remove(client, deployment, id)
        deployment_log.remove(client, deployment, resource_id)
        click.echo(
            f"   Removed entry for '{resource_id}' in deployment '{deployment}' "
            f"and its dependencies {dependents}")
    else:
        deployment_log.remove(client, deployment, resource_id)
        click.echo(f"   Removed entry for '{resource_id}' in deployment '{deployment}'")


cli.add_command(log)

@cli.command(epilog=help_footer)
@click.option("-e", "--environment", type=str, envvar="LUSID_ENV")
@click.option("-t", "--access-token", type=str, envvar="FBN_ACCESS_TOKEN")
@click.option("-v", "--vars_file", type=click.File("r"))
@click.argument("script_path", type=click.Path(readable=True))
@http_exception_handler
@click.pass_context
@runtime_error_handler
def run(ctx, script_path, environment, vars_file, access_token):
    """ Deploy the configuration

        Loads the configuration script from SCRIPT_PATH
        and runs against lusid.
        vars_file will be injected into the configure function
    """
    host_vars = load_vars(vars_file)
    try:
        module = load_module(script_path, os.path.basename(script_path))
        if getattr(module, "configure", None) is None:
            raise click.ClickException(
                f"Failed importing user config: [{script_path}]. Error : No configure function found"
            )

        d = module.configure(host_vars)
    except ImportError as e:
        raise click.ClickException(f"Failed importing user config: [{script_path}]. Error : \n{e}")
    deploy(d, environment, access_token)

if __name__ == "__main__":
    cli()
