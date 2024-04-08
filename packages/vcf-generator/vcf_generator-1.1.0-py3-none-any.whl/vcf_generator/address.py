from dataclasses import dataclass


@dataclass
class Address:
    """Address Data class."""

    type: str
    unit: str | None
    street: str
    city: str
    state: str
    postal_code: str
    country: str

    def __post_init__(self) -> None:
        """Capitalize the type of address."""
        self.type = self.type.upper()

    def __str__(self) -> str:
        return (
            f"{self.type}: "
            + f"{self.street}, "
            + (f"{self.unit} " if self.unit else "")
            + f"{self.city}, {self.state} "
            + f"{self.postal_code} "
            + f"{self.country}"
        )
