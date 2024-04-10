"""Usage:
  tenzir-platform admin add-auth-rule [-d] email-domain <workspace_id> <connection> <domain>
  tenzir-platform admin add-auth-rule [-d] organization-membership <workspace_id> <connection> <organization_claim> <organization>
  tenzir-platform admin add-auth-rule [-d] organization-role <workspace_id> <connection> <roles_claim> <role> <organization_claim> <organization>
  tenzir-platform admin add-auth-rule [-d] user <workspace_id> <user_id>
  tenzir-platform admin delete-auth-rule <workspace_id> <auth_rule_index>
  tenzir-platform admin list-auth-rules <workspace_id>
  tenzir-platform admin create-workspace <owner_namespace> <owner_id> [--name=<workspace_name>]
  tenzir-platform admin delete-workspace <workspace_id>
  tenzir-platform admin list-global-workspaces

Options:
  -d,--dry-run             Do not add the rule, only print a JSON representation.
  --name=<workspace_name>  The name of the newly created workspace.
"""

from tenzir_platform.helpers.client import AppClient, TargetApi
from tenzir_platform.helpers.oidc import IdTokenClient
from tenzir_platform.helpers.environment import PlatformEnvironment
from tenzir_platform.helpers.auth_rule import (
    AuthRule,
    UserAuthRule,
    EmailDomainRule,
    RoleAndOrganizationRule,
    OrganizationMembershipRule,
)
from pydantic import BaseModel
from docopt import docopt


def add_auth_rule(client: AppClient, workspace_id: str, rule: AuthRule):
    resp = client.post(
        "add-auth-function",
        target_api=TargetApi.ADMIN,
        json={"tenant_id": workspace_id, "auth_rule": rule.model_dump()},
    )
    resp.raise_for_status()
    print(f"Added {rule.model_dump_json()}")


def delete_auth_rule(client: AppClient, workspace_id: str, index: int):
    resp = client.post(
        "delete-auth-function",
        target_api=TargetApi.ADMIN,
        json={"tenant_id": workspace_id, "index": index},
    )
    resp.raise_for_status()
    print(f"Deleted auth function {resp.json()} of {workspace_id}")


def list_auth_rules(client: AppClient, workspace_id: str):
    resp = client.get(
        "global-tenant-list",
        target_api=TargetApi.ADMIN,
    )
    resp.raise_for_status()
    for t in resp.json():
        if t["id"] == workspace_id:
            print(t["auth_functions"])


def create_workspace(client: AppClient, name: str, owner: str, owner_namespace: str):
    resp = client.post(
        "create-tenant",
        target_api=TargetApi.ADMIN,
        json={
            "owner": {
                "namespace": owner_namespace,
                "owner_id": owner,
            },
            "name": name,
        },
    )
    resp.raise_for_status()
    tenant_id = resp.json()["tenant_id"]
    print(f"Created workspace {tenant_id}")


def delete_workspace(client: AppClient, workspace_id: str):
    resp = client.post(
        "force-delete-tenant",
        target_api=TargetApi.ADMIN,
        json={
            "tenant_id": workspace_id,
        },
    )
    resp.raise_for_status()
    print(resp.json())


def list_global_workspaces(client: AppClient):
    resp = client.get(
        "global-tenant-list",
        target_api=TargetApi.ADMIN,
    )
    resp.raise_for_status()
    print(resp.json())


def auth_rule_from_arguments(arguments) -> AuthRule:
    connection = arguments["<connection>"]
    domain = arguments["<domain>"]
    user_id = arguments["<user_id>"]
    organization_claim = arguments["<organization_claim>"]
    organization = arguments["<organization>"]
    roles_claim = arguments["<roles_claim>"]
    role = arguments["<role>"]
    auth_rule: AuthRule
    if arguments["email-domain"]:
        auth_rule = EmailDomainRule(connection=connection, email_domain=domain)
    elif arguments["organization-membership"]:
        auth_rule = OrganizationMembershipRule(
            connection=connection,
            organization_claim=organization_claim,
            organization=organization,
        )
    elif arguments["organization-role"]:
        auth_rule = RoleAndOrganizationRule(
            connection=connection,
            roles_claim=roles_claim,
            role=role,
            organization_claim=organization_claim,
            organization=organization,
        )
    elif arguments["user"]:
        auth_rule = UserAuthRule(user_id=user_id)
    else:
        raise Exception("couldn't determine auth rule from command-line arguments")
    return auth_rule


def admin_subcommand(platform: PlatformEnvironment, argv):
    arguments = docopt(__doc__, argv=argv)

    def connect_and_login() -> AppClient:
        token_client = IdTokenClient(platform)
        token = token_client.load_id_token()
        client = AppClient(platform)
        client.user_login(token)
        return client

    if arguments["create-workspace"]:
        client = connect_and_login()
        owner_namespace = arguments["<owner_namespace>"]
        owner = arguments["<owner_id>"]
        name: str
        if arguments["--name"] is not None:
            name = arguments["--name"]
        else:
            name = f"{owner}'s Workspace"
        create_workspace(client, name, owner, owner_namespace)

    if arguments["delete-workspace"]:
        workspace_id = arguments["<workspace_id>"]
        client = connect_and_login()
        delete_workspace(client, workspace_id)

    if arguments["list-global-workspaces"]:
        client = connect_and_login()
        list_global_workspaces(client)

    if arguments["add-auth-rule"]:
        workspace_id = arguments["<workspace_id>"]
        dry_run = arguments["--dry-run"]
        auth_rule = auth_rule_from_arguments(arguments)
        if dry_run:
            print(f"Would add rule {auth_rule.model_dump_json()}")
        else:
            client = connect_and_login()
            add_auth_rule(client, workspace_id, auth_rule)

    if arguments["delete-auth-rule"]:
        workspace_id = arguments["<workspace_id>"]
        auth_fn_index: int = arguments["<auth_fn_index>"]
        client = connect_and_login()
        delete_auth_rule(client, workspace_id, auth_fn_index)

    if arguments["list-auth-rules"]:
        workspace_id = arguments["<workspace_id>"]
        client = connect_and_login()
        list_auth_rules(client, workspace_id)
