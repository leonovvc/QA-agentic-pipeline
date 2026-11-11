# Сводка автотестов — cart-pricing-f9ae3c

Язык вывода: ru. Кейсы: `docs/qa/cart-pricing-f9ae3c/test-cases-*.md`. Код тестов: `tests/test_pricing_rules.py` (новый файл в существующем наборе `tests/`).

## Профиль стека

## Stack Profile — shop (src/shop)

## Language(s)
Python 3.11 (`requires-python >= 3.10`), манифест `pyproject.toml`. Единственная тестовая поверхность — чистые функции `src/shop/pricing.py`.

## Unit Test Framework
pytest 9; конфиг `[tool.pytest.ini_options]` в `pyproject.toml` (`testpaths = ["tests"]`, `pythonpath = ["src"]`, `addopts = "-q"`). Каталог `tests/`, именование `test_*.py`, общая фикстура `mug` в `tests/conftest.py`. Существующий стиль (`tests/test_cart_lines.py`): простые функции без классов, `Decimal`, Arrange-Act-Assert. Новые тесты следуют ему; докстринг с ID кейса на русском, идентификаторы на английском.

## API Test Approach
none detected — в репозитории нет HTTP-слоя и обработчика `POST /api/cart/price`. Рекомендация: после появления обработчика — pytest + нативный тестовый клиент фреймворка сервиса (без нового стека).

## E2E Framework
none detected — нет UI страницы корзины, нет playwright/cypress конфигов. Рекомендация: Playwright после появления UI.

## How to Run
`python -m pytest` (из корня репозитория).

## CI Integration
CI-конфигурации (`.github/workflows`, `.gitlab-ci.yml`) не найдены: тесты нигде автоматически не запускаются. Новые тесты не дают защиты, пока не подключён CI.

## Recommendation
Добавить CI-задачу `python -m pytest`. API/E2E-инфраструктуру не создавать до появления реализации.

## Соответствие кейсов и тестов

## Mapping

| TC | File | Test | Status | Notes |
|---|---|---|---|---|
| TC-UNIT-001 | tests/test_pricing_rules.py | test_tc_unit_001_quantity_zero_is_rejected | passed | |
| TC-UNIT-002 | tests/test_pricing_rules.py | test_tc_unit_002_quantity_one_is_accepted | passed | |
| TC-UNIT-003 | tests/test_pricing_rules.py | test_tc_unit_003_quantity_twenty_is_accepted | passed | |
| TC-UNIT-004 | tests/test_pricing_rules.py | test_tc_unit_004_quantity_twenty_one_is_rejected | passed | |
| TC-UNIT-005 | tests/test_pricing_rules.py | test_tc_unit_005_negative_quantity_is_rejected | passed | |
| TC-UNIT-006 | tests/test_pricing_rules.py | test_tc_unit_006_subtotal_sums_price_times_quantity_over_lines | passed | |
| TC-UNIT-007 | tests/test_pricing_rules.py | test_tc_unit_007_subtotal_of_empty_cart_is_zero | passed | Частично дублирует существующий `tests/test_cart_lines.py::test_subtotal_of_empty_cart_is_zero` (без TC ID); новый тест дополнительно проверяет 2 знака после запятой |
| TC-UNIT-008 | tests/test_pricing_rules.py | test_tc_unit_008_subtotal_keeps_cents_without_precision_loss | passed | |
| TC-UNIT-009 | tests/test_pricing_rules.py | test_tc_unit_009_shipping_below_threshold_costs_300 | passed | |
| TC-UNIT-010 | tests/test_pricing_rules.py | test_tc_unit_010_shipping_just_below_threshold_costs_300 | passed | |
| TC-UNIT-011 | tests/test_pricing_rules.py | test_tc_unit_011_shipping_at_exact_threshold_is_free | failed | Подозреваемый дефект продукта (расхождение ТЗ и кода), см. ниже. Тест не изменялся под код и не помечен xfail |
| TC-UNIT-012 | tests/test_pricing_rules.py | test_tc_unit_012_shipping_just_above_threshold_is_free | passed | |
| TC-UNIT-013 | tests/test_pricing_rules.py | test_tc_unit_013_member_gets_discount_at_exact_threshold | passed | |
| TC-UNIT-014 | tests/test_pricing_rules.py | test_tc_unit_014_member_gets_no_discount_just_below_threshold | passed | |
| TC-UNIT-015 | tests/test_pricing_rules.py | test_tc_unit_015_non_member_gets_no_discount | passed | |
| TC-UNIT-016 | tests/test_pricing_rules.py | test_tc_unit_016_member_gets_no_discount_during_sale | passed | |
| TC-UNIT-017 | tests/test_pricing_rules.py | test_tc_unit_017_discount_rounds_half_up | passed | Ожидание half-up по допущению A4 (Q6 открыт) |
| TC-UNIT-018 | tests/test_pricing_rules.py | test_tc_unit_018_discount_rounds_down_below_half_cent | passed | |
| TC-API-001 | — | — | not run | Нет реализации: в репозитории нет `POST /api/cart/price` и HTTP-слоя |
| TC-API-002 | — | — | not run | Нет реализации (см. TC-API-001) |
| TC-API-003 | — | — | not run | Нет реализации; ожидание зависит от Q2 |
| TC-API-004 | — | — | not run | Нет реализации; зависит от Q11 |
| TC-API-005 | — | — | not run | Нет реализации |
| TC-API-006 | — | — | not run | Нет реализации; зависит от Q3 |
| TC-API-007 | — | — | not run | Нет реализации; зависит от Q4 |
| TC-API-008 | — | — | not run | Нет реализации; зависит от Q4 |
| TC-API-009 | — | — | not run | Нет реализации; зависит от Q1 |
| TC-API-010 | — | — | not run | Нет реализации; зависит от Q1, Q8 |
| TC-API-011 | — | — | not run | Нет реализации; зависит от Q1 |
| TC-API-012 | — | — | not run | Нет реализации; зависит от Q1 |
| TC-API-013 | — | — | not run | Нет реализации |
| TC-API-014 | — | — | not run | Нет реализации; зависит от Q1 |
| TC-API-015 | — | — | not run | Нет реализации; зависит от Q1 |
| TC-API-016 | — | — | not run | Нет реализации |
| TC-E2E-001 | — | — | not run | Нет реализации: нет UI страницы корзины, браузерного фреймворка и стенда |
| TC-E2E-002 | — | — | not run | Нет реализации (UI и API) |
| TC-E2E-003 | — | — | not run | Нет реализации; зависит от Q7 |
| TC-E2E-004 | — | — | not run | Нет реализации; зависит от Q7, Q11 |
| TC-E2E-005 | — | — | not run | Нет реализации; зависит от Q3 |
| TC-MAN-001 | — | — | manual | Исследовательский чартер, не автоматизируется |
| TC-MAN-002 | — | — | manual | Исследовательский чартер, не автоматизируется |

