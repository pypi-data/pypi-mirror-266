import pytest

from vcf_generator.address import Address
from vcf_generator.contact import Contact
from vcf_generator.email import Email
from vcf_generator.gen_vcards import (
    gen_vcards_str,
    serialize_contact,
    serialize_contacts,
)
from vcf_generator.phone_number import PhoneNumber


@pytest.fixture
def phone():
    return PhoneNumber(
        type="work",
        country_code="1",
        area_code="123",
        subscriber_number="4567890",
    )


@pytest.fixture
def email():
    return Email(address="test@example.com", type="work")


@pytest.fixture
def address():
    return Address(
        type="home",
        unit=None,
        street="123 Main St",
        city="Anytown",
        state="NY",
        postal_code="12345",
        country="USA",
    )


@pytest.fixture
def contact(phone, email, address):
    return Contact(
        first_name="John",
        last_name="Doe",
        middle_name="M",
        title="Mr",
        phone_numbers=[phone],
        addresses=[address],
        birth_date="1980-01-01",
        emails=[email],
        nickname=None,
        notes=None,
    )


@pytest.fixture
def contacts(contact, phone, email, address):
    contacts = [
        contact,
        Contact(
            first_name="Jane",
            last_name="Smith",
            middle_name="A",
            title="Ms",
            phone_numbers=[phone],
            addresses=[address],
            birth_date="1975-01-01",
            emails=[email],
            nickname=None,
            notes=None,
        ),
    ]
    return contacts


def test_serialize_contact(contact):
    vcard = serialize_contact(contact)
    assert "BEGIN:VCARD" in vcard
    assert "VERSION:4.0" in vcard
    assert "N:Doe;John;M;;Mr" in vcard
    assert "FN:John M Doe" in vcard
    assert "ORG:Mr Co." in vcard
    assert "TITLE:Mr" in vcard
    assert "TEL;TYPE#WORK,voice;VALUE#uri:tel:+1-123-4567890" in vcard
    assert (
        "ADR;TYPE#HOME;PREF#1;LABEL#123 Main St\nAnytown, NY 12345\nUSA:;;123 Main St;Anytown;NY;12345;USA"
        in vcard
    )
    assert "BDAY:1980-01-01" in vcard
    assert "EMAIL:test@example.com" in vcard
    assert "END:VCARD" in vcard


def test_serialize_contact_no_phone_no_address(contact):
    contact.phone_numbers = []
    contact.addresses = []
    vcard = serialize_contact(contact)
    assert "BEGIN:VCARD" in vcard
    assert "VERSION:4.0" in vcard
    assert "N:Doe;John;M;;Mr" in vcard
    assert "FN:John M Doe" in vcard
    assert "ORG:Mr Co." in vcard
    assert "TITLE:Mr" in vcard
    assert "BDAY:1980-01-01" in vcard
    assert "EMAIL:test@example.com" in vcard


def test_serialize_contacts(contacts):
    vcards = serialize_contacts(contacts)
    assert len(vcards) == 2
    for vcard in vcards:
        assert "BEGIN:VCARD" in vcard
        assert "VERSION:4.0" in vcard
        assert "N:" in vcard
        assert "FN:" in vcard
        assert "ORG:" in vcard
        assert "TITLE:" in vcard
        assert "TEL;TYPE#WORK,voice;VALUE#uri:tel:+1-123-4567890" in vcard
        assert (
            "ADR;TYPE#HOME;PREF#1;LABEL#123 Main St\nAnytown, NY 12345\nUSA:;;123 Main St;Anytown;NY;12345;USA"
            in vcard
        )
        assert "BDAY:" in vcard

    assert "FN:John M Doe" in vcards[0]
    assert "FN:Jane A Smith" in vcards[1]


def test_gen_vcards(contacts, monkeypatch):
    monkeypatch.setattr(
        "vcf_generator.gen_contacts.gen_contact_instances",
        lambda x: contacts,
    )

    vcards_str = gen_vcards_str(num_contacts=len(contacts))
    assert len(vcards_str) == len(contacts)
    for vcard in vcards_str:
        assert "BEGIN:VCARD" in vcard
        assert "VERSION:4.0" in vcard
        assert "N:" in vcard
        assert "FN:" in vcard
        assert "ORG:" in vcard
        assert "TITLE:" in vcard
        assert "BDAY:" in vcard
