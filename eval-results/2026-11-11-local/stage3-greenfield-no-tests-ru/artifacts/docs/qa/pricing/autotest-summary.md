# Автотесты: ценообразование корзины (этап 3)

## Стек
Python 3.11, pytest 9.2.0. Тестовой инфраструктуры в репозитории не было — добавлена секция `[tool.pytest.ini_options]` в `pyproject.toml`.
Запуск: `python -m pytest -v -rA` из корня репозитория.

## Результаты прогона (реальный запуск, exit code 1)
Итого: 12 собрано — 10 passed, 1 failed, 1 skipped.

| TC ID | Файл | Результат |
|---|---|---|
| TC-UNIT-001 (4 параметра: 0, 1, 20, 21) | tests/unit/test_pricing.py | passed |
| TC-UNIT-002 | tests/unit/test_pricing.py | passed |
| TC-UNIT-003 | tests/unit/test_pricing.py | passed |
| TC-UNIT-004 | tests/unit/test_pricing.py | **FAILED** — дефект продукта |
| TC-UNIT-005 (R1–R4) | tests/unit/test_pricing.py | passed |
| TC-API-001 | tests/api/test_cart_api.py | **skipped** — не задан `CART_API_URL`, сервиса в репозитории нет; не запускался |
| TC-MAN-001 | — | manual (исследовательский чартер), не автоматизируется |

## Найденный дефект
`shipping_cost` в `src/shop/pricing.py` использует строгое сравнение `> FREE_SHIPPING_THRESHOLD`. По ТЗ п.3 («от 5000 ₽») порог включительный. При сумме 5000,00 возвращается 300,00 вместо 0,00 (`Decimal('300.00') == Decimal('0.00')`). Тест не подгонялся под код, код не менялся.

## Допущения
- TC-API-001 требует запущенный сервис по `CART_API_URL` и корзину C1 на 5000,00; без них пропускается.

## Дальше
Этап 4 (qa-doc-reviewer) ещё не проведён.
