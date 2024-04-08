import base64
from typing import Dict, List, Optional

from rhdzmota.settings import logger_manager, get_environ_variable
from rhdzmota.mail.message import Message

logger = logger_manager.get_logger(name=__name__)

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    logger.error("Import error detected, try: pip install rhdzmota[google]")
    raise

from .auth import get_credentials_via_appflow  # noqa


GMAIL_DEFAULT_MESSAGE_AUTHOR = get_environ_variable(
    name="GMAIL_DEFAULT_MESSAGE_AUTHOR",
    default="me"
)


class GMail:
    DEFAULT_SCOPES = [
        "https://mail.google.com/"
    ]

    def __init__(
            self,
            creds: Credentials,
            gmail_service_name: Optional[str] = None,
            gmail_service_version: Optional[str] = None
    ):
        self.creds = creds
        self.service_name = gmail_service_name or get_environ_variable(
            name="GMAIL_SERVICE_NAME",
            default="gmail"
        )
        self.service_version = gmail_service_version or get_environ_variable(
            name="GMAIL_SERVICE_VERSION",
            default="v1"
        )
        self.service = build(
            self.service_name,
            version=self.service_version,
            credentials=self.creds
        )

    @classmethod
    def authenticate_via_appflow(
            cls,
            scopes: Optional[List[str]] = None,
            client_id: Optional[str] = None,
            client_secret: Optional[str] = None,
            project_id: Optional[str] = None,
            gmail_service_name: Optional[str] = None,
            gmail_service_version: Optional[str] = None
    ) -> 'GMail':
        if not scopes:
            logger.warning("Using the default scopes.")
            scopes = cls.DEFAULT_SCOPES
        return cls(
            creds=get_credentials_via_appflow(
                scopes=scopes,
                client_id=client_id,
                client_secret=client_secret,
                project_id=project_id,
            ),
            gmail_service_name=gmail_service_name,
            gmail_service_version=gmail_service_version,
        )

    def message(
            self,
            subject: str,
            content: str,
            recipient: str,
            author: Optional[str] = None,
            send: bool = False,
    ) -> Message:
        message = Message(
            subject=subject,
            content=content,
            recipient=recipient,
            author=author or GMAIL_DEFAULT_MESSAGE_AUTHOR,
        )
        if send:
            self.send(message=message)
        return message

    def send(
            self,
            message: Message,
    ) -> Dict:
        encoded_message = base64.urlsafe_b64encode(message.to_email_message().as_bytes()).decode()
        return self.service.users().messages().send(
            userId=message.author,
            body={
                "raw": encoded_message
            }
        ).execute()
