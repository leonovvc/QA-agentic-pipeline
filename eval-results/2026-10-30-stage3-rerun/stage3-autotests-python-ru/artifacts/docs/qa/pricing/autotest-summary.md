# Сводка автотестов — Ценообразование корзины

> Задача: pricing · Кейсы: docs/qa/pricing/test-cases-unit.md, test-cases-api.md, test-cases-manual.md

## Профиль стека

- **Язык:** Python >= 3.10 (`pyproject.toml`), пакет `shop` в `src/shop/`.
- **Unit-фреймворк:** pytest (`[tool.pytest.ini_options]` в `pyproject.toml`: `testpaths = ["tests"]`, `pythonpath = ["src"]`, `addopts = "-q"`). Каталог `tests/`, именование `test_*.py`, функции `test_<поведение>`, общие фикстуры в `tests/conftest.py`.
- **API-подход:** не обнаружен. Сервиса корзины (HTTP) в репозитории нет. По умолчанию — стандартная библиотека (`urllib`) внутри pytest, без новых зависимостей.
- **E2E:** не обнаружен, и кейсов этого уровня нет.
- **Как запускать:** `python -m pytest` из корня репозитория.
- **CI:** конфигурации CI (`.github/`, `.gitlab-ci.yml`) нет, тесты нигде автоматически не запускаются.
- **Рекомендация:** добавить CI-джоб с `python -m pytest`; для TC-API-001 нужен стенд сервиса корзины и переменная `CART_API_URL`.

## Допущения

- **A2 (этап 3)** — язык вывода `ru` взят из `output_language` в task-файле. Названия функций на английском, TC ID в имени функции (`test_tc_unit_004_...`) и в докстринге, русские докстринги и сообщения assert.
- **A3 (этап 3)** — TC-API-001 требует сервис по `CART_API_URL`, но в репозитории его нет. Контракт ответа (поле `shipping` в теле JSON) выведен из ожидаемого результата кейса. Без переменной тест пропускается через `skipif`, статус `not run`.
- **A4 (этап 3)** — ожидаемый результат TC-UNIT-004 (5000,00 -> 0,00) соответствует ТЗ п. 3 («от 5000 ₽») и принят как оракул. Утверждение не подгонялось под текущее поведение кода.

## Соответствие кейсов и тестов

| TC | File | Test | Status | Notes |
|---|---|---|---|---|
| TC-UNIT-001 | tests/test_pricing_rules.py | test_tc_unit_001_quantity_valid_only_from_1_to_20 | passed | параметризация 0, 1, 20, 21: 4 прогона |
| TC-UNIT-002 | tests/test_pricing_rules.py | test_tc_unit_002_subtotal_sums_price_times_quantity_over_lines | passed | 348,50 |
| TC-UNIT-003 | tests/test_pricing_rules.py | test_tc_unit_003_shipping_is_paid_just_below_threshold | passed | |
| TC-UNIT-004 | tests/test_pricing_rules.py | test_tc_unit_004_shipping_is_free_exactly_at_threshold | failed | **предполагаемый дефект продукта**, см. ниже. Ожидалось 0,00, получено 300,00 |
| TC-UNIT-005 | tests/test_pricing_rules.py | test_tc_unit_005_member_discount_decision_table | passed | правила R1-R4: 4 прогона |
| TC-API-001 | tests/test_cart_api.py | test_tc_api_001_cart_with_5000_subtotal_has_free_shipping | not run | не задан `CART_API_URL`, сервиса корзины в репозитории нет; тест пропущен (skipped), а не пройден |
| TC-MAN-001 | — | — | manual | исследовательский чартер, не автоматизируется |

## Выполненные команды

| Команда | Код выхода | Результат |
|---|---|---|
| `python -m pytest` (первый прогон, до добавления тестов) | 0 | 2 passed (существующие `test_cart_lines.py`) |
| `python -m pytest -rsf -p no:cacheprovider` | 1 | 12 passed, 1 failed (TC-UNIT-004), 1 skipped (TC-API-001) |

`-p no:cacheprovider` нужен только потому, что в среде запуска каталог репозитория был недоступен для записи из shell.

## Предполагаемые дефекты продукта

- **TC-UNIT-004 / REQ-3** — `src/shop/pricing.py::shipping_cost` использует строгое сравнение `order_subtotal > FREE_SHIPPING_THRESHOLD`. При сумме ровно 5000,00 возвращается 300,00, а по ТЗ («от 5000 ₽») и по кейсу должно быть 0,00. Вероятное исправление: `>=`. Код продукта не менялся, тест остаётся падающим. Это и есть граничный случай, под который кейс P0 был создан. Если TC-API-001 заработает на стенде, он, вероятно, выявит то же расхождение.

## Несогласие с распределением

Нет. Замечание для ревьюера: TC-API-001 помечен как API-кейс, но целевого сервиса в репозитории нет. Для запуска нужен стенд, это вопрос окружения, а не уровня.
