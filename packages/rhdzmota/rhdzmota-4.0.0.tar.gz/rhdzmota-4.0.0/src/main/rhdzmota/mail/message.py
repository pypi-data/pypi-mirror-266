from dataclasses import dataclass
from email.message import EmailMessage
from typing import Optional


__all__ = [
    "Message"
]


@dataclass
class Message:
    subject: str
    content: str
    author: str
    content_type: str
    include_html: Optional[str] = None

    @classmethod
    def content_plain_text(
            cls,
            subject: str,
            content: str,
            author: str,
            include_html: Optional[str] = None,
    ) -> 'Message':
        return cls(
            subject=subject,
            content=content,
            author=author,
            content_type="text/plain",
            include_html=include_html
        )

    @property
    def content_subtype(self) -> str:
        _, subtype = self.content_type.split("/")
        return subtype

    def to_email_message(self, *recipient: str) -> EmailMessage:
        message = EmailMessage()
        message["From"] = self.author
        message["To"] = ", ".join(recipient)
        message["Subject"] = self.subject
        message.set_content(self.content)
        if self.include_html:
            message.add_alternative(self.include_html, subtype="html")
        return message
