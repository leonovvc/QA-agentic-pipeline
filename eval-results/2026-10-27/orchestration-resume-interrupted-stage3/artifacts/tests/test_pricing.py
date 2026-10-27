# Автотесты по задаче pricing; кейсы: docs/qa/pricing/test-cases-unit.md, test-cases-api.md
import json
import os
import urllib.request
from decimal import Decimal

import pytest

from shop.pricing import CartLine, is_valid_quantity, member_discount, shipping_cost, subtotal

SHIPPING_FEE = Decimal("300.00")
NO_SHIPPING = Decimal("0.00")


@pytest.mark.parametrize(
    "quantity, expected",
    [(0, False), (1, True), (20, True), (21, False)],
    ids=["0-invalid", "1-valid", "20-valid", "21-invalid"],
)
def test_tc_unit_001_quantity_boundaries(quantity, expected):
    """TC-UNIT-001: количество 0 и 21 недопустимо, 1 и 20 — допустимо (REQ-1)."""
    assert is_valid_quantity(quantity) is expected, f"quantity={quantity}"


def test_tc_unit_002_subtotal_sums_price_times_quantity_over_lines():
    """TC-UNIT-002: сумма из нескольких строк = Σ цена × количество (REQ-2)."""
    lines = [
        CartLine(sku="MUG-01", price=Decimal("100.00"), quantity=2),
        CartLine(sku="PEN-01", price=Decimal("49.50"), quantity=3),
    ]

    result = subtotal(lines)

    assert result == Decimal("348.50")


def test_tc_unit_003_shipping_is_charged_just_below_threshold():
    """TC-UNIT-003: при 4999,99 доставка платная — 300,00 (REQ-3)."""
    assert shipping_cost(Decimal("4999.99")) == SHIPPING_FEE


def test_tc_unit_004_shipping_is_free_exactly_at_threshold():
    """TC-UNIT-004: при ровно 5000,00 доставка бесплатная (REQ-3, ТЗ: «от 5000 ₽»)."""
    result = shipping_cost(Decimal("5000.00"))

    assert result == NO_SHIPPING, "на пороге 5000,00 доставка должна быть 0,00 (порог включительно)"


@pytest.mark.parametrize(
    "is_member, order_subtotal, is_sale, expected",
    [
        (True, "3000.00", False, "150.00"),  # R1: все условия выполнены
        (False, "3000.00", False, "0.00"),  # R2: не участник
        (True, "2999.99", False, "0.00"),  # R3: ниже порога
        (True, "3000.00", True, "0.00"),  # R4: распродажа
    ],
    ids=["R1-member-at-threshold", "R2-not-member", "R3-below-threshold", "R4-sale-period"],
)
def test_tc_unit_005_member_discount_decision_table(is_member, order_subtotal, is_sale, expected):
    """TC-UNIT-005: скидка 5% только для участника от 3000 вне распродажи (REQ-4, A1)."""
    result = member_discount(Decimal(order_subtotal), is_member, is_sale)

    assert result == Decimal(expected)


@pytest.mark.skipif(
    not os.environ.get("CART_API_URL"),
    reason="CART_API_URL не задан: сервис корзины недоступен, корзина C1 не создана",
)
def test_tc_api_001_cart_response_has_free_shipping_at_5000():
    """TC-API-001: GET /carts/C1 (сумма 5000,00) → 200, shipping = 0.00 (REQ-3)."""
    url = os.environ["CART_API_URL"].rstrip("/") + "/carts/C1"

    with urllib.request.urlopen(url, timeout=10) as response:
        status = response.status
        body = json.load(response)

    assert status == 200
    assert Decimal(str(body["shipping"])) == NO_SHIPPING
