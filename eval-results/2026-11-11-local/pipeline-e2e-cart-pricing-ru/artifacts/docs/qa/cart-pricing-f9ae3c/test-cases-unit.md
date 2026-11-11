# Тест-кейсы: unit — cart-pricing-f9ae3c

Файл-заголовок: кейсы построены по `docs/qa/cart-pricing-f9ae3c/spec-source.md` (ТЗ v1.2) и `spec-gap-report.md`. Тестируется модуль `src/shop/pricing.py` (чистые функции, без I/O). Суммы — `decimal.Decimal`.
Кейс TC-UNIT-007 частично уже покрыт существующим `tests/test_cart_lines.py::test_subtotal_of_empty_cart_is_zero`.

### TC-UNIT-001: Количество 0 отклоняется (нижняя граница − 1)
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`, min−1 (0)
- **Level:** Unit — чистая функция `is_valid_quantity`, I/O нет
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется; внешнего состояния нет
- **Test data:** `quantity = 0`
- **Steps:**
  1. Вызвать `is_valid_quantity(0)`
- **Expected result:** возвращается `False`

### TC-UNIT-002: Количество 1 допустимо (нижняя граница)
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`, min (1)
- **Level:** Unit — чистая функция `is_valid_quantity`, I/O нет
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется; внешнего состояния нет
- **Test data:** `quantity = 1`
- **Steps:**
  1. Вызвать `is_valid_quantity(1)`
- **Expected result:** возвращается `True`

### TC-UNIT-003: Количество 20 допустимо (верхняя граница включительно)
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`, max (20)
- **Level:** Unit — чистая функция `is_valid_quantity`, I/O нет
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется; внешнего состояния нет
- **Test data:** `quantity = 20`
- **Steps:**
  1. Вызвать `is_valid_quantity(20)`
- **Expected result:** возвращается `True`

### TC-UNIT-004: Количество 21 отклоняется (верхняя граница + 1)
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`, max+1 (21)
- **Level:** Unit — чистая функция `is_valid_quantity`, I/O нет
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется; внешнего состояния нет
- **Test data:** `quantity = 21`
- **Steps:**
  1. Вызвать `is_valid_quantity(21)`
- **Expected result:** возвращается `False`

### TC-UNIT-005: Отрицательное количество −1 отклоняется
- **Traces:** REQ-1
- **Technique:** Equivalence partitioning — invalid class "отрицательное количество"
- **Level:** Unit — чистая функция `is_valid_quantity`, I/O нет
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется; внешнего состояния нет
- **Test data:** `quantity = -1`
- **Steps:**
  1. Вызвать `is_valid_quantity(-1)`
- **Expected result:** возвращается `False`

### TC-UNIT-006: Сумма корзины по нескольким строкам = Σ цена × количество
- **Traces:** REQ-4
- **Technique:** Equivalence partitioning — valid class "несколько строк"
- **Level:** Unit — чистая функция `subtotal`, I/O нет
- **Priority:** P0
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** строка 1 `CartLine("MUG-01", Decimal("450.00"), 3)`; строка 2 `CartLine("PEN-02", Decimal("199.99"), 2)`
- **Steps:**
  1. Вызвать `subtotal([строка 1, строка 2])`
- **Expected result:** возвращается `Decimal("1749.98")` (1350.00 + 399.98)

### TC-UNIT-007: Сумма пустой корзины равна 0.00
- **Traces:** REQ-5, A2
- **Technique:** Boundary value analysis — число строк, min (0)
- **Level:** Unit — чистая функция `subtotal`, I/O нет
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `lines = []`
- **Steps:**
  1. Вызвать `subtotal([])`
- **Expected result:** возвращается `Decimal("0.00")`

### TC-UNIT-008: Сумма сохраняет копейки без потери точности
- **Traces:** REQ-4, REQ-19
- **Technique:** Equivalence partitioning — valid class "цена с копейками"
- **Level:** Unit — чистая функция `subtotal`; проверка Decimal-арифметики без float
- **Priority:** P2
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `CartLine("CAB-11", Decimal("199.99"), 3)`
- **Steps:**
  1. Вызвать `subtotal([CartLine("CAB-11", Decimal("199.99"), 3)])`
- **Expected result:** возвращается `Decimal("599.97")`, ровно 2 знака после запятой

### TC-UNIT-009: Доставка при сумме 1000.00 стоит 300.00
- **Traces:** REQ-7
- **Technique:** Equivalence partitioning — valid class "сумма ниже порога бесплатной доставки"
- **Level:** Unit — чистая функция `shipping_cost`, I/O нет
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `order_subtotal = Decimal("1000.00")`
- **Steps:**
  1. Вызвать `shipping_cost(Decimal("1000.00"))`
- **Expected result:** возвращается `Decimal("300.00")`

### TC-UNIT-010: Доставка при сумме 4999.99 стоит 300.00 (порог − 0.01)
- **Traces:** REQ-8
- **Technique:** Boundary value analysis — сумма, threshold−0.01 (4999.99)
- **Level:** Unit — чистая функция `shipping_cost`, I/O нет
- **Priority:** P0
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `order_subtotal = Decimal("4999.99")`
- **Steps:**
  1. Вызвать `shipping_cost(Decimal("4999.99"))`
- **Expected result:** возвращается `Decimal("300.00")`

