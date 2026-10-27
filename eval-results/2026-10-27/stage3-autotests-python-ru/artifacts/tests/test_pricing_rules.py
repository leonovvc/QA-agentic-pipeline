from decimal import Decimal

import pytest

from shop.pricing import CartLine, is_valid_quantity, member_discount, shipping_cost, subtotal


@pytest.mark.parametrize(
    "quantity, expected",
    [(0, False), (1, True), (20, True), (21, False)],
)
def test_tc_unit_001_quantity_boundaries(quantity, expected):
    assert is_valid_quantity(quantity) is expected


def test_tc_unit_002_subtotal_of_several_lines_is_sum_of_price_times_quantity():
    lines = [
        CartLine(sku="A", price=Decimal("100.00"), quantity=2),
        CartLine(sku="B", price=Decimal("49.50"), quantity=3),
    ]

    assert subtotal(lines) == Decimal("348.50")


def test_tc_unit_003_shipping_is_paid_just_below_threshold():
    assert shipping_cost(Decimal("4999.99")) == Decimal("300.00")


def test_tc_unit_004_shipping_is_free_exactly_at_threshold():
    # ТЗ: «при сумме от 5000 ₽» — порог включительно
    assert shipping_cost(Decimal("5000.00")) == Decimal("0.00")


@pytest.mark.parametrize(
    "order_subtotal, is_member, is_sale, expected",
    [
        pytest.param("3000.00", True, False, "150.00", id="R1-member-at-threshold"),
        pytest.param("3000.00", False, False, "0.00", id="R2-not-member"),
        pytest.param("2999.99", True, False, "0.00", id="R3-below-threshold"),
        pytest.param("3000.00", True, True, "0.00", id="R4-sale-period"),
    ],
)
def test_tc_unit_005_member_discount_decision_table(order_subtotal, is_member, is_sale, expected):
    result = member_discount(Decimal(order_subtotal), is_member, is_sale)

    assert result == Decimal(expected)
