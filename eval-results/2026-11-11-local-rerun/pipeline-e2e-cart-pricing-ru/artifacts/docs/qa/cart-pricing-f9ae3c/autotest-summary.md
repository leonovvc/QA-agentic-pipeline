# Сводка автотестов — cart-pricing-f9ae3c

Язык вывода: ru. Кейсы: `docs/qa/cart-pricing-f9ae3c/test-cases-{unit,api,manual}.md`.

## Stack Profile

## Stack Profile — shop (src/shop/pricing.py)

## Language(s)
Python >= 3.10 (`pyproject.toml`).

## Unit Test Framework
pytest; конфиг `[tool.pytest.ini_options]` в `pyproject.toml` (`testpaths=["tests"]`, `pythonpath=["src"]`, `addopts="-q"`). Каталог `tests/`, файлы `test_*.py`, функции `test_*`, общая фикстура `mug` в `tests/conftest.py`. Решение: расширен существующий набор, второй фреймворк не вводился.

## API Test Approach
Не обнаружен: в `src/shop/` только `pricing.py`, HTTP-слоя и эндпоинта `POST /api/cart/price` нет. Рекомендация ниже.

## E2E Framework
Не обнаружен; фронтенда нет. UI-кейсы остаются ручными.

## How to Run
`python -m pytest -rxXs` (из корня репозитория).

## CI Integration
CI-конфигурации в репозитории нет (`.github/`, `.gitlab-ci.yml` отсутствуют): тесты нигде автоматически не запускаются.

## Recommendation
Добавить минимальный CI-шаг `python -m pytest`; API-кейсы можно автоматизировать только после появления эндпоинта (и функции «итог»).

## Mapping

| TC | File | Test | Status | Notes |
|---|---|---|---|---|
| TC-UNIT-001 | tests/test_pricing_rules.py | test_tc_unit_001_quantity_inside_range_is_valid (параметры 1, 2, 19, 20) | passed | |
| TC-UNIT-002 | tests/test_pricing_rules.py | test_tc_unit_002_quantity_outside_range_is_invalid (0, -1, 21) | passed | |
| TC-UNIT-003 | tests/test_cart_lines.py | test_tc_unit_003_subtotal_sums_price_times_quantity_across_lines | passed | Существующий test_subtotal_multiplies_price_by_quantity покрывает только одну строку; добавлен кейс с двумя строками (3751.00) |
| TC-UNIT-004 | tests/test_cart_lines.py | test_tc_unit_004_duplicate_sku_lines_are_summed_as_separate_lines | passed | Опирается на A4 / Q8 |
| TC-UNIT-005 | tests/test_cart_lines.py | test_subtotal_of_empty_cart_is_zero | passed | Уже существовал, не дублировался; в названии нет TC ID — трассировка только через эту таблицу (не переименовывал чужой тест) |
| TC-UNIT-006 | tests/test_pricing_rules.py | test_tc_unit_006_shipping_is_charged_below_threshold | passed | |
| TC-UNIT-007 | tests/test_pricing_rules.py | test_tc_unit_007_shipping_is_charged_just_below_threshold | passed | |
| TC-UNIT-008 | tests/test_pricing_rules.py | test_tc_unit_008_shipping_is_free_exactly_at_threshold | failed (xfail strict) | Подозреваемый дефект продукта, см. ниже. pytest показывает как XFAIL |
| TC-UNIT-009 | tests/test_pricing_rules.py | test_tc_unit_009_member_gets_discount_exactly_at_threshold | passed | |
| TC-UNIT-010 | tests/test_pricing_rules.py | test_tc_unit_010_member_gets_no_discount_just_below_threshold | passed | |
| TC-UNIT-011 | tests/test_pricing_rules.py | test_tc_unit_011_non_member_gets_no_discount | passed | |
| TC-UNIT-012 | tests/test_pricing_rules.py | test_tc_unit_012_member_gets_no_discount_in_sale_period | passed | |
| TC-UNIT-013 | tests/test_pricing_rules.py | test_tc_unit_013_discount_rounds_half_up | passed | Зависит от A1 / Q3 |
| TC-API-001 | — | не реализован | not run | Нет HTTP-слоя и эндпоинта `POST /api/cart/price`; подделывать вызовом функций в тесте не стал |
| TC-API-002 | — | не реализован | not run | То же; плюс в `pricing.py` нет функции итога (subtotal − discount + shipping) |
| TC-API-003 | — | не реализован | not run | То же; зависит от A2 / Q10 |
| TC-API-004 | — | не реализован | not run | То же |
| TC-MAN-001 | — | — | manual | UI отсутствует |
| TC-MAN-002 | — | — | manual | UI отсутствует, формат N не определён (Q9) |
| TC-MAN-003 | — | — | manual | UI и API отсутствуют |
| TC-MAN-004 | — | — | manual | Исследовательский чартер, оракула нет (Q1, Q5, Q6) |

Решение по TC-UNIT-008: выбран `xfail(strict=True)` с причиной, а не красный тест. Набор остаётся зелёным и не прячет дефект: пока баг есть — XFAIL в отчёте (`-rxXs`), после исправления продукта тест станет XPASS(strict) = FAIL и потребует снять маркер. Ожидание (`== 0.00`) не менялось, продуктовый код не правился. Если команда предпочитает красный тест, достаточно снять декоратор.

## Commands Run

1. `python -m pytest -rxXs` — exit code не показан инструментом; вывод: `18 passed, 1 xfailed in 0.15s`.
2. Первая попытка составного shell-вызова (запись файлов через heredoc + pytest) была отклонена системой разрешений, файлы после этого созданы инструментами Write/Edit; затем pytest запущен одиночной командой (п. 1) успешно.

## Suspected Product Defects

- **TC-UNIT-008 / REQ-8** — `shop.pricing.shipping_cost`: условие `order_subtotal > FREE_SHIPPING_THRESHOLD` вместо `>=`. Для `Decimal("5000.00")` возвращается `300.00`, ожидается `0.00` (ТЗ: «от 5000» включительно). Затронет и TC-API-003 при появлении эндпоинта.

## Allocation Disagreements

Нет. Замечание для ревьюера: API-кейсы (TC-API-001..004) назначены на уровень, для которого в репозитории нет кода; это не несогласие с уровнем, но они не выполнимы до появления эндпоинта.