Итого: unit — 18 кейсов, 17 passed, 1 failed; API — 16 not run; E2E — 5 not run; manual — 2.

## Выполненные команды

| Команда (из корня репозитория) | Код выхода | Результат |
|---|---|---|
| `python -m pytest -p no:cacheprovider -rf` | 1 | 19 passed, 1 failed (весь набор: 18 новых + 2 существующих теста `test_cart_lines.py`); упал только TC-UNIT-011 |
| `python -m pyflakes tests/test_pricing_rules.py` | 1 | pyflakes не установлен (`No module named pyflakes`) — статическая проверка не выполнена; импорты подтверждены успешным запуском pytest |

Примечание: вывод консоли Windows показывает кириллицу в докстрингах/сообщениях как mojibake или `\uXXXX` — это артефакт кодировки консоли, не дефект файлов (файлы в UTF-8).

## Предполагаемые дефекты продукта

- **TC-UNIT-011 (REQ-8, A14, Q11) — предполагаемый дефект продукта / расхождение ТЗ и кода.** ТЗ: бесплатная доставка «от 5000 ₽» (граница включительна). Код `shipping_cost` в `src/shop/pricing.py` использует `order_subtotal > FREE_SHIPPING_THRESHOLD`, поэтому при сумме ровно 5000.00 возвращает `300.00` вместо `0.00`. Фактический результат: `assert Decimal('300.00') == Decimal('0.00')`. Вероятное исправление: `>=`. Решение зависит от Q11 (владелец ТЗ); если подтвердят «строго больше», нужно править ТЗ и кейс, а не assertion «втихую». Тест оставлен честно падающим, продуктовый код не менялся. Связанные API-кейс TC-API-004 и E2E TC-E2E-004 ждут того же решения.

## Несогласие с распределением

Нет. Замечание для ревьюера: TC-UNIT-007 дублирует существующий тест `test_subtotal_of_empty_cart_is_zero` (без TC ID); при желании существующий тест можно переименовать вместо дубля.
