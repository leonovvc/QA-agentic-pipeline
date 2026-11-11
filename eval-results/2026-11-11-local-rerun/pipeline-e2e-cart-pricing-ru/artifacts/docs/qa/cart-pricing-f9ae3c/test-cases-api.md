# Тест-кейсы уровня API — `POST /api/cart/price`

Задача: cart-pricing-f9ae3c. Важно для автотест-билдера: в репозитории нет HTTP-слоя (в `src/shop/` только `pricing.py`) и нет функции «итог», поэтому эти кейсы могут оказаться `not run` до появления эндпоинта. Не подменять их логикой в тесте. Тело запроса: `{"lines": [{"sku","price","quantity"}], "is_member": bool, "is_sale_period": bool}` — имя поля со строками в ТЗ не задано (Q11), используется `lines`.

### TC-API-001: Корректный запрос возвращает четыре суммы с двумя знаками после запятой
- **Traces:** REQ-13, REQ-14, REQ-18, A5
- **Technique:** Equivalence partitioning — валидный запрос, не участник, без скидки (контракт ответа)
- **Level:** API — проверяется контракт запроса и ответа (имена полей, формат сумм) без UI
- **Priority:** P1
- **Preconditions:** Сервис запущен; эндпоинт `POST /api/cart/price` доступен
- **Test data:** `lines = [{"sku": "MUG-01", "price": 500.00, "quantity": 2}]`, `is_member = false`, `is_sale_period = false`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных → Expected: статус `200`, в теле ровно поля `subtotal`, `discount`, `shipping`, `total`
- **Expected result:** `200`; `subtotal = 1000.00`, `discount = 0.00`, `shipping = 300.00`, `total = 1300.00`, каждая сумма имеет два знака после запятой

### TC-API-002: Участник с суммой 3500.00 — скидка 175.00, доставка 300.00, итог 3625.00
- **Traces:** REQ-12, REQ-9
- **Technique:** Decision table — правило R1 (участник = да, распродажа = нет, 3000 ≤ сумма < 5000)
- **Level:** API — итог собирается на сервере (REQ-17), в `pricing.py` нет функции итога, поэтому формула проверяется на контракте
- **Priority:** P0
- **Preconditions:** Сервис запущен
- **Test data:** `lines = [{"sku": "MUG-01", "price": 700.00, "quantity": 5}]`, `is_member = true`, `is_sale_period = false`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных → Expected: статус `200`
- **Expected result:** `subtotal = 3500.00`, `discount = 175.00`, `shipping = 300.00`, `total = 3625.00` (3500.00 − 175.00 + 300.00)

### TC-API-003: Участник с суммой ровно 5000.00 — доставка бесплатна, итог 4750.00
- **Traces:** REQ-12, REQ-8, A2
- **Technique:** Boundary value analysis — порог бесплатной доставки 5000.00 при наличии скидки (порог сравнивается до вычета скидки)
- **Level:** API — проверяется сквозная композиция скидки, порога и итога, которой нет ни в одной unit-функции
- **Priority:** P0
- **Preconditions:** Сервис запущен
- **Test data:** `lines = [{"sku": "MUG-01", "price": 1000.00, "quantity": 5}]`, `is_member = true`, `is_sale_period = false`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных → Expected: статус `200`
- **Expected result:** `subtotal = 5000.00`, `discount = 250.00`, `shipping = 0.00`, `total = 4750.00`. Зависит от допущения A2 (Q10): если порог считается после скидки, ожидание меняется на `shipping = 300.00`

### TC-API-004: Участник в период распродажи — скидка 0.00, итог 4300.00
- **Traces:** REQ-10, REQ-12, A8
- **Technique:** Decision table — правило R2 (участник = да, распродажа = да)
- **Level:** API — проверяется, что флаг `is_sale_period` из тела запроса доходит до расчёта и итог пересчитан
- **Priority:** P1
- **Preconditions:** Сервис запущен
- **Test data:** `lines = [{"sku": "MUG-01", "price": 1000.00, "quantity": 4}]`, `is_member = true`, `is_sale_period = true`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных → Expected: статус `200`
- **Expected result:** `subtotal = 4000.00`, `discount = 0.00`, `shipping = 300.00`, `total = 4300.00`
