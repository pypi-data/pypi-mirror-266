import base64
import sys
import textwrap
from dataclasses import dataclass
from importlib.metadata import version
from os import environ, getenv
from pathlib import Path
from string import Template
from typing import Optional

import grpc
from flyteidl.service.identity_pb2 import UserInfoRequest
from flyteidl.service.identity_pb2_grpc import IdentityServiceStub
from flytekit.clients.auth_helper import get_authenticated_channel
from flytekit.configuration import AuthType, Config, ConfigFile, PlatformConfig, get_config_file
from flytekit.configuration.default_images import DefaultImages

_DEFAULT_GCP_SERVERLESS_ENDPOINT: str = "serverless-1.us-east-2.s.union.ai"

# Temporary mapping until mutating webhooks are in place.
_SERVERLESS_ENDPOINT_TO_REGISTRY = {
    "serverless-gcp.cloud-staging.union.ai": "us-central1-docker.pkg.dev/serverless-gcp-dataplane",
    "utt-srv-staging-1.cloud-staging.union.ai": "us-central1-docker.pkg.dev/serverless-gcp-dataplane",
    "serverless-preview.canary.unionai.cloud": "us-central1-docker.pkg.dev/uc-serverless-canary",
    "utt-srv-canary-1.canary.unionai.cloud": "us-central1-docker.pkg.dev/uc-serverless-canary",
    "serverless-1.us-east-2.s.union.ai": "us-central1-docker.pkg.dev/uc-serverless-production",
}

_UNIONAI_CONFIG_ENV_VAR: str = "UNIONAI_CONFIG"
_UNIONAI_SERVERLESS_ENDPOINT_ENV_VAR: str = "UNIONAI_SERVERLESS_ENDPOINT"
_UNIONAI_SERVERLESS_API_KEY_ENV_VAR: str = "UNIONAI_SERVERLESS_API_KEY"
_UNIONAI_DEFAULT_CONFIG_DIR: Path = Path.home() / ".unionai"
_UNIONAI_CONFIG_NAME: str = "config.yaml"
_UNIONAI_DEFAULT_CONFIG_PATH: Path = _UNIONAI_DEFAULT_CONFIG_DIR / _UNIONAI_CONFIG_NAME


@dataclass
class _UnionAIConfig:
    serverless_endpoint: str = getenv(
        _UNIONAI_SERVERLESS_ENDPOINT_ENV_VAR,
        _DEFAULT_GCP_SERVERLESS_ENDPOINT,
    )
    org: Optional[str] = None
    config: Optional[str] = None
    is_direct_unionai_cli_call: bool = False


_UNIONAI_CONFIG = _UnionAIConfig()


def _is_serverless_endpoint(endpoint: str) -> str:
    """Check if endpoint is serverless."""
    serverless_endpoint = _UNIONAI_CONFIG.serverless_endpoint
    return (
        endpoint in (serverless_endpoint, f"dns:///{serverless_endpoint}")
        and endpoint in _SERVERLESS_ENDPOINT_TO_REGISTRY
    )


@dataclass
class AppClientCredentials:
    endpoint: str
    client_id: str
    client_secret: str
    org: str


def _encode_app_client_credentials(app_credentials: AppClientCredentials) -> str:
    """Encode app_credentials with base64."""
    data = (
        f"{app_credentials.endpoint}:{app_credentials.client_id}:{app_credentials.client_secret}:{app_credentials.org}"
    )
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def _decode_app_client_credentials(encoded_str: str) -> AppClientCredentials:
    """Decode encoded base64 string into app credentials."""
    endpoint, client_id, client_secret, org = base64.b64decode(encoded_str.encode("utf-8")).decode("utf-8").split(":")
    return AppClientCredentials(endpoint=endpoint, client_id=client_id, client_secret=client_secret, org=org)


def _get_config_obj(config: Optional[str] = None, default_to_serverless: bool = False) -> Config:
    """Get Config object."""
    if _UNIONAI_CONFIG.is_direct_unionai_cli_call or default_to_serverless:
        # CLI ran with `unionai` -> Config is _UNIONAI_CONFIG.config and the default is serverless
        if _UNIONAI_CONFIG.config is not None:
            cfg_file = ConfigFile(_UNIONAI_CONFIG.config)
        elif _UNIONAI_DEFAULT_CONFIG_PATH.exists():
            # Read config from file system
            cfg_file = ConfigFile(str(_UNIONAI_DEFAULT_CONFIG_PATH.absolute()))
        else:
            # Setting None here uses serverless
            cfg_file = None
    else:
        # CLI ran with `pyflyte`, use the same semantics as `pyflyte`.
        # If `get_config_file` returns None, then we go to serverless
        if config is None:
            cfg_file = get_config_file(_UNIONAI_CONFIG.config)
        else:
            cfg_file = get_config_file(config)

    if cfg_file is None:
        serverless_api_value = environ.get(_UNIONAI_SERVERLESS_API_KEY_ENV_VAR, "")
        config = Config.for_endpoint(endpoint=_UNIONAI_CONFIG.serverless_endpoint)

        if serverless_api_value == "":
            # Serverless clients points to the serverless endpoint by default.
            return config
        try:
            app_credentials = _decode_app_client_credentials(serverless_api_value)
        except Exception as e:
            raise ValueError(f"Unable to read {_UNIONAI_SERVERLESS_API_KEY_ENV_VAR}") from e

        if _UNIONAI_CONFIG.org is None and app_credentials.org != "":
            _UNIONAI_CONFIG.org = app_credentials.org

        return config.with_params(
            platform=PlatformConfig(
                endpoint=app_credentials.endpoint,
                insecure=False,
                auth_mode=AuthType.CLIENTSECRET,
                client_id=app_credentials.client_id,
                client_credentials_secret=app_credentials.client_secret,
            )
        )
    else:
        # Allow for --config to still be passed in for Managed+ users.
        return Config.auto(cfg_file)


