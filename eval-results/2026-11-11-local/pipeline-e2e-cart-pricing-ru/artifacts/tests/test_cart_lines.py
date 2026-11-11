from decimal import Decimal

from shop.pricing import CartLine, subtotal


def test_subtotal_of_empty_cart_is_zero():
    assert subtotal([]) == Decimal("0.00")


def test_subtotal_multiplies_price_by_quantity(mug):
    lines = [CartLine(sku=mug.sku, price=mug.price, quantity=3)]

    result = subtotal(lines)

    assert result == Decimal("1350.00")
