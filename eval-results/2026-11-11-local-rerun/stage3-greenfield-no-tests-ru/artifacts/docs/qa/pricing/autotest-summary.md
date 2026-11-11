# Сводка автотестов — Ценообразование корзины

> Задача: pricing · Кейсы: docs/qa/pricing/test-cases-*.md · Язык: ru

## Профиль стека

## Language(s)
Python 3.11 (`requires-python >= 3.10`), пакет `shop` в `src/shop/`, одна тестовая поверхность.

## Unit Test Framework
Не обнаружен (в репозитории не было ни тестов, ни конфигурации). Решение: pytest (уже установлен, 9.2.0), минимальная конфигурация в `pyproject.toml` (`[tool.pytest.ini_options]`: `pythonpath=["src"]`, `testpaths=["tests"]`). Каталог `tests/unit/`, имена `test_*.py`.

## API Test Approach
Не обнаружен. Решение: pytest + стандартный `urllib` (без новых зависимостей), `tests/api/`, маркер `api`. В репозитории нет кода сервиса корзины и OpenAPI — только `CART_API_URL` из кейса.

## E2E Framework
Не обнаружен и не нужен: UI в репозитории нет, E2E-кейсов в плане нет.

## How to Run
`python -m pytest -v -rs` из корня репозитория (для API-теста дополнительно `CART_API_URL=<url>`).

## CI Integration
CI-конфигурации нет. Рекомендация: добавить job с `python -m pytest`; без этого тесты не дают защиты от регрессий.

## Recommendation
Сделано минимальное: pytest-конфиг в `pyproject.toml` и каталог `tests/`. Добавить CI и поднять тестовый стенд сервиса корзины.

## Соответствие кейсов и тестов

| TC | File | Test | Status | Notes |
|---|---|---|---|---|
| TC-UNIT-001 | tests/unit/test_pricing.py | test_is_valid_quantity_accepts_only_1_to_20 (4 параметра) | passed | |
| TC-UNIT-002 | tests/unit/test_pricing.py | test_subtotal_sums_price_times_quantity_over_lines | passed | |
| TC-UNIT-003 | tests/unit/test_pricing.py | test_shipping_is_paid_300_below_free_threshold | passed | |
| TC-UNIT-004 | tests/unit/test_pricing.py | test_shipping_is_free_at_exactly_5000 | failed | Предполагаемый дефект продукта, см. ниже. Утверждение не ослаблялось |
| TC-UNIT-005 | tests/unit/test_pricing.py | test_member_discount_decision_table (R1–R4) | passed | Округление half-up по A1 в кейсе не проверяется отдельно (150,00 — точное значение) |
| TC-API-001 | tests/api/test_cart_api.py | test_cart_with_5000_subtotal_has_free_shipping | not run | Не задан `CART_API_URL`, сервиса корзины и корзины C1 в окружении нет; тест пропущен (skip), а не пройден |
| TC-MAN-001 | — | — | manual | Исследовательский чартер, нет стабильного оракула; автоматизация не нужна |

Оракулы: основной — ожидаемый результат кейса; негативный/данные — для чистых функций избыточны (нет побочных эффектов, `Decimal` сравнивается точно). Названия тестов начинаются/содержат TC-ID в docstring и id параметров (pytest-функции — английские идентификаторы по стандарту).

## Выполненные команды

1. `python -m pytest -v -rs -p no:cacheprovider` — код выхода 1: 10 passed, 1 failed (TC-UNIT-004), 1 skipped (TC-API-001).

(Первая попытка создать файлы через heredoc в составной команде была отклонена парсером оболочки; файлы созданы инструментом записи, тесты не менялись.)

## Предполагаемые дефекты продукта

**BUG-1** — TC-UNIT-004, REQ-3: `shop.pricing.shipping_cost(Decimal("5000.00"))` возвращает `300.00`, ожидается `0.00`. ТЗ п.3: «при сумме корзины **от** 5000 ₽ доставка бесплатная» — граница включена, а в коде `if order_subtotal > FREE_SHIPPING_THRESHOLD` (строгое сравнение). Исправление: `>=`. Тест остаётся красным до исправления. Это же, вероятно, затрагивает TC-API-001 (тот же порог в сервисе корзины), когда его удастся запустить.

## Несогласие с распределением

Нет. Замечание для ревьюера: TC-API-001 заявлен как API, но в репозитории нет сервиса корзины — только чистые функции; кейс не исполним без внешнего стенда.

## Допущения Stage 3

- Выбран pytest и структура `tests/{unit,api}`, т.к. тестовой инфраструктуры не было.
- Граница «от 5000» трактуется как включительная (дословно по ТЗ).
- Тест API пропускается при отсутствии `CART_API_URL`; в отчёте это `not run`, не `passed`.
- Ничего не коммичено; код продукта не менялся.
