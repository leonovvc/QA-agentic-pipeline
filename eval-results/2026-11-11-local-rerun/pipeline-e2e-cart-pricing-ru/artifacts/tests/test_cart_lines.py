from decimal import Decimal

from shop.pricing import CartLine, subtotal


def test_subtotal_of_empty_cart_is_zero():
    assert subtotal([]) == Decimal("0.00")


def test_subtotal_multiplies_price_by_quantity(mug):
    lines = [CartLine(sku=mug.sku, price=mug.price, quantity=3)]

    result = subtotal(lines)

    assert result == Decimal("1350.00")


def test_tc_unit_003_subtotal_sums_price_times_quantity_across_lines(mug):
    """TC-UNIT-003: сумма нескольких строк = сумма «цена × количество»."""
    lines = [
        CartLine(sku=mug.sku, price=mug.price, quantity=3),
        CartLine(sku="PEN-02", price=Decimal("1200.50"), quantity=2),
    ]

    result = subtotal(lines)

    # 1350.00 + 2401.00
    assert result == Decimal("3751.00")


def test_tc_unit_004_duplicate_sku_lines_are_summed_as_separate_lines(mug):
    """TC-UNIT-004: один sku в двух строках суммируется как две строки (A4)."""
    line = CartLine(sku=mug.sku, price=mug.price, quantity=20)

    result = subtotal([line, line])

    assert result == Decimal("18000.00")