### TC-UNIT-011: Доставка при сумме ровно 5000.00 бесплатна (по ТЗ; зависит от Q11)
- **Traces:** REQ-8, A14, Q11
- **Technique:** Boundary value analysis — сумма, threshold (5000.00), включительно
- **Level:** Unit — чистая функция `shipping_cost`, I/O нет
- **Priority:** P0
- **Preconditions:** Модуль `shop.pricing` импортируется. Зависит от Q11: ожидание выведено из ТЗ («от 5000 ₽» включительно), не из кода
- **Test data:** `order_subtotal = Decimal("5000.00")`
- **Steps:**
  1. Вызвать `shipping_cost(Decimal("5000.00"))`
- **Expected result:** возвращается `Decimal("0.00")`. Текущий код (`> 5000`) вернёт `300.00` — падение кейса фиксируется как подозреваемый дефект продукта/расхождение ТЗ и кода, а не как дефект теста

### TC-UNIT-012: Доставка при сумме 5000.01 бесплатна (порог + 0.01)
- **Traces:** REQ-8
- **Technique:** Boundary value analysis — сумма, threshold+0.01 (5000.01)
- **Level:** Unit — чистая функция `shipping_cost`, I/O нет
- **Priority:** P0
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `order_subtotal = Decimal("5000.01")`
- **Steps:**
  1. Вызвать `shipping_cost(Decimal("5000.01"))`
- **Expected result:** возвращается `Decimal("0.00")`

### TC-UNIT-013: Участник без распродажи при сумме ровно 3000.00 получает скидку 150.00
- **Traces:** REQ-9, A3
- **Technique:** Decision table — правило R1 (участник = да, распродажа = нет, сумма ≥ 3000); Boundary value analysis — сумма, threshold (3000.00)
- **Level:** Unit — чистая функция `member_discount`, I/O нет
- **Priority:** P0
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `order_subtotal = Decimal("3000.00")`, `is_member = True`, `is_sale_period = False`
- **Steps:**
  1. Вызвать `member_discount(Decimal("3000.00"), True, False)`
- **Expected result:** возвращается `Decimal("150.00")`

### TC-UNIT-014: Участник при сумме 2999.99 скидку не получает (порог − 0.01)
- **Traces:** REQ-9, A3
- **Technique:** Decision table — правило R4 (участник = да, распродажа = нет, сумма < 3000); Boundary value analysis — сумма, threshold−0.01 (2999.99)
- **Level:** Unit — чистая функция `member_discount`, I/O нет
- **Priority:** P0
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `order_subtotal = Decimal("2999.99")`, `is_member = True`, `is_sale_period = False`
- **Steps:**
  1. Вызвать `member_discount(Decimal("2999.99"), True, False)`
- **Expected result:** возвращается `Decimal("0.00")`

### TC-UNIT-015: Не участник при сумме 10000.00 скидку не получает
- **Traces:** REQ-9
- **Technique:** Decision table — правило R3 (участник = нет; остальные условия не важны)
- **Level:** Unit — чистая функция `member_discount`, I/O нет
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `order_subtotal = Decimal("10000.00")`, `is_member = False`, `is_sale_period = False`
- **Steps:**
  1. Вызвать `member_discount(Decimal("10000.00"), False, False)`
- **Expected result:** возвращается `Decimal("0.00")`

### TC-UNIT-016: Участник в период распродажи скидку не получает
- **Traces:** REQ-10
- **Technique:** Decision table — правило R2 (участник = да, распродажа = да, сумма ≥ 3000)
- **Level:** Unit — чистая функция `member_discount`, I/O нет
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `order_subtotal = Decimal("10000.00")`, `is_member = True`, `is_sale_period = True`
- **Steps:**
  1. Вызвать `member_discount(Decimal("10000.00"), True, True)`
- **Expected result:** возвращается `Decimal("0.00")`

### TC-UNIT-017: Скидка 150.005 округляется half-up до 150.01 (зависит от Q6)
- **Traces:** REQ-11, A4, Q6
- **Technique:** Equivalence partitioning — класс "дробная часть ровно половина копейки"
- **Level:** Unit — чистая функция `member_discount`; округление — внутренняя логика функции
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется. Зависит от Q6: режим half-up принят по A4; при банковском округлении ожидалось бы `150.00`
- **Test data:** `order_subtotal = Decimal("3000.10")` (3000.10 × 0.05 = 150.0050), `is_member = True`, `is_sale_period = False`
- **Steps:**
  1. Вызвать `member_discount(Decimal("3000.10"), True, False)`
- **Expected result:** возвращается `Decimal("150.01")`

### TC-UNIT-018: Скидка 150.0045 округляется вниз до 150.00
- **Traces:** REQ-11, A4, Q6
- **Technique:** Equivalence partitioning — класс "дробная часть меньше половины копейки"
- **Level:** Unit — чистая функция `member_discount`; округление — внутренняя логика функции
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется. Зависит от Q6 (режим округления)
- **Test data:** `order_subtotal = Decimal("3000.09")` (3000.09 × 0.05 = 150.0045), `is_member = True`, `is_sale_period = False`
- **Steps:**
  1. Вызвать `member_discount(Decimal("3000.09"), True, False)`
- **Expected result:** возвращается `Decimal("150.00")`
