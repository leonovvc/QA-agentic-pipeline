# Сводка автотестов — Ценообразование корзины

## Профиль стека

## Language(s)
Python >=3.10 (`pyproject.toml`); фактически запущено на Python 3.11.9.

## Unit Test Framework
pytest (`[tool.pytest.ini_options]` в `pyproject.toml`: `testpaths = ["tests"]`, `pythonpath = ["src"]`, `addopts = "-q"`). Каталог `tests/`, именование `test_*.py`, простые функции без классов, общие фикстуры в `tests/conftest.py`.

## API Test Approach
Нет отдельной настройки. Принято решение (допущение): pytest + стандартный `urllib` (без новых зависимостей), URL сервиса из переменной `CART_API_URL`; без неё тест пропускается как «предусловие не выполнено».

## E2E Framework
Не обнаружен; E2E-кейсов в плане нет, не требуется.

## How to Run
`python -m pytest -rsx -v` из корня репозитория.

## CI Integration
Конфигурации CI (`.github/workflows`, `.gitlab-ci.yml`) не найдены. Новые тесты в CI не запускаются.

## Recommendation
Добавить CI-задачу с `python -m pytest`; для TC-API-001 — поднять стенд корзины и задать `CART_API_URL`. Репозиторий не является git-репозиторием, коммит не выполнялся.

## Соответствие кейсов и тестов

## Mapping

| TC | File | Test | Status | Notes |
|---|---|---|---|---|
| TC-UNIT-001 | tests/test_pricing_rules.py | test_quantity_is_valid_only_between_1_and_20 | passed | параметризован: 0, 1, 20, 21 |
| TC-UNIT-002 | tests/test_pricing_rules.py | test_subtotal_of_several_lines_sums_price_times_quantity | passed | 348.50 |
| TC-UNIT-003 | tests/test_pricing_rules.py | test_shipping_is_charged_below_free_threshold | passed | |
| TC-UNIT-004 | tests/test_pricing_rules.py | test_shipping_is_free_exactly_at_threshold | failed | предполагаемый дефект продукта: `shipping_cost(5000.00)` вернул 300.00, ожидалось 0.00 (см. ниже); тест оставлен красным, без xfail/skip |
| TC-UNIT-005 | tests/test_pricing_rules.py | test_member_discount_applies_only_for_member_from_3000_outside_sale | passed | параметризован R1–R4 |
| TC-API-001 | tests/test_cart_api.py | test_cart_response_has_free_shipping_at_5000 | not run | не задан `CART_API_URL`, сервис корзины недоступен; тест пропущен через `skipif` (отсутствие предусловия) |
| TC-MAN-001 | — | — | manual | исследовательский чартер, автоматизация не имеет смысла |

## Выполненные команды

1. `cd ... && python -m pytest -rsx -v` — отказано в разрешении (составная команда), не выполнялась.
2. `python -m pytest -rsx -v` — exit code 1; итог: 12 passed, 1 failed (TC-UNIT-004), 1 skipped (TC-API-001). Два существующих теста в `tests/test_cart_lines.py` проходят.

Проверка импортов/pyflakes отдельно не запускалась; импорты подтверждены успешной коллекцией pytest.

## Предполагаемые дефекты продукта

- **TC-UNIT-004 / REQ-3** — `src/shop/pricing.py::shipping_cost` использует `order_subtotal > FREE_SHIPPING_THRESHOLD`, тогда как ТЗ п. 3 говорит «от 5000 ₽» (включительно). При сумме ровно 5000.00 возвращается 300.00 вместо 0.00. Вероятное исправление: `>=`. Код продукта не менялся. Тот же дефект ожидаемо проявится и в TC-API-001, если сервис использует это правило.

## Несогласие с распределением

Нет. Замечание для Stage 4: TC-API-001 зависит от заранее подготовленной корзины C1 на 5000,00 в стенде — способ её создания в кейсе не описан.
