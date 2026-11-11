"""API-тесты сервиса корзины.

Источник: задача `pricing`, кейсы в docs/qa/pricing/test-cases-api.md.
Требуют запущенный сервис: переменная окружения CART_API_URL и корзина C1 на 5000.00.
Без них тесты пропускаются (skip) — это НЕ прохождение.
"""
import json
import os
import urllib.request
from decimal import Decimal

import pytest

pytestmark = pytest.mark.api

CART_API_URL = os.environ.get("CART_API_URL")
requires_cart_service = pytest.mark.skipif(
    not CART_API_URL, reason="CART_API_URL не задан: сервис корзины недоступен"
)


@requires_cart_service
def test_tc_api_001_cart_response_has_free_shipping_at_5000():
    """TC-API-001: ответ корзины C1 (5000,00) содержит shipping = 0.00 (REQ-3)."""
    with urllib.request.urlopen(f"{CART_API_URL}/carts/C1", timeout=10) as response:
        status = response.status
        body = json.loads(response.read())

    assert status == 200
    assert Decimal(str(body["shipping"])) == Decimal("0.00"), "доставка при сумме 5000.00 должна быть бесплатной"
