import re


VALIDATION_PATTERN = re.compile(
    r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+[\._]?[a-z0-9]'
)


def validate_email_pattern(target_email: str) -> bool:
    output = re.match(VALIDATION_PATTERN, target_email)
    return isinstance(output, re.Match)
