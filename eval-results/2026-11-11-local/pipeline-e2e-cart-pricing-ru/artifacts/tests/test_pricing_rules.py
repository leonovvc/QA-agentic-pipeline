"""Unit-тесты правил цены корзины (src/shop/pricing.py).

Кейсы: docs/qa/cart-pricing-f9ae3c/test-cases-unit.md (ТЗ: specs/cart-pricing.md).
Название каждого теста начинается с ID кейса в докстринге.
"""
from decimal import Decimal

import pytest

from shop.pricing import (
    CartLine,
    is_valid_quantity,
    member_discount,
    shipping_cost,
    subtotal,
)


# --- REQ-1: допустимое количество 1..20 включительно ---


def test_tc_unit_001_quantity_zero_is_rejected():
    """TC-UNIT-001: Количество 0 отклоняется (нижняя граница − 1)"""
    assert is_valid_quantity(0) is False, "0 ниже минимума 1"


def test_tc_unit_002_quantity_one_is_accepted():
    """TC-UNIT-002: Количество 1 допустимо (нижняя граница)"""
    assert is_valid_quantity(1) is True, "1 — минимально допустимое количество"


def test_tc_unit_003_quantity_twenty_is_accepted():
    """TC-UNIT-003: Количество 20 допустимо (верхняя граница включительно)"""
    assert is_valid_quantity(20) is True, "20 — максимально допустимое количество"


def test_tc_unit_004_quantity_twenty_one_is_rejected():
    """TC-UNIT-004: Количество 21 отклоняется (верхняя граница + 1)"""
    assert is_valid_quantity(21) is False, "21 выше максимума 20"


def test_tc_unit_005_negative_quantity_is_rejected():
    """TC-UNIT-005: Отрицательное количество −1 отклоняется"""
    assert is_valid_quantity(-1) is False, "отрицательное количество недопустимо"


# --- REQ-4, REQ-5, REQ-19: сумма корзины ---


def test_tc_unit_006_subtotal_sums_price_times_quantity_over_lines():
    """TC-UNIT-006: Сумма корзины по нескольким строкам = Σ цена × количество"""
    lines = [
        CartLine(sku="MUG-01", price=Decimal("450.00"), quantity=3),
        CartLine(sku="PEN-02", price=Decimal("199.99"), quantity=2),
    ]

    result = subtotal(lines)

    assert result == Decimal("1749.98"), "1350.00 + 399.98"


def test_tc_unit_007_subtotal_of_empty_cart_is_zero():
    """TC-UNIT-007: Сумма пустой корзины равна 0.00"""
    result = subtotal([])

    assert result == Decimal("0.00")
    assert result.as_tuple().exponent == -2, "ноль должен иметь 2 знака после запятой"


def test_tc_unit_008_subtotal_keeps_cents_without_precision_loss():
    """TC-UNIT-008: Сумма сохраняет копейки без потери точности"""
    lines = [CartLine(sku="CAB-11", price=Decimal("199.99"), quantity=3)]

    result = subtotal(lines)

    assert result == Decimal("599.97"), "199.99 × 3 без float-погрешности"
    assert result.as_tuple().exponent == -2, "ровно 2 знака после запятой"


# --- REQ-7, REQ-8: доставка (300.00, бесплатно от 5000.00 по ТЗ) ---


def test_tc_unit_009_shipping_below_threshold_costs_300():
    """TC-UNIT-009: Доставка при сумме 1000.00 стоит 300.00"""
    assert shipping_cost(Decimal("1000.00")) == Decimal("300.00")


def test_tc_unit_010_shipping_just_below_threshold_costs_300():
    """TC-UNIT-010: Доставка при сумме 4999.99 стоит 300.00 (порог − 0.01)"""
    assert shipping_cost(Decimal("4999.99")) == Decimal("300.00")


def test_tc_unit_011_shipping_at_exact_threshold_is_free():
    """TC-UNIT-011: Доставка при сумме ровно 5000.00 бесплатна (по ТЗ; Q11)

    ТЗ: бесплатная доставка «от 5000 ₽» — граница включительна. Если тест падает,
    это расхождение кода (`> 5000`) и ТЗ, а не дефект теста.
    """
    assert shipping_cost(Decimal("5000.00")) == Decimal("0.00"), (
        "при сумме ровно 5000.00 доставка должна быть бесплатной (ТЗ: «от 5000 ₽»)"
    )


def test_tc_unit_012_shipping_just_above_threshold_is_free():
    """TC-UNIT-012: Доставка при сумме 5000.01 бесплатна (порог + 0.01)"""
    assert shipping_cost(Decimal("5000.01")) == Decimal("0.00")


# --- REQ-9..11: скидка участника 5% (от 3000.00, не в распродажу, half-up) ---


def test_tc_unit_013_member_gets_discount_at_exact_threshold():
    """TC-UNIT-013: Участник без распродажи при сумме ровно 3000.00 получает скидку 150.00"""
    result = member_discount(Decimal("3000.00"), is_member=True, is_sale_period=False)

    assert result == Decimal("150.00"), "5% от 3000.00; порог 3000 включительно"


def test_tc_unit_014_member_gets_no_discount_just_below_threshold():
    """TC-UNIT-014: Участник при сумме 2999.99 скидку не получает (порог − 0.01)"""
    result = member_discount(Decimal("2999.99"), is_member=True, is_sale_period=False)

    assert result == Decimal("0.00")


def test_tc_unit_015_non_member_gets_no_discount():
    """TC-UNIT-015: Не участник при сумме 10000.00 скидку не получает"""
    result = member_discount(Decimal("10000.00"), is_member=False, is_sale_period=False)

    assert result == Decimal("0.00")


def test_tc_unit_016_member_gets_no_discount_during_sale():
    """TC-UNIT-016: Участник в период распродажи скидку не получает"""
    result = member_discount(Decimal("10000.00"), is_member=True, is_sale_period=True)

    assert result == Decimal("0.00")


def test_tc_unit_017_discount_rounds_half_up():
    """TC-UNIT-017: Скидка 150.005 округляется half-up до 150.01 (Q6, допущение A4)"""
    # 3000.10 × 0.05 = 150.0050 — ровно половина копейки; банковское округление дало бы 150.00
    result = member_discount(Decimal("3000.10"), is_member=True, is_sale_period=False)

    assert result == Decimal("150.01"), "половина копейки округляется вверх (half-up)"


def test_tc_unit_018_discount_rounds_down_below_half_cent():
    """TC-UNIT-018: Скидка 150.0045 округляется вниз до 150.00 (Q6)"""
    # 3000.09 × 0.05 = 150.0045 — меньше половины копейки
    result = member_discount(Decimal("3000.09"), is_member=True, is_sale_period=False)

    assert result == Decimal("150.00")
