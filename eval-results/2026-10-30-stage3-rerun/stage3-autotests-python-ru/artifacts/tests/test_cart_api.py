# Кейсы: docs/qa/pricing/test-cases-api.md (задача pricing)
import json
import os
import urllib.request

import pytest

CART_API_URL = os.environ.get("CART_API_URL")

# Сервис корзины в репозитории отсутствует: без CART_API_URL тест пропускается, а не «проходит».
requires_cart_api = pytest.mark.skipif(not CART_API_URL, reason="CART_API_URL не задан")


@requires_cart_api
def test_tc_api_001_cart_with_5000_subtotal_has_free_shipping():
    """TC-API-001: ответ корзины C1 на сумму 5000,00 содержит shipping = 0.00."""
    with urllib.request.urlopen(f"{CART_API_URL}/carts/C1", timeout=10) as response:
        status = response.status
        body = json.load(response)

    assert status == 200
    assert str(body["shipping"]) in ("0.00", "0"), f"shipping={body['shipping']}"
