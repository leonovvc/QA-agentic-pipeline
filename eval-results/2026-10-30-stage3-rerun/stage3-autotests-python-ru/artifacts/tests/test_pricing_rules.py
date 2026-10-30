# Кейсы: docs/qa/pricing/test-cases-unit.md (задача pricing)
from decimal import Decimal

import pytest

from shop.pricing import CartLine, is_valid_quantity, member_discount, shipping_cost, subtotal


@pytest.mark.parametrize(
    ("quantity", "expected"),
    [(0, False), (1, True), (20, True), (21, False)],
)
def test_tc_unit_001_quantity_valid_only_from_1_to_20(quantity, expected):
    """TC-UNIT-001: количество 0 и 21 недопустимо, 1 и 20 — допустимо."""
    assert is_valid_quantity(quantity) is expected, f"количество {quantity}: ожидалось {expected}"


def test_tc_unit_002_subtotal_sums_price_times_quantity_over_lines():
    """TC-UNIT-002: сумма корзины из нескольких строк = сумма цена × количество."""
    lines = [
        CartLine(sku="MUG-01", price=Decimal("100.00"), quantity=2),
        CartLine(sku="CUP-02", price=Decimal("49.50"), quantity=3),
    ]

    result = subtotal(lines)

    assert result == Decimal("348.50")


def test_tc_unit_003_shipping_is_paid_just_below_threshold():
    """TC-UNIT-003: при сумме 4999,99 доставка платная — 300,00."""
    assert shipping_cost(Decimal("4999.99")) == Decimal("300.00")


def test_tc_unit_004_shipping_is_free_exactly_at_threshold():
    """TC-UNIT-004: при сумме ровно 5000,00 доставка бесплатная (REQ-3: «от 5000»)."""
    result = shipping_cost(Decimal("5000.00"))

    assert result == Decimal("0.00"), "порог 5000,00 включительно: доставка должна быть бесплатной"


@pytest.mark.parametrize(
    ("case", "order_subtotal", "is_member", "is_sale", "expected"),
    [
        ("R1", "3000.00", True, False, "150.00"),
        ("R2", "3000.00", False, False, "0.00"),
        ("R3", "2999.99", True, False, "0.00"),
        ("R4", "3000.00", True, True, "0.00"),
    ],
)
def test_tc_unit_005_member_discount_decision_table(case, order_subtotal, is_member, is_sale, expected):
    """TC-UNIT-005: скидка участника 5% только при сумме от 3000 вне распродажи."""
    result = member_discount(Decimal(order_subtotal), is_member, is_sale)

    assert result == Decimal(expected), f"{case}: ожидалась скидка {expected}"
