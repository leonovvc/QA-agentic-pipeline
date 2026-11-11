"""Автотесты правил расчёта корзины (shop.pricing).

Источник: задача cart-pricing-f9ae3c, ТЗ specs/cart-pricing.md v1.2.
Кейсы: docs/qa/cart-pricing-f9ae3c/test-cases-unit.md
TC-UNIT-003 покрыт существующим test_subtotal_of_empty_cart_is_zero (tests/test_cart_lines.py).
"""
from decimal import Decimal

import pytest

from shop.pricing import CartLine, is_valid_quantity, member_discount, shipping_cost, subtotal


@pytest.mark.parametrize("quantity", [1, 2, 19, 20])
def test_is_valid_quantity_accepts_values_within_range(quantity):
    """TC-UNIT-001: количество 1, 2, 19, 20 допустимо."""
    assert is_valid_quantity(quantity) is True, f"{quantity} входит в диапазон 1..20"


@pytest.mark.parametrize("quantity", [0, 21, -1])
def test_is_valid_quantity_rejects_values_outside_range(quantity):
    """TC-UNIT-001: количество 0, 21, -1 недопустимо."""
    assert is_valid_quantity(quantity) is False, f"{quantity} вне диапазона 1..20"


def test_subtotal_sums_price_times_quantity_over_several_lines():
    """TC-UNIT-002: сумма нескольких строк с копейками = сумма «цена × количество»."""
    lines = [
        CartLine(sku="MUG-01", price=Decimal("450.00"), quantity=3),
        CartLine(sku="PEN-02", price=Decimal("99.99"), quantity=2),
    ]

    result = subtotal(lines)

    assert result == Decimal("1549.98")  # 1350.00 + 199.98


def test_shipping_cost_is_300_for_subtotal_1000():
    """TC-UNIT-004: сумма 1000.00 — доставка 300.00."""
    assert shipping_cost(Decimal("1000.00")) == Decimal("300.00")


def test_shipping_cost_just_below_threshold_is_paid():
    """TC-UNIT-005: 4999.99 — доставка платная."""
    assert shipping_cost(Decimal("4999.99")) == Decimal("300.00")


def test_shipping_cost_just_above_threshold_is_free():
    """TC-UNIT-005: 5000.01 — доставка бесплатная."""
    assert shipping_cost(Decimal("5000.01")) == Decimal("0.00")


def test_shipping_cost_is_free_at_exact_threshold_5000():
    """TC-UNIT-006: ровно 5000.00 — доставка бесплатная (ТЗ: «от 5000 ₽», A4).

    Предполагаемый дефект продукта: код использует `>` вместо `>=`.
    """
    assert shipping_cost(Decimal("5000.00")) == Decimal("0.00"), (
        "порог 5000 включительный: при сумме ровно 5000.00 доставка должна быть 0.00"
    )


def test_member_discount_is_zero_just_below_threshold():
    """TC-UNIT-007: участник, 2999.99 — скидки нет."""
    assert member_discount(Decimal("2999.99"), True, False) == Decimal("0.00")


def test_member_discount_is_5_percent_at_threshold_3000():
    """TC-UNIT-008: участник, ровно 3000.00 — скидка 150.00."""
    assert member_discount(Decimal("3000.00"), True, False) == Decimal("150.00")


def test_member_discount_is_zero_for_non_member():
    """TC-UNIT-009: не участник, 3000.00 — скидки нет."""
    assert member_discount(Decimal("3000.00"), False, False) == Decimal("0.00")


def test_member_discount_is_zero_during_sale_period():
    """TC-UNIT-010: участник в период распродажи, 3000.00 — скидки нет."""
    assert member_discount(Decimal("3000.00"), True, True) == Decimal("0.00")


def test_member_discount_rounds_half_up_to_cents():
    """TC-UNIT-011: 3000.10 × 5% = 150.0050 → 150.01 (half-up; банковское дало бы 150.00)."""
    result = member_discount(Decimal("3000.10"), True, False)

    assert result == Decimal("150.01")
    assert result.as_tuple().exponent == -2, "результат должен иметь два знака после запятой"
