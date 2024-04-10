from pydantic_settings import BaseSettings


API_ENDPOINT = "https://rest.tenzir.app/production-v1/"
OIDC_ISSUER_URL = "https://tenzir.eu.auth0.com/"
OIDC_CLIENT_ID = "vzRh8grIVu1bwutvZbbpBDCOvSzN8AXh"
OIDC_AUDIENCE = "tenzir_cli"


class PlatformEnvironment(BaseSettings):
    # The remote API endpoint of the platform.
    api_endpoint: str = API_ENDPOINT

    # An arbitrary short string to identify this environment
    # in the local cache directory.
    stage_identifier: str = "prod"

    # TODO: Provide a new `/oidc-config` endpoint in the public platform api
    # to load these values dynamically.
    oidc_issuer_url: str = OIDC_ISSUER_URL
    oidc_client_id: str = OIDC_CLIENT_ID
    oidc_audience: str = OIDC_AUDIENCE

    @staticmethod
    def load():
        return PlatformEnvironment(
            _env_prefix="TENZIR_PLATFORM_CLI", _env_nested_delimiter="__"
        )
