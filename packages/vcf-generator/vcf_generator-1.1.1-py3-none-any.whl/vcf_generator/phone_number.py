"""Phone Number Data class."""

from dataclasses import dataclass


@dataclass
class PhoneNumber:
    """Phone Number Data class.

    We are using the North American Numbering Plan (NANP)
    for the phone numbers.
    """

    type: str
    country_code: int
    area_code: int
    subscriber_number: int

    def __post_init__(self) -> None:
        """Capitalize the type of phone number."""
        self.type = self.type.upper()

    def __str__(self) -> str:
        subscriber_number = str(self.subscriber_number)
        subscriber_number = subscriber_number[:3] + "-" + subscriber_number[3:]
        return (
            f"{self.type}: " + f"+{self.country_code} "
            f"({self.area_code}) "
            f"{subscriber_number}"
        )
