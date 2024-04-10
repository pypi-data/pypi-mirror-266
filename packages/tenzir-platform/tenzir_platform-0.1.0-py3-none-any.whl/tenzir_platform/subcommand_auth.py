"""Usage: tenzir-platform auth login

Login command.
"""

from tenzir_platform.helpers.oidc import IdTokenClient
from tenzir_platform.helpers.environment import PlatformEnvironment
from docopt import docopt


def login(platform: PlatformEnvironment):
    token_client = IdTokenClient(platform)
    token = token_client.load_id_token()
    decoded_token = token_client.validate_token(token)
    print(f"Logged in as {decoded_token.user_id}")


def auth_subcommand(platform: PlatformEnvironment, argv):
    args = docopt(__doc__, argv=argv)
    if args["login"]:
        login(platform)
