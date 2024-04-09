import secrets
import string
from tempfile import NamedTemporaryFile
from typing import Optional


def get_random_string(
        length: int,
        case_sensitive: bool = False,
        include_digits: bool = False,
        include_special_characters: bool = False
) -> str:
    options = string.ascii_lowercase
    if case_sensitive:
        options += string.ascii_uppercase
    if include_digits:
        options += string.digits
    if include_special_characters:
        options += string.punctuation
    return "".join(secrets.choice(options) for _ in range(length))


def get_short_id():
    return get_random_string(
        length=5,
        case_sensitive=True,
        include_digits=True,
    )


def create_temporal_file(content: str, suffix: Optional[str] = None, path: Optional[str] = None) -> str:
    with NamedTemporaryFile(mode="r+", delete=False, dir=path, suffix=suffix) as file:
        file.write(content)
    return file.name
