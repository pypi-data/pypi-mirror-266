from vcf_generator.phone_number import PhoneNumber


def test_str():
    phone_number = PhoneNumber("cell", 1, 123, 4567890)
    assert str(phone_number) == "CELL: +1 (123) 456-7890"


def test_str_another():
    phone_number = PhoneNumber("work", 44, 20, 1234567)
    assert str(phone_number) == "WORK: +44 (20) 123-4567"
