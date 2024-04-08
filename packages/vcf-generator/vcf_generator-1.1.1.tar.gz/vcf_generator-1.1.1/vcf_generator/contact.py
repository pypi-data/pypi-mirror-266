from dataclasses import dataclass, field

from vcf_generator.address import Address
from vcf_generator.email import Email
from vcf_generator.phone_number import PhoneNumber


@dataclass
class Contact:
    """Contact Data class."""

    first_name: str
    middle_name: str | None
    last_name: str | None
    nickname: str | None
    title: str | None
    birth_date: str | None
    notes: str | None
    phone_numbers: list[PhoneNumber] = field(default_factory=list)
    emails: list[Email] = field(default_factory=list)
    addresses: list[Address] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return (
            f"{self.first_name}"
            + (f" {self.middle_name}" if self.middle_name else "")
            + (f" {self.last_name}" if self.last_name else "")
        )

    def __str__(self) -> str:
        return (
            f"Name: {self.full_name}"
            + (f" ({self.nickname})" if self.nickname else "")
            + (f" - {self.title}" if self.title else "")
            + "\n"
            + (f"DOB: {self.birth_date}" if self.birth_date else "")
            + "\n"
            + (
                f"Phone Numbers: {'. '.join([str(p) for p in self.phone_numbers])}"
                if self.phone_numbers
                else ""
            )
            + "\n"
            + (
                f"Emails: {'. '.join([str(e) for e in self.emails])}"
                if self.emails
                else ""
            )
            + "\n"
            + (
                f"Addresses: {'. '.join([str(a) for a in self.addresses])}"
                if self.addresses
                else ""
            )
            + "\n"
        )
