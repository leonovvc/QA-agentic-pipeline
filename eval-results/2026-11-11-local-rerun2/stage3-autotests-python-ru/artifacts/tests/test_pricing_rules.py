from decimal import Decimal

import pytest

from shop.pricing import CartLine, is_valid_quantity, member_discount, shipping_cost, subtotal


@pytest.mark.parametrize(
    "quantity, expected",
    [(0, False), (1, True), (20, True), (21, False)],
)
def test_quantity_is_valid_only_between_1_and_20(quantity, expected):
    """TC-UNIT-001: количество 0 и 21 недопустимо, 1 и 20 — допустимо."""
    assert is_valid_quantity(quantity) is expected, f"quantity={quantity}"


def test_subtotal_of_several_lines_sums_price_times_quantity():
    """TC-UNIT-002: сумма корзины из нескольких строк = сумма цена × количество."""
    lines = [
        CartLine(sku="MUG-01", price=Decimal("100.00"), quantity=2),
        CartLine(sku="PEN-02", price=Decimal("49.50"), quantity=3),
    ]

    result = subtotal(lines)

    assert result == Decimal("348.50")


def test_shipping_is_charged_below_free_threshold():
    """TC-UNIT-003: при сумме 4999,99 доставка платная — 300,00."""
    result = shipping_cost(Decimal("4999.99"))

    assert result == Decimal("300.00")


def test_shipping_is_free_exactly_at_threshold():
    """TC-UNIT-004: при сумме ровно 5000,00 доставка бесплатная (ТЗ п. 3: «от 5000 ₽»)."""
    result = shipping_cost(Decimal("5000.00"))

    assert result == Decimal("0.00"), "доставка при сумме ровно 5000,00 должна быть бесплатной"


@pytest.mark.parametrize(
    "order_subtotal, is_member, is_sale_period, expected",
    [
        pytest.param("3000.00", True, False, "150.00", id="R1-member-at-threshold"),
        pytest.param("3000.00", False, False, "0.00", id="R2-not-member"),
        pytest.param("2999.99", True, False, "0.00", id="R3-below-threshold"),
        pytest.param("3000.00", True, True, "0.00", id="R4-sale-period"),
    ],
)
def test_member_discount_applies_only_for_member_from_3000_outside_sale(
    order_subtotal, is_member, is_sale_period, expected
):
    """TC-UNIT-005: скидка участника 5% — только при сумме от 3000 вне распродажи."""
    result = member_discount(Decimal(order_subtotal), is_member, is_sale_period)

    assert result == Decimal(expected)
