import os
import tempfile

import pytest

from vcf_generator.address import Address
from vcf_generator.contact import Contact
from vcf_generator.email import Email
from vcf_generator.gen_contacts import (
    gen_address,
    gen_contact_instance,
    gen_contact_instances,
    gen_email,
    gen_phone_number,
    main,
)
from vcf_generator.phone_number import PhoneNumber


@pytest.fixture
def email():
    return gen_email()


@pytest.fixture
def phone_number():
    return gen_phone_number()


@pytest.fixture
def address():
    return gen_address()


@pytest.fixture
def contact():
    return gen_contact_instance()


@pytest.fixture
def contacts():
    return gen_contact_instances()


def test_gen_email(email):
    assert isinstance(email.address, str)
    assert email.type in ["PERSONAL", "WORK", "OTHER"]


def test_gen_phone_number(phone_number):
    assert isinstance(phone_number.type, str)
    assert phone_number.type in ["HOME", "WORK", "MOBILE", "OTHER"]
    assert isinstance(phone_number.country_code, int)
    assert isinstance(phone_number.area_code, int)
    assert isinstance(phone_number.subscriber_number, int)


def test_gen_address(address):
    assert isinstance(address.type, str)
    assert address.type in ["HOME", "WORK", "OTHER"]
    assert isinstance(address.unit, str)
    assert isinstance(address.street, str)
    assert isinstance(address.city, str)
    assert isinstance(address.state, str)
    assert isinstance(address.postal_code, str)
    assert isinstance(address.country, str)


def test_gen_contact(contact):
    assert isinstance(contact.first_name, str)
    assert isinstance(contact.middle_name, (str, type(None)))
    assert isinstance(contact.last_name, (str, type(None)))
    assert isinstance(contact.nickname, (str, type(None)))
    assert isinstance(contact.title, (str, type(None)))
    assert isinstance(contact.birth_date, str)
    assert isinstance(contact.notes, (str, type(None)))
    assert isinstance(contact.phone_numbers, list)
    assert all(isinstance(num, PhoneNumber) for num in contact.phone_numbers)
    assert isinstance(contact.emails, list)
    assert all(isinstance(email, Email) for email in contact.emails)
    assert isinstance(contact.addresses, list)
    assert all(isinstance(address, Address) for address in contact.addresses)


def test_gen_contacts(contacts):
    assert isinstance(contacts, list)
    assert all(isinstance(contact, Contact) for contact in contacts)


def test_main_without_output_file(contacts, capsys, monkeypatch):
    # Set the return value for gen_contact_instances called in main
    monkeypatch.setattr(
        "vcf_generator.gen_contacts.gen_contact_instances",
        lambda x: contacts,
    )
    # Call main without output file
    main(num_contacts=len(contacts), output_file=None)
    # Capture the standard output
    captured = capsys.readouterr()
    assert captured.out == "".join([str(contact) for contact in contacts])


def test_main_with_output_file(contacts, monkeypatch):
    expected_output_text = "".join([str(contact) for contact in contacts])

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        # Set the return value for gen_contact_instances called in main
        monkeypatch.setattr(
            "vcf_generator.gen_contacts.gen_contact_instances",
            lambda x: contacts,
        )
        # Call main with output file
        main(num_contacts=len(contacts), output_file=temp.name)
        # Read the output file and compare with expected output
        with open(temp.name) as f:
            file_contacts = f.readlines()
            # Convert list to string
            file_contacts = "".join(file_contacts)
            # Compare the output file with the expected output
            assert file_contacts == expected_output_text

        # Clean up: remove the temporary file
        # This causes an error in Windows, so we need to use a try-except block
        try:
            os.unlink(temp.name)
        except PermissionError:
            pass


def test_main_with_output_file_exception(contacts, capsys, monkeypatch):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        # Set the return value for gen_contact_instances called in main
        monkeypatch.setattr(
            "vcf_generator.gen_contacts.gen_contact_instances",
            lambda x: contacts,
        )
        # Set the output file to a directory path instead of a file path
        output_file = os.path.dirname(temp.name)
        # Call main with output file
        main(num_contacts=len(contacts), output_file=output_file)

        # Check if the error message was printed
        captured = capsys.readouterr()
        assert "Error writing to file" in captured.out

        try:
            # Clean up: remove the temporary file
            os.unlink(temp.name)
        except PermissionError:
            pass
