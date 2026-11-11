from decimal import Decimal

import pytest

from shop.pricing import is_valid_quantity, member_discount, shipping_cost

ZERO = Decimal("0.00")
SHIPPING_FEE = Decimal("300.00")


@pytest.mark.parametrize("quantity", [1, 2, 19, 20])
def test_tc_unit_001_quantity_inside_range_is_valid(quantity):
    """TC-UNIT-001: количество на границах диапазона 1..20 принимается."""
    assert is_valid_quantity(quantity) is True, f"quantity={quantity} должно быть допустимым"


@pytest.mark.parametrize("quantity", [0, -1, 21])
def test_tc_unit_002_quantity_outside_range_is_invalid(quantity):
    """TC-UNIT-002: количество вне диапазона (0, -1, 21) отклоняется."""
    assert is_valid_quantity(quantity) is False, f"quantity={quantity} должно быть отклонено"


def test_tc_unit_006_shipping_is_charged_below_threshold():
    """TC-UNIT-006: сумма 1000.00 ниже порога — доставка 300.00."""
    assert shipping_cost(Decimal("1000.00")) == SHIPPING_FEE


def test_tc_unit_007_shipping_is_charged_just_below_threshold():
    """TC-UNIT-007: сумма 4999.99 — доставка платная 300.00."""
    assert shipping_cost(Decimal("4999.99")) == SHIPPING_FEE


@pytest.mark.xfail(
    strict=True,
    reason="Предполагаемый дефект продукта: shipping_cost сравнивает '>' вместо '>=', "
    "при сумме ровно 5000.00 доставка 300.00 вместо 0.00 (REQ-8)",
)
def test_tc_unit_008_shipping_is_free_exactly_at_threshold():
    """TC-UNIT-008: сумма ровно 5000.00 — доставка бесплатная (граница включительно)."""
    assert shipping_cost(Decimal("5000.00")) == ZERO, "порог 5000 включительно: доставка должна быть 0.00"


def test_tc_unit_009_member_gets_discount_exactly_at_threshold():
    """TC-UNIT-009: участник при сумме ровно 3000.00 получает 150.00."""
    assert member_discount(Decimal("3000.00"), True, False) == Decimal("150.00")


def test_tc_unit_010_member_gets_no_discount_just_below_threshold():
    """TC-UNIT-010: участник при сумме 2999.99 скидку не получает."""
    assert member_discount(Decimal("2999.99"), True, False) == ZERO


def test_tc_unit_011_non_member_gets_no_discount():
    """TC-UNIT-011: не участник при сумме 4000.00 скидку не получает."""
    assert member_discount(Decimal("4000.00"), False, False) == ZERO


def test_tc_unit_012_member_gets_no_discount_in_sale_period():
    """TC-UNIT-012: в период распродажи скидка участника 0.00 (без распродажи было бы 200.00)."""
    assert member_discount(Decimal("4000.00"), True, True) == ZERO


def test_tc_unit_013_discount_rounds_half_up():
    """TC-UNIT-013: скидка 150.005 округляется half-up до 150.01 (допущение A1, Q3)."""
    # Банковское округление дало бы 150.00 — кейс ловит именно его.
    assert member_discount(Decimal("3000.10"), True, False) == Decimal("150.01")
