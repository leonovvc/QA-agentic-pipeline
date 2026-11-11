"""Unit-тесты правил ценообразования корзины.

Источник: задача `pricing`, кейсы в docs/qa/pricing/test-cases-unit.md.
Оракул каждого теста — ожидаемый результат кейса (ТЗ: docs/qa/pricing/spec-source.md).
"""
from decimal import Decimal

import pytest

from shop.pricing import CartLine, is_valid_quantity, member_discount, shipping_cost, subtotal

pytestmark = pytest.mark.unit

SHIPPING_FEE = Decimal("300.00")
NO_SHIPPING = Decimal("0.00")


@pytest.mark.parametrize(
    "quantity, expected",
    [(0, False), (1, True), (20, True), (21, False)],
    ids=["qty-0", "qty-1", "qty-20", "qty-21"],
)
def test_tc_unit_001_quantity_boundaries(quantity, expected):
    """TC-UNIT-001: количество 0 и 21 недопустимо, 1 и 20 — допустимо (REQ-1)."""
    assert is_valid_quantity(quantity) is expected, f"количество {quantity}: ожидалось {expected}"


def test_tc_unit_002_subtotal_sums_price_times_quantity():
    """TC-UNIT-002: сумма из нескольких строк = сумма цена × количество (REQ-2)."""
    lines = [
        CartLine(sku="MUG-01", price=Decimal("100.00"), quantity=2),
        CartLine(sku="CUP-02", price=Decimal("49.50"), quantity=3),
    ]

    result = subtotal(lines)

    assert result == Decimal("348.50"), "100.00*2 + 49.50*3 должно давать 348.50"


def test_tc_unit_003_shipping_is_paid_below_threshold():
    """TC-UNIT-003: при сумме 4999,99 доставка платная — 300,00 (REQ-3)."""
    result = shipping_cost(Decimal("4999.99"))

    assert result == SHIPPING_FEE, "ниже порога 5000 доставка стоит 300.00"


def test_tc_unit_004_shipping_is_free_exactly_at_threshold():
    """TC-UNIT-004: при сумме ровно 5000,00 доставка бесплатная (REQ-3).

    ТЗ п.3: «от 5000 ₽» — порог включительный.
    """
    result = shipping_cost(Decimal("5000.00"))

    assert result == NO_SHIPPING, "при сумме ровно 5000.00 доставка должна быть бесплатной (ТЗ п.3: «от 5000»)"


@pytest.mark.parametrize(
    "is_member, order_subtotal, is_sale, expected",
    [
        (True, "3000.00", False, "150.00"),   # R1: все условия выполнены
        (False, "3000.00", False, "0.00"),    # R2: не участник
        (True, "2999.99", False, "0.00"),     # R3: ниже порога
        (True, "3000.00", True, "0.00"),      # R4: период распродажи
    ],
    ids=["R1-member-at-3000", "R2-not-member", "R3-below-3000", "R4-sale-period"],
)
def test_tc_unit_005_member_discount_decision_table(is_member, order_subtotal, is_sale, expected):
    """TC-UNIT-005: скидка 5% только для участника при сумме от 3000 вне распродажи (REQ-4, A1)."""
    result = member_discount(Decimal(order_subtotal), is_member, is_sale)

    assert result == Decimal(expected), f"участник={is_member}, сумма={order_subtotal}, распродажа={is_sale}"
