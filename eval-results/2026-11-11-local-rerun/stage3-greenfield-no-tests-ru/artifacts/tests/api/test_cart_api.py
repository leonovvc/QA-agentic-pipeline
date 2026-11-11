"""API-тест корзины.

Источник: задача pricing, кейсы docs/qa/pricing/test-cases-api.md (TC-API-001).
Нужен живой сервис корзины: адрес берётся из CART_API_URL, иначе тест пропускается.
Корзина C1 на сумму 5000,00 должна существовать в тестовом окружении.
"""
import json
import os
import urllib.request
from decimal import Decimal

import pytest

CART_API_URL = os.environ.get("CART_API_URL")

pytestmark = [
    pytest.mark.api,
    pytest.mark.skipif(not CART_API_URL, reason="CART_API_URL не задан: сервис корзины недоступен"),
]


def test_cart_with_5000_subtotal_has_free_shipping():
    """TC-API-001: ответ корзины содержит бесплатную доставку при сумме 5000,00 (REQ-3)."""
    with urllib.request.urlopen(f"{CART_API_URL}/carts/C1", timeout=10) as response:
        status = response.status
        body = json.loads(response.read(), parse_float=Decimal)

    assert status == 200
    assert body["shipping"] == Decimal("0.00")
