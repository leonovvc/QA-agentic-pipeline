# Тест-кейсы уровня Unit — расчёт стоимости корзины (`shop.pricing`)

Задача: cart-pricing-f9ae3c. Тестируемые функции: `is_valid_quantity`, `subtotal`, `shipping_cost`, `member_discount` в `src/shop/pricing.py`. Все суммы — `Decimal`. Существующие тесты `tests/test_cart_lines.py` (пустая корзина, 3 × 450.00) частично покрывают TC-UNIT-003 и TC-UNIT-005: автотест-билдер переиспользует их, не дублируя.

### TC-UNIT-001: Количество на границах допустимого диапазона 1..20 принимается
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`: min (1), min+1 (2), max-1 (19), max (20)
- **Level:** Unit — чистая функция `is_valid_quantity(quantity)`, без ввода-вывода
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется; состояние не требуется
- **Test data:** `quantity` ∈ {1, 2, 19, 20}
- **Steps:**
  1. Вызвать `is_valid_quantity(q)` для каждого значения из тестовых данных → Expected: для каждого значения возвращается `True`
- **Expected result:** Для всех четырёх значений (1, 2, 19, 20) результат строго `True`

### TC-UNIT-002: Количество вне диапазона (0, -1, 21) отклоняется
- **Traces:** REQ-1
- **Technique:** Boundary value analysis — `quantity`: min-1 (0), max+1 (21); equivalence partitioning — класс «отрицательное» (-1)
- **Level:** Unit — чистая функция `is_valid_quantity(quantity)`, без ввода-вывода
- **Priority:** P1
- **Preconditions:** Модуль `shop.pricing` импортируется
- **Test data:** `quantity` ∈ {0, -1, 21}
- **Steps:**
  1. Вызвать `is_valid_quantity(q)` для каждого значения из тестовых данных → Expected: для каждого значения возвращается `False`
- **Expected result:** Для 0, -1 и 21 результат строго `False`

### TC-UNIT-003: Сумма корзины из нескольких строк равна сумме «цена × количество»
- **Traces:** REQ-4
- **Technique:** Equivalence partitioning — класс «несколько строк с разными ценами и количествами»
- **Level:** Unit — чистая функция `subtotal(lines)`, без ввода-вывода
- **Priority:** P1
- **Preconditions:** Нет
- **Test data:** строка 1: `sku="MUG-01"`, `price=450.00`, `quantity=3`; строка 2: `sku="PEN-02"`, `price=1200.50`, `quantity=2`
- **Steps:**
  1. Вызвать `subtotal([строка 1, строка 2])` → Expected: возвращается `Decimal("3751.00")` (1350.00 + 2401.00)
- **Expected result:** `subtotal(...) == Decimal("3751.00")`

### TC-UNIT-004: Один и тот же sku в двух строках суммируется как две отдельные строки
- **Traces:** REQ-4, A4
- **Technique:** Equivalence partitioning — класс «дубль sku в разных строках»
- **Level:** Unit — чистая функция `subtotal(lines)`; правило агрегации без ввода-вывода
- **Priority:** P2
- **Preconditions:** Нет
- **Test data:** две строки `sku="MUG-01"`, `price=450.00`, `quantity=20` каждая
- **Steps:**
  1. Вызвать `subtotal([строка, строка])` → Expected: возвращается `Decimal("18000.00")`
- **Expected result:** `subtotal(...) == Decimal("18000.00")`; (допущение A4: каждая строка проверяется отдельно, итог — сумма; ограничение на суммарное количество не утверждается — Q8)

### TC-UNIT-005: Сумма пустой корзины равна 0.00
- **Traces:** REQ-5, A3
- **Technique:** Boundary value analysis — размер корзины: 0 строк
- **Level:** Unit — чистая функция `subtotal(lines)`, без ввода-вывода
- **Priority:** P3
- **Preconditions:** Нет
- **Test data:** `lines = []`
- **Steps:**
  1. Вызвать `subtotal([])` → Expected: возвращается `Decimal("0.00")`
- **Expected result:** `subtotal([]) == Decimal("0.00")`; значения `shipping`/`total` для пустой корзины не проверяются (Q2)

### TC-UNIT-006: Сумма 1000.00 ниже порога — доставка 300.00
- **Traces:** REQ-7
- **Technique:** Equivalence partitioning — класс «сумма < 5000, платная доставка»
- **Level:** Unit — чистая функция `shipping_cost(order_subtotal)`, без ввода-вывода
- **Priority:** P2
- **Preconditions:** Нет
- **Test data:** `order_subtotal = Decimal("1000.00")`
- **Steps:**
  1. Вызвать `shipping_cost(Decimal("1000.00"))` → Expected: возвращается `Decimal("300.00")`
- **Expected result:** `shipping_cost(...) == Decimal("300.00")`

### TC-UNIT-007: Сумма 4999.99 (чуть ниже порога) — доставка платная 300.00
- **Traces:** REQ-8
- **Technique:** Boundary value analysis — порог бесплатной доставки 5000.00, значение max-1 (4999.99)
- **Level:** Unit — чистая функция `shipping_cost(order_subtotal)`, без ввода-вывода
- **Priority:** P0
- **Preconditions:** Нет
- **Test data:** `order_subtotal = Decimal("4999.99")`
- **Steps:**
  1. Вызвать `shipping_cost(Decimal("4999.99"))` → Expected: возвращается `Decimal("300.00")`
- **Expected result:** `shipping_cost(...) == Decimal("300.00")`

### TC-UNIT-008: Сумма ровно 5000.00 — доставка бесплатная 0.00 (граница включительно)
- **Traces:** REQ-8
- **Technique:** Boundary value analysis — порог бесплатной доставки, значение на границе (5000.00, «от 5000» включительно)
- **Level:** Unit — чистая функция `shipping_cost(order_subtotal)`, без ввода-вывода
- **Priority:** P0
- **Preconditions:** Нет
- **Test data:** `order_subtotal = Decimal("5000.00")`
- **Steps:**
  1. Вызвать `shipping_cost(Decimal("5000.00"))` → Expected: возвращается `Decimal("0.00")`
- **Expected result:** `shipping_cost(...) == Decimal("0.00")`. Примечание для исполнителя: текущая реализация сравнивает `>` вместо `>=`, поэтому ожидается падение — предполагаемый дефект продукта

### TC-UNIT-009: Участник при сумме ровно 3000.00 получает скидку 150.00 (граница включительно)
- **Traces:** REQ-9
- **Technique:** Decision table — правило R1 (участник = да, распродажа = нет, сумма ≥ 3000); Boundary value analysis — 3000.00
- **Level:** Unit — чистая функция `member_discount(...)`, без ввода-вывода
- **Priority:** P1
- **Preconditions:** Нет
- **Test data:** `order_subtotal = Decimal("3000.00")`, `is_member = True`, `is_sale_period = False`
- **Steps:**
  1. Вызвать `member_discount(Decimal("3000.00"), True, False)` → Expected: возвращается `Decimal("150.00")`
- **Expected result:** `member_discount(...) == Decimal("150.00")` (3000.00 × 5%)

### TC-UNIT-010: Участник при сумме 2999.99 скидку не получает
- **Traces:** REQ-9
- **Technique:** Decision table — правило R4 (участник = да, сумма < 3000); Boundary value analysis — 2999.99 (min-1)
- **Level:** Unit — чистая функция `member_discount(...)`, без ввода-вывода
- **Priority:** P1
- **Preconditions:** Нет
- **Test data:** `order_subtotal = Decimal("2999.99")`, `is_member = True`, `is_sale_period = False`
- **Steps:**
  1. Вызвать `member_discount(Decimal("2999.99"), True, False)` → Expected: возвращается `Decimal("0.00")`
- **Expected result:** `member_discount(...) == Decimal("0.00")`

### TC-UNIT-011: Не участник при сумме 4000.00 скидку не получает
- **Traces:** REQ-9
- **Technique:** Decision table — правило R3 (участник = нет)
- **Level:** Unit — чистая функция `member_discount(...)`, без ввода-вывода
- **Priority:** P2
- **Preconditions:** Нет
- **Test data:** `order_subtotal = Decimal("4000.00")`, `is_member = False`, `is_sale_period = False`
- **Steps:**
  1. Вызвать `member_discount(Decimal("4000.00"), False, False)` → Expected: возвращается `Decimal("0.00")`
- **Expected result:** `member_discount(...) == Decimal("0.00")`

### TC-UNIT-012: В период распродажи скидка участника равна 0.00
- **Traces:** REQ-10, A8
- **Technique:** Decision table — правило R2 (участник = да, распродажа = да, сумма ≥ 3000)
- **Level:** Unit — чистая функция `member_discount(...)`, без ввода-вывода
- **Priority:** P1
- **Preconditions:** Нет
- **Test data:** `order_subtotal = Decimal("4000.00")`, `is_member = True`, `is_sale_period = True`
- **Steps:**
  1. Вызвать `member_discount(Decimal("4000.00"), True, True)` → Expected: возвращается `Decimal("0.00")`
- **Expected result:** `member_discount(...) == Decimal("0.00")` (без распродажи было бы 200.00)

### TC-UNIT-013: Скидка 150.005 округляется «половина вверх» до 150.01
- **Traces:** REQ-11, A1
- **Technique:** Equivalence partitioning — класс «половинное значение копейки»; зависит от допущения A1 (Q3)
- **Level:** Unit — чистая функция `member_discount(...)`; округление не требует ввода-вывода
- **Priority:** P1
- **Preconditions:** Нет
- **Test data:** `order_subtotal = Decimal("3000.10")`, `is_member = True`, `is_sale_period = False` (3000.10 × 0.05 = 150.005; банковское округление дало бы 150.00)
- **Steps:**
  1. Вызвать `member_discount(Decimal("3000.10"), True, False)` → Expected: возвращается `Decimal("150.01")`
- **Expected result:** `member_discount(...) == Decimal("150.01")`; если Q3 будет решён иначе, кейс пересматривается
