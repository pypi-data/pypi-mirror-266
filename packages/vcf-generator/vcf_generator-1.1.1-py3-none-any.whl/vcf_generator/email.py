from dataclasses import dataclass


@dataclass
class Email:
    """Email Data class."""

    type: str
    address: str

    def __post_init__(self):
        self.type = self.type.upper()

    def __str__(self):
        return f"{self.type}: {self.address}"
