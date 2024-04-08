"""This module generates contacts data by creating instances
of the Contact class with different field values."""

import fire
from faker import Faker

from vcf_generator import MIN_NUM_CONTACTS
from vcf_generator.address import Address
from vcf_generator.contact import Contact
from vcf_generator.email import Email
from vcf_generator.phone_number import PhoneNumber

fake = Faker()


def gen_email() -> Email:
    """Generate an random email."""
    email_type = fake.random_element(["personal", "work", "other"])
    return Email(address=fake.email(), type=email_type)


def gen_phone_number() -> PhoneNumber:
    """Generate a random phone number."""
    phone_type = fake.random_element(["home", "work", "mobile", "other"])
    # Generate 3 parts of Phone Number
    area_code = fake.random_int(min=100, max=999)
    subscriber_number = fake.random_int(min=1000000, max=9999999)
    country_code = fake.random_int(min=1, max=999)
    return PhoneNumber(
        type=phone_type,
        country_code=country_code,
        area_code=area_code,
        subscriber_number=subscriber_number,
    )


def gen_address() -> Address:
    """Generate a random address."""
    address_type = fake.random_element(["home", "work", "other"])
    return Address(
        type=address_type,
        unit=fake.building_number(),
        street=fake.street_address(),
        city=fake.city(),
        state=fake.state_abbr(),
        postal_code=fake.postcode(),
        country=fake.country(),
    )


def gen_contact_instance() -> Contact:
    """Generate a random contact."""
    num_phone_numbers = fake.random_int(min=1, max=3)
    num_emails = fake.random_int(min=1, max=3)
    num_addresses = fake.random_int(min=1, max=3)
    return Contact(
        first_name=fake.first_name(),
        middle_name=(
            fake.first_name() if fake.boolean(chance_of_getting_true=50) else None
        ),
        last_name=fake.last_name() if fake.boolean(chance_of_getting_true=50) else None,
        nickname=fake.first_name() if fake.boolean(chance_of_getting_true=50) else None,
        title=fake.prefix() if fake.boolean(chance_of_getting_true=50) else None,
        birth_date=str(fake.date_of_birth(minimum_age=18, maximum_age=80)),
        notes=fake.paragraph() if fake.boolean(chance_of_getting_true=50) else None,
        phone_numbers=[gen_phone_number() for _ in range(num_phone_numbers)],
        emails=[gen_email() for _ in range(num_emails)],
        addresses=[gen_address() for _ in range(num_addresses)],
    )


def gen_contact_instances(num_contacts: int = MIN_NUM_CONTACTS) -> list[Contact]:
    """Generate a list of random contacts."""
    return [gen_contact_instance() for _ in range(num_contacts)]


def main(num_contacts: int = MIN_NUM_CONTACTS, output_file: str | None = None):
    """Generate a list of random contacts and (optionally) write them to a file.

    Args:
        num_contacts (int, optional): Number of contacts to generate. Defaults
          to `MIN_NUM_CONTACTS`.
        output_file (str | None, optional): Output file path. Defaults to None.
    """
    contacts = gen_contact_instances(num_contacts)
    if output_file:
        try:
            with open(output_file, "w") as file:
                for contact in contacts:
                    file.write(str(contact))
        except Exception as e:
            print(f"Error writing to file: {e}")
    else:
        for contact in contacts:
            print(contact, end="")


if __name__ == "__main__":
    fire.Fire(main)
