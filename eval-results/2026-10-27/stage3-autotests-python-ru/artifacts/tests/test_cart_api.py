import json
import os
import urllib.request
from decimal import Decimal

import pytest

CART_API_URL = os.environ.get("CART_API_URL")

pytestmark = pytest.mark.skipif(not CART_API_URL, reason="CART_API_URL не задан: сервис корзины недоступен")


def test_tc_api_001_cart_with_subtotal_5000_has_free_shipping():
    # Предусловие кейса: на стенде существует корзина C1 на сумму 5000,00
    with urllib.request.urlopen(f"{CART_API_URL.rstrip('/')}/carts/C1", timeout=10) as response:
        status = response.status
        body = json.loads(response.read(), parse_float=Decimal)

    assert status == 200
    assert body["shipping"] == Decimal("0.00")
