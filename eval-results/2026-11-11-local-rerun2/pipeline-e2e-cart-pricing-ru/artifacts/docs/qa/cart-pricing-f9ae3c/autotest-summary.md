# Автотесты: cart-pricing-f9ae3c

## Профиль стека

## Языки
Python (>=3.10), `pyproject.toml`; исходники в `src/shop/` (единственный модуль — `pricing.py`).

## Unit-фреймворк
pytest; конфигурация в `pyproject.toml` (`[tool.pytest.ini_options]`: `testpaths=["tests"]`, `pythonpath=["src"]`, `addopts="-q"`). Каталог `tests/`, файлы `test_*.py`, фикстуры в `tests/conftest.py` (`mug`). Существующий стиль: простые функции `test_<поведение>`, без классов. Новые тесты добавлены в тот же каталог, второй набор не создавался.

## API-тесты
Не обнаружено. В репозитории нет кода эндпоинта `POST /api/cart/price` (нет веб-фреймворка, роутов, зависимостей).

## E2E-фреймворк
Не обнаружено. Нет фронтенда, Playwright/Cypress.

## Как запускать
`python -m pytest` (из корня репозитория).

## Интеграция с CI
CI-конфигурации нет (`.github/workflows`, `.gitlab-ci.yml` отсутствуют) — новые тесты в CI не запускаются.

## Рекомендация
Добавить CI-джобу с `python -m pytest`. API/E2E-тесты писать после появления кода эндпоинта и страницы корзины.

Примечание: `.agents/qa-project-context.md` отсутствует. Язык вывода — ru (идентификаторы на английском). Файл `tests/test_cart_pricing.py` — расширение существующего набора, в стиле ближайших тестов (функции, `Decimal`, `mug`-подход), с docstring на русском и TC-ID в нём (названия pytest-функций остаются английскими по `qa-output-standards`).

## Соответствие кейсов и тестов

| TC | File | Test | Status | Notes |
|---|---|---|---|---|
| TC-UNIT-001 | tests/test_cart_pricing.py | test_is_valid_quantity_accepts_values_within_range[1,2,19,20]; test_is_valid_quantity_rejects_values_outside_range[0,21,-1] | passed | Два параметризованных теста (допустимые / недопустимые классы) |
| TC-UNIT-002 | tests/test_cart_pricing.py | test_subtotal_sums_price_times_quantity_over_several_lines | passed | 1549.98 |
| TC-UNIT-003 | tests/test_cart_lines.py | test_subtotal_of_empty_cart_is_zero | passed | Существующий тест, по кейсу новый не создаётся; в его имени/docstring нет TC-ID (существующий файл не менялся) |
| TC-UNIT-004 | tests/test_cart_pricing.py | test_shipping_cost_is_300_for_subtotal_1000 | passed | |
| TC-UNIT-005 | tests/test_cart_pricing.py | test_shipping_cost_just_below_threshold_is_paid; test_shipping_cost_just_above_threshold_is_free | passed | Две стороны порога — два теста |
| TC-UNIT-006 | tests/test_cart_pricing.py | test_shipping_cost_is_free_at_exact_threshold_5000 | failed | Предполагаемый дефект продукта (не дефект теста); без xfail/skip |
| TC-UNIT-007 | tests/test_cart_pricing.py | test_member_discount_is_zero_just_below_threshold | passed | |
| TC-UNIT-008 | tests/test_cart_pricing.py | test_member_discount_is_5_percent_at_threshold_3000 | passed | |
| TC-UNIT-009 | tests/test_cart_pricing.py | test_member_discount_is_zero_for_non_member | passed | |
| TC-UNIT-010 | tests/test_cart_pricing.py | test_member_discount_is_zero_during_sale_period | passed | |
| TC-UNIT-011 | tests/test_cart_pricing.py | test_member_discount_rounds_half_up_to_cents | passed | Проверены значение 150.01 и экспонента -2 |
| TC-API-001 | — | — | not run | В репозитории нет кода `POST /api/cart/price` (есть только `shop.pricing`); тест не выдумывался |
| TC-API-002 | — | — | not run | То же: нет кода эндпоинта |
| TC-API-003 | — | — | not run | То же: нет кода эндпоинта |
| TC-API-004 | — | — | not run | То же: нет кода эндпоинта |
| TC-E2E-001 | — | — | not run | Нет фронтенда/страницы корзины и E2E-фреймворка |
| TC-E2E-002 | — | — | not run | То же |
| TC-E2E-003 | — | — | not run | То же |
| TC-MAN-001 | — | — | manual | Исследовательский чартер, не автоматизируется |
| TC-MAN-002 | — | — | manual | Исследовательский чартер, не автоматизируется |

## Выполненные команды

- `python -m pytest -rA` — exit code 1 (1 failed, 18 passed; failed: TC-UNIT-006).
- Первая попытка записать файл тестов и запустить pytest одной составной командой (heredoc + `&&`) была запрещена системой разрешений; файл создан инструментом записи, затем `python -m pytest -rA` запущен одиночной командой успешно.
- Проверка стиля/линтером (`ruff`, `pyflakes`) не запускалась — не настроены в репозитории. Импорты подтверждены самим прогоном.

## Предполагаемые дефекты продукта

1. **TC-UNIT-006, REQ-10 (A4)** — `shop.pricing.shipping_cost(Decimal("5000.00"))` возвращает `300.00`, ожидается `0.00`. ТЗ §3: бесплатная доставка «от 5000 ₽»; в коде `src/shop/pricing.py` условие `order_subtotal > FREE_SHIPPING_THRESHOLD` (строгое), нужно `>=`. Тест остаётся красным; карантин — решение человека на чекпойнте. Замечание: граница опирается на допущение A4 (порог включительный); если владелец ТЗ ответит иначе, это дефект кейса, а не кода.

## Несогласие с распределением

Нет. Замечание для ревьюера: TC-UNIT-003 сопоставлен существующему тесту без TC-ID в названии (контракт требует ID в названии/теге) — решить, добавлять ли ID в существующий файл.
