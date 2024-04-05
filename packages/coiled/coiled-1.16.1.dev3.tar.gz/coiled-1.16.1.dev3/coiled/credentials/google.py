import datetime
import json
import logging
import os
from typing import Tuple

from coiled.utils import supress_logs


class _FakeCredentialsBase:
    def __init__(self, *args, **kwargs): ...


try:
    from google.oauth2.credentials import Credentials as GoogleOAuth2Credentials
except ImportError:
    GoogleOAuth2Credentials = _FakeCredentialsBase


logger = logging.getLogger(__name__)


def get_gcp_local_session_token() -> dict:
    auth_logger = None
    comp_logger = None
    auth_logger_level = 0
    comp_logger_level = 0

    try:
        import google.auth
        from google.auth.transport.requests import Request

        with supress_logs(["google.auth._default", "google.auth.compute_engine._metadata"]):
            # get token from local auth
            local_creds, project = google.auth.default()
            local_creds.refresh(Request())

        return {
            "token": local_creds.token,
            "project": project,
            "expiry": local_creds.expiry.replace(tzinfo=datetime.timezone.utc),
        }
    except Exception as e:
        if "default credentials were not found" not in str(e):
            logger.warning(f"Error getting token from client GCP session: {e}")
    finally:
        if auth_logger:
            auth_logger.setLevel(auth_logger_level)
        if comp_logger:
            comp_logger.setLevel(comp_logger_level)

    return {}


def get_application_default_credentials():
    try:
        import google.auth
    except ImportError:
        raise ImportError(
            "Unable to retrieve Google Application Default Credentials because google-auth is not installed."
        ) from None
    local_creds, project = google.auth.default()

    return {
        "client_id": local_creds.client_id,
        "client_secret": local_creds.client_secret,
        "quota_project_id": local_creds.quota_project_id or project,
        "refresh_token": local_creds.refresh_token,
        "type": "authorized_user",
    }


def send_application_default_credentials(cluster):
    adf = get_application_default_credentials()
    adf_json = json.dumps(adf)

    project = adf["quota_project_id"]

    default_config = f"""[core]
project = {project}
"""

    gdal_env_vars = {
        "GS_OAUTH2_CLIENT_ID": adf["client_id"],
        "GS_OAUTH2_CLIENT_SECRET": adf["client_secret"],
        "GS_OAUTH2_REFRESH_TOKEN": adf["refresh_token"],
    }

    cluster.send_private_envs({
        "GOOGLE_CLOUD_PROJECT": project,
        **gdal_env_vars,
    })

    def write_adf_file():
        adc_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
        os.makedirs(os.path.dirname(adc_path), exist_ok=True)
        with open(adc_path, "w") as f:
            f.write(adf_json)

        config_path = os.path.expanduser("~/.config/gcloud/configurations/config_default")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            f.write(default_config)

    with cluster.get_client() as client:
        client.run_on_scheduler(write_adf_file)
        client.run(write_adf_file)

    print(
        "Google Application Default Credentials have been written to a file on your Coiled VM(s).\n"
        "These credentials will potentially be valid until explicitly revoked by running\n"
        "gcloud auth application-default revoke"
    )


class CoiledShippedCredentials(GoogleOAuth2Credentials):  # type: ignore
    def __init__(
        self,
        token=None,
        refresh_token=None,
        id_token=None,
        token_uri=None,
        client_id=None,
        client_secret=None,
        scopes=None,
        default_scopes=None,
        quota_project_id=None,
        expiry=None,
        rapt_token=None,
        refresh_handler=None,
        enable_reauth_refresh=False,
        granted_scopes=None,
    ):
        if GoogleOAuth2Credentials is _FakeCredentialsBase:
            raise ImportError("Unable to create Google Credentials object because google-cloud-iam is not installed.")

        env_token = self.get_shipped_token()
        if token and env_token and token != env_token:
            raise ValueError(
                "Specified Google OAuth2 token does not match "
                "token shipped by Coiled in CLOUDSDK_AUTH_ACCESS_TOKEN.\n"
                "We recommend not specifying a token and using the shipped token."
            )
        if token and not env_token:
            logger.warning(
                "Instantiating credentials with explicit token, no shipped token "
                "found in CLOUDSDK_AUTH_ACCESS_TOKEN. Refresh (which uses CLOUDSDK_AUTH_ACCESS_TOKEN) "
                "is unlikely to work."
            )

        super().__init__(token=env_token, refresh_handler=self.coiled_token_refresh_handler)

    @staticmethod
    def get_shipped_token():
        token = os.environ.get("CLOUDSDK_AUTH_ACCESS_TOKEN")

        if not token:
            # It's not the normal use-case, but Coiled can also set this env on local client machine
            # so that you can use `CoiledShippedCredentials` (with same OAuth2 token) locally and on cluster.
            token = os.environ.get("COILED_LOCAL_CLOUDSDK_AUTH_ACCESS_TOKEN")

        if not token:
            logger.warning("No Google OAuth2 token found, CLOUDSDK_AUTH_ACCESS_TOKEN env var not set")
        return token

    @staticmethod
    def get_token_expiry(token: str) -> datetime.datetime:
        import httpx

        result = httpx.get(f"https://oauth2.googleapis.com/tokeninfo?access_token={token}")
        data = result.json()
        timestamp = int(data["exp"])
        # note that refresh_handler is expected to return naive utc datetime
        expiry = datetime.datetime.utcfromtimestamp(timestamp)
        return expiry

    def coiled_token_refresh_handler(self, request, scopes) -> Tuple[str, datetime.datetime]:
        # this relies on other Coiled mechanisms to have already shipped a non-expired token to the cluster
        token = self.get_shipped_token()

        if not token:
            from google.auth.exceptions import RefreshError

            raise RefreshError(
                "Coiled was unable to find Google OAuth2 token on the cluster. "
                "See https://docs.coiled.io/user_guide/remote-data-access.html#gcp for details about shipping "
                "OAuth2 tokens from the client to the cluster."
            )

        expiry = self.get_token_expiry(token)

        logger.info(f"CoiledShippedCredentials have been refreshed, new expiration is {expiry}")

        return token, expiry
