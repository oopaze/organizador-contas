import re

OPEN_BILL_RE = re.compile(r"^Fatura (.+?) (\d{2})/(\d{4})$")


def parse_open_bill_identifier(identifier: str) -> tuple[str, int, int] | None:
    if not identifier:
        return None
    match = OPEN_BILL_RE.match(identifier.strip())
    if match is None:
        return None
    name, month, year = match.groups()
    return name.strip(), int(month), int(year)
