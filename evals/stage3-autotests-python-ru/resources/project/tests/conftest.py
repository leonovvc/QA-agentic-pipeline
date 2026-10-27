from decimal import Decimal

import pytest

from shop.pricing import CartLine


@pytest.fixture
def mug() -> CartLine:
    """A single cheap item; tests change its quantity."""
    return CartLine(sku="MUG-01", price=Decimal("450.00"), quantity=1)
