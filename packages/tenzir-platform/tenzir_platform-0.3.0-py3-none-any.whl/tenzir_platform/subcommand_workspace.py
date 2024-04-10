"""
Usage:
  tenzir-platform workspace list
  tenzir-platform workspace select <workspace_id>
"""

from tenzir_platform.helpers.client import AppClient, TargetApi
from tenzir_platform.helpers.environment import PlatformEnvironment
from tenzir_platform.helpers.cache import store_workspace
from tenzir_platform.helpers.oidc import IdTokenClient
from docopt import docopt
import json


def list(platform: PlatformEnvironment):
    """Get list of authorized workspaces for the current CLI user"""
    id_token = IdTokenClient(platform).load_id_token()
    app_cli = AppClient(platform=platform)
    resp = app_cli.post(
        "get-login-info",
        json={
            "id_token": id_token,
        },
        target_api=TargetApi.USER_PUBLIC,
    )
    resp.raise_for_status()
    for i, workspace in enumerate(resp.json()["allowed_tenants"]):
        print(f"{workspace['tenant_id']} - {workspace['name']}")


def select(platform: PlatformEnvironment, workspace_id: str):
    """Log in to a tenant as the current CLI user"""
    id_token = IdTokenClient(platform).load_id_token()
    app_cli = AppClient(platform)
    resp = app_cli.post(
        "switch-tenant",
        json={
            "id_token": id_token,
            "tenant_id": workspace_id,
        },
        target_api=TargetApi.USER_PUBLIC,
    )
    resp.raise_for_status()
    user_key = resp.json()["user_key"]
    store_workspace(platform, workspace_id, user_key)
    print(f"Switched to workspace {workspace_id}")


def workspace_subcommand(platform: PlatformEnvironment, argv):
    args = docopt(__doc__, argv=argv)
    if args["list"]:
        list(platform)
    if args["select"]:
        workspace_id = args["<workspace_id>"]
        select(platform, workspace_id)
