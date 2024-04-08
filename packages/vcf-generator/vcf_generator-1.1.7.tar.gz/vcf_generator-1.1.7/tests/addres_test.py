import pytest

from vcf_generator.address import Address


@pytest.fixture
def address_with_unit():
    return Address(
        type="home",
        unit="1A",
        street="123 Main St",
        city="Anytown",
        state="Anystate",
        postal_code="12345",
        country="USA",
    )


@pytest.fixture
def address_without_unit():
    return Address(
        type="home",
        unit=None,
        street="123 Main St",
        city="Anytown",
        state="Anystate",
        postal_code="12345",
        country="USA",
    )


def test_post_init(address_with_unit):
    assert address_with_unit.type == "HOME"


def test_str_no_unit(address_without_unit):
    assert str(address_without_unit) == "HOME: 123 Main St, Anytown, Anystate 12345 USA"


def test_str_with_unit(address_with_unit):
    assert str(address_with_unit) == "HOME: 123 Main St, 1A Anytown, Anystate 12345 USA"
