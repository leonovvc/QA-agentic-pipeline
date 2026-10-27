# Сводка автотестов — Ценообразование корзины

> Задача: pricing · Язык вывода: ru · Кейсы: docs/qa/pricing/test-cases-*.md

## Профиль стека
- **Язык:** Python (>=3.10), `pyproject.toml`, пакет `shop` в `src/`.
- **Unit-фреймворк:** pytest; конфиг `[tool.pytest.ini_options]` в `pyproject.toml` (`testpaths=["tests"]`, `pythonpath=["src"]`, `addopts="-q"`). Каталог `tests/`, именование `test_*.py`, функции `test_*`, общая фикстура `mug` в `tests/conftest.py`.
- **API-подход:** отдельного API-фреймворка нет; сервиса корзины в репозитории нет (вся логика — чистые функции `shop.pricing`). Для TC-API-001 использован стандартный `urllib` (без новых зависимостей), адрес из `CART_API_URL`.
- **E2E:** не обнаружен, не требуется (E2E-кейсов нет).
- **Запуск:** `python -m pytest`.
- **CI:** конфигурации CI (`.github/workflows`, `.gitlab-ci.yml`) не найдено — тесты нигде автоматически не запускаются. Рекомендация: добавить CI-джоб с `python -m pytest`.
- **Несоответствие конвенции:** существующие тесты — плоские функции без TC ID; новые названы `test_tc_<lvl>_<nnn>_...` с TC ID в имени и докстринге.

## Соответствие кейсов и тестов
| TC | File | Test | Status | Notes |
|---|---|---|---|---|
| TC-UNIT-001 | tests/test_pricing.py | test_tc_unit_001_quantity_boundaries (4 параметра: 0, 1, 20, 21) | passed | |
| TC-UNIT-002 | tests/test_pricing.py | test_tc_unit_002_subtotal_sums_price_times_quantity_over_lines | passed | 348,50 |
| TC-UNIT-003 | tests/test_pricing.py | test_tc_unit_003_shipping_is_charged_just_below_threshold | passed | |
| TC-UNIT-004 | tests/test_pricing.py | test_tc_unit_004_shipping_is_free_exactly_at_threshold | failed | **Предполагаемый дефект продукта**, см. ниже. Ассерт не ослаблен. |
| TC-UNIT-005 | tests/test_pricing.py | test_tc_unit_005_member_discount_decision_table (R1–R4) | passed | |
| TC-API-001 | tests/test_pricing.py | test_tc_api_001_cart_response_has_free_shipping_at_5000 | not run | Пропущен (skip): не задан `CART_API_URL`, сервиса корзины и корзины C1 нет. Результат не подтверждён. |
| TC-MAN-001 | — | — | manual | Исследовательская сессия — не автоматизируется (нет стабильного оракула, отображение/вёрстка). |

## Выполненные команды
- `python -m pytest -p no:cacheprovider -rsxf --ignore=tests/test_pricing_partial.py` → exit 1; `1 failed, 12 passed, 1 skipped` (всего 14 элементов: 12 новых в test_pricing.py из 6 функций + 2 существующих; 12 passed включая 2 существующих, т.е. 10 новых passed).
- `python -m pytest -p no:cacheprovider` (без `--ignore`) → exit 2: ошибка сбора из-за `tests/test_pricing_partial.py` (SyntaxError), см. «Допущения и проблемы».
- Существующие `tests/test_cart_lines.py` (2 теста) проходят.

## Предполагаемые дефекты продукта
- **TC-UNIT-004 / REQ-3:** ТЗ п. 3 — «при сумме корзины от 5000 ₽ доставка бесплатная» (включительно), критерий приёмки: 5000 → 0. В `src/shop/pricing.py::shipping_cost` условие `order_subtotal > FREE_SHIPPING_THRESHOLD` (строгое), поэтому при 5000,00 возвращается 300,00 вместо 0,00. Вероятное исправление: `>=`. Код продукта не менялся. TC-API-001 (тот же порог) при наличии сервиса, вероятно, упадёт по той же причине.

## Несогласие с распределением
Нет. (Замечание: TC-API-001 по сути дублирует границу TC-UNIT-004 и требует отсутствующий в репозитории сервис — на усмотрение ревьюера.)

## Допущения и проблемы
- **Не удалось удалить `tests/test_pricing_partial.py`:** файловая система каталога `tests/` из Bash доступна только для чтения (`rm` — Read-only file system), создавать/удалять файлы через shell нельзя; новый файл создан инструментом записи. Остаток прерванной сессии (синтаксически битый, 7 строк, содержимое не использовалось) нужно удалить вручную: `git rm`/`rm tests/test_pricing_partial.py`. Пока он на месте, полный `pytest` падает на сборке (exit 2).
- A1 (округление half-up, порог до скидки) принято из плана; R1 = 150,00 не различает округление, граничных случаев округления в кейсах нет (Q1 открыт).
- Порог скидки участника в коде включительный (`<` исключает), согласуется с TC-UNIT-005 R1/R3.
- Время и случайность в тестах не используются; тесты независимы по порядку.
- Ревью `qa-doc-reviewer` (с `ai-qa-review`) ещё не проведено — следующий этап.
