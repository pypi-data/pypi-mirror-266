from dataclasses import dataclass
from email.message import EmailMessage

__all__ = [
    "Message"
]


@dataclass
class Message:
    recipient: str
    subject: str
    content: str
    author: str

    def to_email_message(self) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self.author
        message["To"] = self.recipient
        message["Subject"] = self.subject
        message.set_content(self.content)
        return message

    def set_recipient(self, recipient: str):
        self.recipient = recipient
        return self
