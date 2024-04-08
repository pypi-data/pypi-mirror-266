"""Convert a list of contacts to a list of vCards."""

import fire

from vcf_generator import MIN_NUM_CONTACTS
from vcf_generator.contact import Contact
from vcf_generator.gen_contacts import gen_contact_instances


def serialize_contact(contact: Contact) -> str:
    """Serialize a contact to a vCard string."""
    vcard = [
        "BEGIN:VCARD",
        "VERSION:4.0",
        f"N:{contact.last_name};{contact.first_name};{contact.middle_name};;{contact.title}",
        f"FN:{contact.full_name}",
        f"TITLE:{contact.title}",
    ]
    if contact.phone_numbers:
        for i, phone in enumerate(contact.phone_numbers, start=1):
            vcard.append(
                f"TEL;TYPE#{phone.type},voice;VALUE#uri:tel:+{phone.country_code}-{phone.area_code}-{phone.subscriber_number}",
            )
    if contact.addresses:
        for i, address in enumerate(contact.addresses, start=1):
            vcard.append(
                f"ADR;TYPE#{address.type};PREF#{i};LABEL#{address.street}\n{address.city}, {address.state} {address.postal_code}\n{address.country}:;;{address.street};{address.city};{address.state};{address.postal_code};{address.country}",
            )
    if contact.birth_date:
        vcard.append(f"BDAY:{contact.birth_date}")
    if contact.emails:
        for email in contact.emails:
            vcard.append(f"EMAIL:{email.address}")
    vcard.append("END:VCARD")
    return "\n".join(vcard)


def serialize_contacts(contacts: list[Contact]) -> list[str]:
    """Serialize a list of contacts to a list of vCard strings."""
    return [serialize_contact(contact) for contact in contacts]


def gen_vcards_str(num_contacts: int = MIN_NUM_CONTACTS) -> list[str]:
    """Generate a list of vCards."""
    contacts = gen_contact_instances(num_contacts=num_contacts)
    return serialize_contacts(contacts=contacts)


def main(num_contacts: int = MIN_NUM_CONTACTS, output_file: str | None = None):
    """Generate a list of vCards and (optionally) write them to a file.

    Args:
        num_contacts (int, optional): Number of contacts to generate. Defaults to `MIN_NUM_CONTACTS`.
        output_file (str | None, optional): Output file path. Defaults to None.
    """
    vcards = gen_vcards_str(num_contacts=num_contacts)

    if output_file:
        try:
            with open(output_file, "w") as file:
                for vcard in vcards:
                    file.write(vcard + "\n")
        except FileNotFoundError:
            print(f"Error: {output_file} not found.")
    else:
        for vcard in vcards:
            print(vcard)


if __name__ == "__main__":
    fire.Fire(main)
