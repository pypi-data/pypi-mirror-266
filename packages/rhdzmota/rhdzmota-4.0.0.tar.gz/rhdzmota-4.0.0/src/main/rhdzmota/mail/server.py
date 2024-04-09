import enum
import smtplib
from dataclasses import dataclass
from typing import Dict, Optional

from rhdzmota.mail.message import Message
from rhdzmota.settings import (
    EMAIL_SERVER_LOGIN_USER,
    EMAIL_SERVER_LOGIN_PASSWORD,
    logger_manager
)


logger = logger_manager.get_logger(name=__name__)


class EmailServerWrapper:
    singleton: Optional = None
    _server: Optional = None

    @staticmethod
    def _smtp_server_instance(
            host: str,
            port: int,
            **configs
    ):
        return smtplib.SMTP(host=host, port=port, **configs)

    def _smtp_server_instance_with_defaults(
            self,
            overwrite_host: Optional[str] = None,
            overwrite_port: Optional[int] = None,
            **overwrite_configs
    ):
        return self._smtp_server_instance(
            host=overwrite_host or self.host,
            port=overwrite_port or self.port,
            **(overwrite_configs or self.configs)
        )

    def __new__(cls, host: str, port: int, **configs):
        if cls.singleton is None:
            cls.singleton = super(EmailServerWrapper, cls).__new__(cls)
            cls.singleton._server = cls._smtp_server_instance(
                host=host,
                port=port,
                **configs
            )

        return cls.singleton

    def __init__(
            self,
            host: str,
            port: int,
            **configs
    ):
        self.host = host
        self.port = port
        self.configs = configs

    @classmethod
    def gmail(cls, **configs) -> 'EmailServerWrapper':
        return cls(
            host="smtp.gmail.com",
            port=587,
            **configs
        )

    def expired(self) -> bool:
        if not self._server:
            return False
        return self._server.sock is None

    def get_server(
            self,
            disable_tls: bool = False,
            overwrite_host: Optional[str] = None,
            overwrite_port: Optional[int] = None,
            **overwrite_configs,
    ) -> smtplib.SMTP:
        if self.expired():
            self._server = self._smtp_server_instance_with_defaults(
                overwrite_host=overwrite_host,
                overwrite_port=overwrite_port,
                **overwrite_configs
            )
            self._server.connect(
                host=overwrite_host or self.host,
                port=overwrite_port or self.port,
                **(overwrite_configs or self.configs),
            )
        self._server.ehlo()
        if self._server.has_extn("starttls") and not disable_tls:
            self._server.starttls()
        return self._server

    def login(
            self,
            user: Optional[str] = None,
            password: Optional[str] = None,
            disable_tls: bool = False,
            overwrite_host: Optional[str] = None,
            overwrite_port: Optional[int] = None,
            **overwrite_configs,
    ):
        user = user or EMAIL_SERVER_LOGIN_USER
        password = password or EMAIL_SERVER_LOGIN_PASSWORD
        if not all([user, password]):
            raise ValueError("Missing user and/or password for email server.")
        # Get validated server instance
        server_instance = self.get_server(
            disable_tls=disable_tls,
            overwrite_host=overwrite_host,
            overwrite_port=overwrite_port,
            **overwrite_configs,
        )
        # Loging to server via user/password
        server_instance.login(user=user, password=password)  # type: ignore
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            code, message = self._server.docmd("QUIT")
            if code != 221:
                raise smtplib.SMTPResponseException(code, message)
        except smtplib.SMTPServerDisconnected:
            return
        finally:
            self._server.close()

    def close(self):
        self._server.close()

    def send(
            self,
            *recipient: str,
            message: Message,
            disable_tls: bool = False,
            overwrite_host: Optional[str] = None,
            overwrite_port: Optional[int] = None,
            **overwrite_configs,
    ) -> Dict:
        # Get validated server instance
        server = self.get_server(
            diable_tls=disable_tls,
            overwrite_host=overwrite_host,
            overwrite_port=overwrite_port,
            **overwrite_configs,
        )
        # Get email message
        email_message = message.to_email_message(*recipient)
        return server.sendmail(
            from_addr=message.author,
            to_addrs=[
                *recipient,
            ],
            msg=email_message.as_string()
        )
