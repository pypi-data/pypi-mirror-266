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


@dataclass
class ServerWrapper:
    host: str
    port: int
    instance: Optional[smtplib.SMTP] = None

    def expired(self) -> bool:
        if not self.instance:
            return False
        return self.instance.sock is None

    def get_server(self, disable_tls: bool = False, **configs) -> smtplib.SMTP:
        if self.instance is None or self.instance.sock is None:
            logger.info("Creating SMTP server instance...")
            self.instance = smtplib.SMTP(host=self.host, port=self.port, **configs)
        if self.expired():
            logger.info("Server connection expired, reconnecting...")
            self.instance.connect(host=self.host, port=self.port, **configs)
        self.instance.ehlo()
        if self.instance.has_extn("starttls") and not disable_tls:
            self.instance.starttls()
        return self.instance

    def __call__(
            self,
            user: Optional[str] = None,
            password: Optional[str] = None,
            disable_tls: bool = False,
            **configs
    ):
        user = user or EMAIL_SERVER_LOGIN_USER
        password = password or EMAIL_SERVER_LOGIN_PASSWORD
        server_instance = self.get_server(disable_tls=disable_tls, **configs)
        logger.info("Logging to server...")
        server_instance.login(user=user, password=password)  # type: ignore
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.instance is None:
            return
        try:
            code, message = self.instance.docmd("QUIT")
            if code != 221:
                raise smtplib.SMTPResponseException(code, message)
        except smtplib.SMTPServerDisconnected:
            return
        finally:
            self.instance.close()

    def message(
            self,
            subject: str,
            content: str,
            recipient: str,
            author: str,
            send: bool = False,
    ) -> Message:
        message = Message(
            subject=subject,
            content=content,
            recipient=recipient,
            author=author,
        )
        if send:
            self.send(message=message)
        return message

    def send(
            self,
            message: Message,
            disable_tls: bool = False,
            **configs
    ) -> Dict:
        return self.get_server(disable_tls=disable_tls, **configs).sendmail(
            from_addr=message.author,
            to_addrs=[
                message.recipient,
            ],
            msg=message.to_email_message().as_string()
        )


class Server(enum.Enum):
    gmail = ServerWrapper(host="smtp.gmail.com", port=587)
