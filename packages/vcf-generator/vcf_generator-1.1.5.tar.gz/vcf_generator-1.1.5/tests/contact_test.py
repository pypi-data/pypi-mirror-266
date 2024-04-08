import pytest

from vcf_generator.address import Address
from vcf_generator.contact import Contact
from vcf_generator.email import Email
from vcf_generator.phone_number import PhoneNumber


# Define a fixture for a PhoneNumber instance
@pytest.fixture
def phone_number():
    return PhoneNumber("home", 1, 123, 4567890)


# Define a fixture for an Email instance
@pytest.fixture
def email():
    return Email("work", "test@example.com")


# Define a fixture for an Address instance
@pytest.fixture
def address():
    return Address(
        type="home",
        unit="1A",
        street="123 Main St",
        city="Anytown",
        state="Anystate",
        postal_code="12345",
        country="USA",
    )


# Define a fixture for a Contact instance
@pytest.fixture
def contact(phone_number, email, address):
    return Contact(
        first_name="John",
        middle_name=None,
        last_name="Doe",
        nickname=None,
        title=None,
        birth_date=None,
        notes=None,
        phone_numbers=[phone_number],
        emails=[email],
        addresses=[address],
    )


# Define a fixture for a Contact with all fields filled
@pytest.fixture
def contact_full_name():
    return Contact(
        first_name="John",
        middle_name="Nicholas",
        last_name="Doe",
        nickname="JD",
        title="Mr.",
        birth_date="1990-01-01",
        notes=None,
        phone_numbers=[
            PhoneNumber("home", 1, 123, 4567890),
            PhoneNumber("work", 1, 198, 7654321),
        ],
        emails=[
            Email(type="home", address="email@address.com"),
        ],
        addresses=[
            Address(
                type="home",
                unit=None,
                street="123 Main St",
                city="Anytown",
                state="Anystate",
                postal_code="12345",
                country="USA",
            ),
            Address(
                type="work",
                unit=None,
                street="456 Oak St",
                city="Othertown",
                state="Otherstate",
                postal_code="54321",
                country="USA",
            ),
        ],
    )


def test_contact_full_name(contact):
    assert contact.full_name == "John Doe"


def test_contact_full_name_w_middlename(contact_full_name):
    assert contact_full_name.full_name == "John Nicholas Doe"


def test_contact_phone_number(contact):
    assert str(contact.phone_numbers[0]) == "HOME: +1 (123) 456-7890"


def test_contact_email(contact):
    assert contact.emails[0].address == "test@example.com"


def test_contact_address(contact):
    assert (
        str(contact.addresses[0]) == "HOME: 123 Main St, 1A Anytown, Anystate 12345 USA"
    )


def test_contact_str(contact_full_name):
    expected_output = (
        "Name: John Nicholas Doe (JD) - Mr.\n"
        + "DOB: 1990-01-01\n"
        + "Phone Numbers: HOME: +1 (123) 456-7890. WORK: +1 (198) 765-4321\n"
        + "Emails: HOME: email@address.com\n"
        + "Addresses: HOME: 123 Main St, Anytown, Anystate 12345 USA. WORK: 456 Oak St, Othertown, Otherstate 54321 USA\n"
    )
    assert str(contact_full_name) == expected_output
