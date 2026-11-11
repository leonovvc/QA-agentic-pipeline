# Тест-кейсы: API — cart-pricing-f9ae3c

Все кейсы этого файла — **нет реализации**: в репозитории нет обработчика `POST /api/cart/price`. Кейсы спроектированы по контракту допущений A12–A13 (Stage 2) и подлежат автоматизации после появления обработчика. Базовая форма запроса (A12):
`{"lines": [{"sku": "...", "price": "...", "quantity": N}], "is_member": bool, "is_sale_period": bool}`. Суммы сравниваются как десятичные значения с 2 знаками после запятой, независимо от JSON-типа (A9). Бизнес-правила проверены на unit-уровне (`test-cases-unit.md`); здесь — контракт, склейка флагов и итог.

### TC-API-001: Не участник, сумма 1000.00 → итог 1300.00
- **Traces:** REQ-12, REQ-13, REQ-14, A6
- **Technique:** Decision table — колонка "скидки нет, доставка платная"
- **Level:** API — проверяется контракт запроса/ответа и сборка итога из трёх правил
- **Priority:** P0
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис с `POST /api/cart/price` запущен; аутентификация и лимиты в тесте не используются (A15)
- **Test data:** `{"lines": [{"sku": "MUG-01", "price": "450.00", "quantity": 2}, {"sku": "PEN-02", "price": "100.00", "quantity": 1}], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** `200`; тело содержит ровно поля `subtotal = 1000.00`, `discount = 0.00`, `shipping = 300.00`, `total = 1300.00`

### TC-API-002: Участник, сумма 3000.00 → скидка 150.00, итог 3150.00
- **Traces:** REQ-9, REQ-12, A3, A6
- **Technique:** Decision table — колонка "скидка есть, доставка платная"; Boundary value analysis — сумма, threshold (3000.00)
- **Level:** API — проверяется, что флаг `is_member` из тела доходит до правила и скидка вычитается до прибавления доставки
- **Priority:** P0
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис с `POST /api/cart/price` запущен
- **Test data:** `{"lines": [{"sku": "TEA-03", "price": "1000.00", "quantity": 3}], "is_member": true, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** `200`; `subtotal = 3000.00`, `discount = 150.00`, `shipping = 300.00`, `total = 3150.00`

### TC-API-003: Участник, сумма 5100.00 — порог доставки до или после скидки (зависит от Q2)
- **Traces:** REQ-8, REQ-12, A1, Q2
- **Technique:** Decision table — колонка "скидка есть, сумма ≥ 5000 до скидки и < 5000 после скидки"
- **Level:** API — различие видно только в собранном ответе: итоговый `shipping` зависит от порядка правил
- **Priority:** P0
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q2: ожидание по A1 (порог проверяется по сумме до скидки)
- **Test data:** `{"lines": [{"sku": "LAMP-05", "price": "1020.00", "quantity": 5}], "is_member": true, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** `200`; `subtotal = 5100.00`, `discount = 255.00`, `shipping = 0.00`, `total = 4845.00`. Если Q2 будет решён как «после скидки»: `shipping = 300.00`, `total = 5145.00`

### TC-API-004: Не участник, сумма ровно 5000.00 → доставка 0.00 (зависит от Q11)
- **Traces:** REQ-8, REQ-12, A14, Q11
- **Technique:** Boundary value analysis — сумма, threshold (5000.00), включительно
- **Level:** API — проверяет границу на сквозном контракте, а не на отдельной функции
- **Priority:** P0
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q11: ожидание следует ТЗ, не текущему коду
- **Test data:** `{"lines": [{"sku": "BOX-09", "price": "1000.00", "quantity": 5}], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** `200`; `subtotal = 5000.00`, `discount = 0.00`, `shipping = 0.00`, `total = 5000.00`

### TC-API-005: Участник, сумма 4999.99 → скидка 250.00, доставка 300.00, итог 5049.99
- **Traces:** REQ-8, REQ-9, REQ-11, A4, A6
- **Technique:** Boundary value analysis — сумма, threshold−0.01 (4999.99) с одновременной скидкой
- **Level:** API — округление 249.9995 → 250.00 и платная доставка проверяются в одном ответе
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен
- **Test data:** `{"lines": [{"sku": "SAFE-10", "price": "4999.99", "quantity": 1}], "is_member": true, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** `200`; `subtotal = 4999.99`, `discount = 250.00`, `shipping = 300.00`, `total = 5049.99`

### TC-API-006: Пустой список строк → все суммы 0.00 (зависит от Q3)
- **Traces:** REQ-5, REQ-12, A2, Q3
- **Technique:** Boundary value analysis — число строк, min (0)
- **Level:** API — поведение пустой корзины в ответе API задано только допущением, проверяется на контракте
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q3: ожидание по A2
- **Test data:** `{"lines": [], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** `200`; `subtotal = 0.00`, `discount = 0.00`, `shipping = 0.00`, `total = 0.00`. Если Q3 решён «по формуле п.5»: `shipping = 300.00`, `total = 300.00`

### TC-API-007: Количество 0 отклоняется, цены в ответе нет (зависит от Q4, A7)
- **Traces:** REQ-1, REQ-2, REQ-16, A7, A13, Q4
- **Technique:** Boundary value analysis — `quantity`, min−1 (0)
- **Level:** API — правило применяется на сервере (A7), контракт ошибки — часть API
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q4 и Q1: точный статус и текст ошибки не заданы, ожидание по A13
- **Test data:** `{"lines": [{"sku": "MUG-01", "price": "450.00", "quantity": 0}], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** статус в диапазоне `400–499`; тело JSON с непустым текстовым сообщением об ошибке; в теле нет полей `subtotal` и `total`

### TC-API-008: Количество 21 отклоняется (зависит от Q4, A7)
- **Traces:** REQ-1, REQ-2, REQ-16, A7, A13, Q4
- **Technique:** Boundary value analysis — `quantity`, max+1 (21)
- **Level:** API — правило применяется на сервере (A7), контракт ошибки — часть API
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q4 и Q1: ожидание по A13
- **Test data:** `{"lines": [{"sku": "MUG-01", "price": "450.00", "quantity": 21}], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** статус в диапазоне `400–499`; тело JSON с непустым текстовым сообщением об ошибке; в теле нет полей `subtotal` и `total`

### TC-API-009: Отрицательное количество не уменьшает итог
- **Traces:** REQ-1, REQ-16, A7, A13, Q1
- **Technique:** Security negative — OWASP A04 (злоупотребление бизнес-логикой: отрицательное количество)
- **Level:** API — защита применяется на сервере, клиентскую проверку обойти прямым вызовом
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q1: ожидание по A13
- **Test data:** `{"lines": [{"sku": "TEA-03", "price": "1000.00", "quantity": 1}, {"sku": "PEN-02", "price": "100.00", "quantity": -1}], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** статус в диапазоне `400–499`; в теле нет полей `subtotal` и `total`; ответ `200` с `subtotal = 900.00` недопустим

### TC-API-010: Отрицательная цена не уменьшает итог
- **Traces:** REQ-13, REQ-16, A13, Q1
- **Technique:** Security negative — OWASP A04 (злоупотребление бизнес-логикой: отрицательная цена)
- **Level:** API — валидация цены, приходящей из тела запроса, выполняется на сервере
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q1 (допустимые значения `price`) и Q8: ожидание по A13
- **Test data:** `{"lines": [{"sku": "TEA-03", "price": "1000.00", "quantity": 1}, {"sku": "PEN-02", "price": "-100.00", "quantity": 1}], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** статус в диапазоне `400–499`; в теле нет полей `subtotal` и `total`; ответ `200` с `subtotal = 900.00` недопустим

### TC-API-011: Нецелое количество 1.5 отклоняется
- **Traces:** REQ-13, REQ-16, A5, A13, Q1
- **Technique:** Equivalence partitioning — invalid class "нецелое количество"
- **Level:** API — проверка типа поля тела запроса, контракт на уровне API
- **Priority:** P2
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q1: ожидание по A5 и A13
- **Test data:** `{"lines": [{"sku": "MUG-01", "price": "450.00", "quantity": 1.5}], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** статус в диапазоне `400–499`; в теле нет полей `subtotal` и `total`

### TC-API-012: Отсутствующие флаги трактуются как false
- **Traces:** REQ-13, A5, Q1
- **Technique:** Equivalence partitioning — valid class "необязательные флаги опущены"
- **Level:** API — значения по умолчанию для полей запроса — контракт API
- **Priority:** P2
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q1: ожидание по A5
- **Test data:** `{"lines": [{"sku": "TEA-03", "price": "1000.00", "quantity": 3}]}` (поля `is_member`, `is_sale_period` отсутствуют)
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** `200`; `subtotal = 3000.00`, `discount = 0.00`, `shipping = 300.00`, `total = 3300.00`

### TC-API-013: Участник в распродажу при сумме 4000.00 → скидка 0.00, итог 4300.00
- **Traces:** REQ-10, REQ-13
- **Technique:** Decision table — правило R2 (участник = да, распродажа = да, сумма ≥ 3000)
- **Level:** API — одна проверка склейки флага `is_sale_period`; сам расчёт покрыт на unit-уровне (TC-UNIT-016)
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен
- **Test data:** `{"lines": [{"sku": "BOX-09", "price": "1000.00", "quantity": 4}], "is_member": true, "is_sale_period": true}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** `200`; `subtotal = 4000.00`, `discount = 0.00`, `shipping = 300.00`, `total = 4300.00`

### TC-API-014: Инъекция в `sku` не вызывает 5xx и не раскрывает внутренности
- **Traces:** REQ-13, REQ-16, Q1
- **Technique:** Security negative — OWASP A03 (вредоносный ввод в `sku`: SQL и HTML)
- **Level:** API — обработка ввода выполняется на сервере
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q1: правила валидации `sku` не заданы, допустимы два исхода
- **Test data:** `{"lines": [{"sku": "'; DROP TABLE carts;--<script>alert(1)</script>", "price": "100.00", "quantity": 1}], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** либо статус `200` с `subtotal = 100.00`, `total = 400.00`, либо статус `400–499`; статус `5xx` недопустим; тело не содержит подстрок `Traceback`, `SQL`, `<script>`

### TC-API-015: Некорректный JSON отклоняется без раскрытия внутренностей
- **Traces:** REQ-16, A13, Q1
- **Technique:** Equivalence partitioning — invalid class "тело не является JSON"
- **Level:** API — ответ на некорректный запрос — часть контракта эндпоинта
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен. Зависит от Q1: формат тела ошибки не определён, ожидание по A13
- **Test data:** тело `{"lines": [` (оборванный JSON), заголовок `Content-Type: application/json`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** статус в диапазоне `400–499`; тело содержит непустое текстовое сообщение об ошибке и не содержит подстрок `Traceback` и путей к файлам (`.py`)

### TC-API-016: Количество 20 принимается, итог 4299.80
- **Traces:** REQ-1, REQ-4
- **Technique:** Boundary value analysis — `quantity`, max (20)
- **Level:** API — принятие верхней границы на сервере (A7) вместе с расчётом на ненулевых копейках
- **Priority:** P1
- **Preconditions:** [НЕТ РЕАЛИЗАЦИИ] Сервис запущен
- **Test data:** `{"lines": [{"sku": "CAB-11", "price": "199.99", "quantity": 20}], "is_member": false, "is_sale_period": false}`
- **Steps:**
  1. Отправить `POST /api/cart/price` с телом из тестовых данных
- **Expected result:** `200`; `subtotal = 3999.80`, `discount = 0.00`, `shipping = 300.00`, `total = 4299.80`