def _get_organization(platform_config: PlatformConfig, channel: Optional[grpc.Channel] = None) -> str:
    """Get organization based on endpoint."""
    if _UNIONAI_CONFIG.org is not None:
        return _UNIONAI_CONFIG.org
    elif _is_serverless_endpoint(platform_config.endpoint):
        org = _get_user_handle(platform_config, channel)
        _UNIONAI_CONFIG.org = org
        return org
    else:
        # Managed+ users, the org is not required for requests and we set it ""
        # to replicate default flytekit behavior.
        return ""


def _get_user_handle(platform_config: PlatformConfig, channel: Optional[grpc.Channel] = None) -> str:
    """Get user_handle for PlatformConfig."""
    if channel is None:
        channel = get_authenticated_channel(platform_config)

    client = IdentityServiceStub(channel)
    user_info = client.UserInfo(UserInfoRequest())
    user_handle = user_info.additional_claims.fields["userhandle"]
    return user_handle.string_value


def _get_default_image() -> str:
    """Get default image version."""
    cfg_obj = _get_config_obj()

    # TODO: This is only temporary to support GCP endpoints. When the unionai images are public,
    # we will always use unionai images
    endpoint = cfg_obj.platform.endpoint
    if _is_serverless_endpoint(endpoint):
        major, minor = sys.version_info.major, sys.version_info.minor
        unionai_version = version("unionai")
        if "dev" in unionai_version:
            suffix = "latest"
        else:
            suffix = unionai_version

        return f"{_SERVERLESS_ENDPOINT_TO_REGISTRY[endpoint]}/union/unionai:py{major}.{minor}-{suffix}"

    return DefaultImages().find_image_for()


def _write_config_to_path(endpoint: str, auth_type: str, config_dir: Path = _UNIONAI_DEFAULT_CONFIG_DIR):
    """Write config to config directory."""
    config_dir.mkdir(exist_ok=True, parents=True)

    config_template = Template(
        textwrap.dedent(
            """\
    admin:
      endpoint: $endpoint
      insecure: false
      authType: $auth_type
    logger:
      show-source: true
      level: 0
    union:
      connection:
        host: $endpoint
        insecure: false
      auth:
        type: $auth_type
    """
        )
    )
    config_path = config_dir / _UNIONAI_CONFIG_NAME
    config_path.write_text(config_template.substitute(endpoint=endpoint, auth_type=auth_type))

    return config_path


def _get_default_project(previous_default: str):
    cfg_obj = _get_config_obj()
    if _is_serverless_endpoint(cfg_obj.platform.endpoint):
        return "default"
    return previous_default


def _get_auth_success_html(endpoint: str) -> str:
    """Get default success html. Return None to use flytekit's default success html."""
    if endpoint.endswith("union.ai") or endpoint.endswith("unionai.cloud"):
        SUCCESS_HTML = textwrap.dedent(
            f"""
        <html>
        <head>
            <title>OAuth2 Authentication to Union Successful</title>
        </head>
        <body style="background:white;font-family:Arial">
            <div style="position: absolute;top:40%;left:50%;transform: translate(-50%, -50%);text-align:center;">
                <div style="margin:auto">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 65" fill="currentColor"
                        style="color:#fdb51e;width:360px;">
                        <title>Union.ai</title>
                        <path d="M32,64.8C14.4,64.8,0,51.5,0,34V3.6h17.6v41.3c0,1.9,1.1,3,3,3h23c1.9,0,3-1.1,3-3V3.6H64V34
                        C64,51.5,49.6,64.8,32,64.8z M69.9,30.9v30.4h17.6V20c0-1.9,1.1-3,3-3h23c1.9,0,3,1.1,3,3v41.3H134V30.9c0-17.5-14.4-30.8-32.1-30.8
                        S69.9,13.5,69.9,30.9z M236,30.9v30.4h17.6V20c0-1.9,1.1-3,3-3h23c1.9,0,3,1.1,3,3v41.3H300V30.9c0-17.5-14.4-30.8-32-30.8
                        S236,13.5,236,30.9L236,30.9z M230.1,32.4c0,18.2-14.2,32.5-32.2,32.5s-32-14.3-32-32.5s14-32.1,32-32.1S230.1,14.3,230.1,32.4
                        L230.1,32.4z M213.5,20.2c0-1.9-1.1-3-3-3h-24.8c-1.9,0-3,1.1-3,3v24.5c0,1.9,1.1,3,3,3h24.8c1.9,0,3-1.1,3-3V20.2z M158.9,3.6
                        h-17.6v57.8h17.6V3.6z"></path>
                    </svg>
                    <h2>You've successfully authenticated to Union!</h2>
                    <p style="font-size:20px;">Return to your terminal for next steps</p>
                </div>
            </div>
        </body>
        </html>
        """  # noqa
        )
        return SUCCESS_HTML
    return None
