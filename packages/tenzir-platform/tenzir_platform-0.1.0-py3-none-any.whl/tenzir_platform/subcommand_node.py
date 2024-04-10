"""Usage:
  tenzir-platform node list
  tenzir-platform node ping <node_id>
  tenzir-platform node run [--name=<node_name>]

Options:
  --name=<node_name>    The name of the newly created node [default: CLI_Node]

Description:
  tenzir-platform node list
    Display a list of all nodes in the current workspace.

  tenzir-platform node ping
    Send a ping request to a node and measure the response time.

  tenzir-platform node run
    Run a temporary node for local testing.
    A new node is created in the currently selected workspace and run using `docker compose`.
    The node is deleted when the command is interrupted.
    Requires a `docker compose` binary in the current PATH.
"""

from tenzir_platform.helpers.cache import load_current_workspace
from tenzir_platform.helpers.client import AppClient
from tenzir_platform.helpers.environment import PlatformEnvironment
from pydantic import BaseModel
from docopt import docopt
import json
import time
import tempfile
import os
import subprocess


class Workspace(BaseModel):
    workspace_id: str
    user_key: str


def list(platform: PlatformEnvironment, workspace: Workspace):
    app_cli = AppClient(platform=platform)
    app_cli.workspace_login(workspace.user_key)
    resp = app_cli.post(
        "/list-nodes",
        json={
            "tenant_id": workspace.workspace_id,
        },
    )
    resp.raise_for_status()
    for i, node in enumerate(resp.json()["nodes"]):
        connection_symbol = "🟢" if node["lifecycle_state"] == "connected" else "🔴"
        print(f"{connection_symbol} {node['name']} ({node['node_id']})")


def ping(platform: PlatformEnvironment, workspace: Workspace, node_id: str):
    app_cli = AppClient(platform=platform)
    app_cli.workspace_login(workspace.user_key)
    start = time.time()
    workspace_id = workspace.workspace_id
    resp = app_cli.post(
        "proxy",
        json={
            "node_id": node_id,
            "tenant_id": workspace_id,
            "http": {
                "path": "/ping",
                "method": "POST",
            },
        },
    )
    if resp.status_code == 410:
        print("node disconnected")
        return
    elif resp.status_code != 200:
        print(f"error {resp.status_code} after {time.time()-start}s")
        return
    print(f"response {resp.status_code} in {time.time()-start}s")


def run(platform: PlatformEnvironment, workspace: Workspace, node_name: str):
    client = AppClient(platform=platform)
    client.workspace_login(workspace.user_key)
    resp = client.post(
        "generate-client-config",
        json={
            "config_type": "docker",
            "tenant_id": workspace.workspace_id,
            "node_name": node_name,
        },
    )
    resp.raise_for_status()
    json = resp.json()
    node_id = json["node_id"]
    contents = json["contents"]

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w+")
    temp_file_name = temp_file.name
    temp_file.write(contents)
    temp_file.flush()

    try:
        print("running temporary Tenzir node")
        full_command = f"docker compose -f {temp_file_name} up"
        subprocess.run(full_command, shell=True, check=True)
    except KeyboardInterrupt:
        # Regular exit with CTRL-C
        pass
    except subprocess.CalledProcessError as e:
        print(f"Error running the docker compose command: {e}")
    finally:
        print("removing node and config file")
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
        client.post(
            "delete-node",
            json={
                "tenant_id": workspace.workspace_id,
                "node_id": node_id,
            },
        )


def node_subcommand(platform: PlatformEnvironment, argv):
    args = docopt(__doc__, argv=argv)
    try:
        workspace_id, user_key = load_current_workspace(platform)
        workspace = Workspace(workspace_id=workspace_id, user_key=user_key)
    except:
        print(
            "Failed to load current workspace, please run 'tenzir-platform workspace select' first"
        )
        exit(1)
    if args["list"]:
        list(platform, workspace)
    elif args["ping"]:
        node_id = args["<node_id>"]
        ping(platform, workspace, node_id)
    elif args["run"]:
        node_name = args["--name"]
        run(platform, workspace, node_name)
