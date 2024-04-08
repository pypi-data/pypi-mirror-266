from typing import Dict, List, Optional
from rhdzmota.settings import logger_manager, get_environ_variable

logger = logger_manager.get_logger(name=__name__)

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    logger.error("Import error detected, try: pip install rhdzmota[google]")
    raise


def get_client_configs(
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        project_id: Optional[str] = None,
) -> Dict:
    return {
        "installed": {
            "client_id": client_id or get_environ_variable(
                name="GOOGLE_SERVICES_CONFIG_CLIENT_ID",
                enforce=True,
            ),
            "client_secret": client_secret or get_environ_variable(
                name="GOOGLE_SERVICES_CONFIG_CLIENT_SECRET",
                enforce=True,
            ),
            "project_id": project_id or get_environ_variable(
                name="GOOGLE_SERVICES_CONFIG_PROJECT_ID",
                enforce=True,
            ),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [
                "http://localhost"
            ]
        }
    }


def get_credentials_via_appflow(
        scopes: List[str],
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        project_id: Optional[str] = None,
        port: int = 0
) -> Credentials:
    flow = InstalledAppFlow.from_client_config(
        client_config=get_client_configs(
            client_id=client_id,
            client_secret=client_secret,
            project_id=project_id
        ),
        scopes=scopes
    )
    return flow.run_local_server(port=port)
