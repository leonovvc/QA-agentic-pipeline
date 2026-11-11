import json
import os
import urllib.request
from decimal import Decimal

import pytest

CART_API_URL = os.environ.get("CART_API_URL")

# Нет URL сервиса — это отсутствие предусловия, а не ожидаемый отказ продукта.
requires_cart_api = pytest.mark.skipif(
    not CART_API_URL, reason="CART_API_URL не задан: сервис корзины недоступен"
)


@requires_cart_api
def test_cart_response_has_free_shipping_at_5000():
    """TC-API-001: ответ корзины C1 (сумма 5000,00) содержит shipping = 0.00."""
    with urllib.request.urlopen(f"{CART_API_URL.rstrip('/')}/carts/C1") as response:
        status = response.status
        body = json.load(response)

    assert status == 200
    assert Decimal(str(body["shipping"])) == Decimal("0.00")
