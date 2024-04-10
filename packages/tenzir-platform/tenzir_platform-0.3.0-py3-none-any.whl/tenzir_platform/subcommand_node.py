"""Usage:
  tenzir-platform node list
  tenzir-platform node ping <node_id>
  tenzir-platform node create [--name=<node_name>]
  tenzir-platform node delete <node_id>
  tenzir-platform node run [--name=<node_name>] [--image=<container_image>]

Options:
  --name=<node_name>         The name of the newly created node [default: CLI_Node]
  --image=<container_image>  The docker image to use for the newly created node

Description:
  tenzir-platform node list
    Display a list of all nodes in the current workspace.

  tenzir-platform node ping
    Send a ping request to a node and measure the response time.

  tenzir-platform node run
    Create a new temporary node and run it in a local 'docker compose' stack.
    A new node is created in the currently selected workspace.
    The node is deleted when the command is interrupted.
    Requires the 'docker compose' binary in the current PATH.
"""

from tenzir_platform.helpers.cache import load_current_workspace
from tenzir_platform.helpers.client import AppClient
from tenzir_platform.helpers.environment import PlatformEnvironment
from pydantic import BaseModel
from docopt import docopt
from typing import Optional
import json
import time
import tempfile
import os
import subprocess
import re
import random
import datetime


def list(client: AppClient, workspace_id: str):
    resp = client.post(
        "/list-nodes",
        json={
            "tenant_id": workspace_id,
        },
    )
    resp.raise_for_status()
    for i, node in enumerate(resp.json()["nodes"]):
        connection_symbol = "🟢" if node["lifecycle_state"] == "connected" else "🔴"
        print(f"{connection_symbol} {node['name']} ({node['node_id']})")


def ping(client: AppClient, workspace_id: str, node_id: str):
    start = time.time()
    resp = client.post(
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


def run(
    client: AppClient, workspace_id: str, node_name: str, container_image: Optional[str]
):
    resp = client.post(
        "generate-client-config",
        json={
            "config_type": "docker",
            "tenant_id": workspace_id,
            "node_name": node_name,
        },
    )
    resp.raise_for_status()
    json = resp.json()
    node_id = json["node_id"]
    contents = json["contents"]

    # Hacky text replacement for using custom containers
    if container_image is not None:
        pattern = r"^(\s*image:) tenzir/tenzir.*$"
        replacement = r"\1 " + container_image
        contents = re.sub(pattern, replacement, contents, count=1, flags=re.MULTILINE)

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
                "tenant_id": workspace_id,
                "node_id": node_id,
            },
        )


def create(client: AppClient, workspace_id: str, node_name: Optional[str]):
    if node_name is None:
        time_suffix = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        node_name = f"node-{time_suffix}"
    resp = client.post(
        "/generate-client-config",
        json={
            "tenant_id": workspace_id,
            "config_type": "docker",
            "node_name": node_name,
        },
    )
    resp.raise_for_status()
    print(f"created node {resp.json()['node_id']}")


def delete(client: AppClient, workspace_id: str, node_id: str):
    resp = client.post(
        "/delete-node",
        json={
            "tenant_id": workspace_id,
            "node_id": node_id,
        },
    )
    resp.raise_for_status()
    print(f"deleted node {node_id}")


def node_subcommand(platform: PlatformEnvironment, argv):
    args = docopt(__doc__, argv=argv)
    try:
        workspace_id, user_key = load_current_workspace(platform)
        client = AppClient(platform=platform)
        client.workspace_login(user_key)
    except Exception as e:
        print(f"error: {e}")
        print(
            "Failed to load current workspace, please run 'tenzir-platform workspace select' first"
        )
        exit(1)

    if args["list"]:
        list(client, workspace_id)
    elif args["ping"]:
        node_id = args["<node_id>"]
        ping(client, workspace_id, node_id)
    elif args["run"]:
        node_name = args["--name"]
        container_image = args["--image"]
        run(client, workspace_id, node_name, container_image)
    elif args["create"]:
        node_name = args["--name"]
        create(client, workspace_id, node_name)
    elif args["delete"]:
        node_id = args["<node_id>"]
        delete(client, workspace_id, node_id)
