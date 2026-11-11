"""Unit-тесты правил ценообразования корзины (shop.pricing).

Источник: задача pricing, ТЗ docs/qa/pricing/spec-source.md.
Кейсы: docs/qa/pricing/test-cases-unit.md (TC-UNIT-001 ... TC-UNIT-005).
Идентификатор кейса стоит в начале docstring и в id параметризации.
"""
from decimal import Decimal

import pytest

from shop.pricing import CartLine, is_valid_quantity, member_discount, shipping_cost, subtotal


@pytest.mark.parametrize(
    ("quantity", "expected"),
    [(0, False), (1, True), (20, True), (21, False)],
    ids=["0-below-min", "1-min", "20-max", "21-above-max"],
)
def test_is_valid_quantity_accepts_only_1_to_20(quantity, expected):
    """TC-UNIT-001: количество 0 и 21 недопустимо, 1 и 20 — допустимо (REQ-1)."""
    assert is_valid_quantity(quantity) is expected, f"количество {quantity}: ожидалось {expected}"


def test_subtotal_sums_price_times_quantity_over_lines():
    """TC-UNIT-002: сумма корзины из нескольких строк = сумма цена × количество (REQ-2)."""
    lines = [
        CartLine(sku="MUG-01", price=Decimal("100.00"), quantity=2),
        CartLine(sku="TEA-02", price=Decimal("49.50"), quantity=3),
    ]

    assert subtotal(lines) == Decimal("348.50")


def test_shipping_is_paid_300_below_free_threshold():
    """TC-UNIT-003: при сумме 4999,99 доставка платная — 300,00 (REQ-3)."""
    assert shipping_cost(Decimal("4999.99")) == Decimal("300.00")


def test_shipping_is_free_at_exactly_5000():
    """TC-UNIT-004: при сумме ровно 5000,00 доставка бесплатная (REQ-3).

    ТЗ п.3: «от 5000 ₽» — граница включена.
    """
    assert shipping_cost(Decimal("5000.00")) == Decimal("0.00"), (
        "на пороге 5000,00 доставка должна быть бесплатной"
    )


@pytest.mark.parametrize(
    ("order_subtotal", "is_member", "is_sale_period", "expected"),
    [
        (Decimal("3000.00"), True, False, Decimal("150.00")),
        (Decimal("3000.00"), False, False, Decimal("0.00")),
        (Decimal("2999.99"), True, False, Decimal("0.00")),
        (Decimal("3000.00"), True, True, Decimal("0.00")),
    ],
    ids=["R1-member-at-threshold", "R2-not-member", "R3-below-threshold", "R4-sale-period"],
)
def test_member_discount_decision_table(order_subtotal, is_member, is_sale_period, expected):
    """TC-UNIT-005: скидка участника 5% только при сумме от 3000 вне распродажи (REQ-4, A1)."""
    assert member_discount(order_subtotal, is_member, is_sale_period) == expected
