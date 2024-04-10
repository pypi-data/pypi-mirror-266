import hashlib
import os
import time

import jwt
import requests
from jwt import PyJWKClient
from typing import Optional, Any
from tenzir_platform.helpers.cache import filename_in_cache
from tenzir_platform.helpers.environment import PlatformEnvironment


class INVALID_API_KEY(Exception):
    pass


class ValidOidcToken:
    """The validated and decoded id_token.

    - Validate the presence of some claims required by the OIDC spec
    - Provide helper methods for checks"""

    def __init__(self, raw_oidc: dict[str, Any]) -> None:
        if "sub" not in raw_oidc or not isinstance(raw_oidc["sub"], str):
            raise INVALID_API_KEY("sub string required in OIDC token")
        self.user_id = raw_oidc["sub"]
        self._raw_oidc = raw_oidc

    def check_connection(self, connection: str) -> bool:
        return self.user_id.startswith(f"{connection}|")

    def get_claim_str(self, key: str, default: str) -> str:
        if key in self._raw_oidc and not isinstance(self._raw_oidc[key], str):
            raise INVALID_API_KEY(f"{key} is expected to be a string")
        return self._raw_oidc.get(key, default)

    @staticmethod
    def _is_list(val: Any) -> bool:
        return isinstance(val, list) and all(isinstance(x, str) for x in val)

    def get_claim_list(self, key: str, default: list[str]) -> list[str]:
        if key in self._raw_oidc and not ValidOidcToken._is_list(self._raw_oidc[key]):
            raise INVALID_API_KEY(f"{key} is expected to be a list of strings")
        return self._raw_oidc.get(key, default)

    def __str__(self) -> str:
        return self._raw_oidc.__str__()


class IdTokenClient:
    def __init__(self, platform: PlatformEnvironment):
        self.platform_environment = platform
        self.issuer = platform.oidc_issuer_url
        self.client_id = platform.oidc_client_id
        self.audience = platform.oidc_audience
        self.verbose = False

    def validate_token(self, id_token: str) -> ValidOidcToken:
        """Verify the token using the audience specific to the CLI"""
        jwks_url = f"{self.issuer.rstrip('/')}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        validated_token = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=self.issuer,
            # for id tokens, the audience is the client_id
            audience=self.client_id,
        )
        return ValidOidcToken(validated_token)

    def reauthenticate_token(self) -> str:
        # TODO: Add an option to use password flow for non-interactive environments.
        token_data = self._device_code_flow()
        return self._unwrap_flow_result(token_data)

    def _device_code_flow(self) -> dict[str, str]:
        device_code_payload = {
            "client_id": self.client_id,
            "scope": "openid email",
            # This points to an API audience in Auth0
            "audience": self.audience,
        }
        device_code_response = requests.post(
            f"{self.issuer.rstrip('/')}/oauth/device/code",
            data=device_code_payload,
        )

        if device_code_response.status_code != 200:
            raise Exception(f"Error generating the device code: {device_code_response.text}")

        device_code_data = device_code_response.json()
        print(
            "1. On your computer or mobile device navigate to: ",
            device_code_data["verification_uri_complete"],
        )
        print(
            "2. Verify you're seeing the following code and confirm: ",
            device_code_data["user_code"],
        )
        print("3. Wait up to 10 seconds")

        token_payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code_data["device_code"],
            "client_id": self.client_id,
        }
        authenticated = False
        while not authenticated:
            token_response = requests.post(
                f"{self.issuer.rstrip('/')}/oauth/token", data=token_payload
            )
            token_data = token_response.json()
            if token_response.status_code == 200:
                print("Authenticated!")
                break
            elif token_data["error"] not in ("authorization_pending", "slow_down"):
                print(token_data["error_description"])
                authenticated = True
            else:
                time.sleep(device_code_data["interval"])
        return token_data

    def _unwrap_flow_result(self, token_data: dict[str, str]) -> str:
        id_token = token_data["id_token"]
        current_user = self.validate_token(id_token)
        if self.verbose:
            print(f"obtained id_token: {current_user}")
        self._store_id_token(id_token)
        return id_token

    def _filename_in_cache(self):
        return filename_in_cache(self.platform_environment, "id_token")

    def _store_id_token(self, token: str):
        filename = self._filename_in_cache()
        print(f"saving token to {filename}")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(token)

    def load_id_token(self) -> str:
        filename = self._filename_in_cache()
        try:
            with open(filename, "r") as f:
                token = f.read()
            self.validate_token(token)
            return token
        except Exception:
            print("could not load valid token from cache, reauthenticating")
        return self.reauthenticate_token()
