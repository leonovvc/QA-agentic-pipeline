"""Cart pricing rules: quantity limits, subtotal, shipping, member discount."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

MIN_QUANTITY = 1
MAX_QUANTITY = 20
SHIPPING_COST = Decimal("300.00")
FREE_SHIPPING_THRESHOLD = Decimal("5000.00")
MEMBER_DISCOUNT_RATE = Decimal("0.05")
MEMBER_DISCOUNT_THRESHOLD = Decimal("3000.00")
CENT = Decimal("0.01")


@dataclass(frozen=True)
class CartLine:
    sku: str
    price: Decimal
    quantity: int


def is_valid_quantity(quantity: int) -> bool:
    return MIN_QUANTITY <= quantity <= MAX_QUANTITY


def subtotal(lines: list[CartLine]) -> Decimal:
    return sum((line.price * line.quantity for line in lines), Decimal("0.00"))


def shipping_cost(order_subtotal: Decimal) -> Decimal:
    if order_subtotal > FREE_SHIPPING_THRESHOLD:
        return Decimal("0.00")
    return SHIPPING_COST


def member_discount(order_subtotal: Decimal, is_member: bool, is_sale_period: bool) -> Decimal:
    if not is_member or is_sale_period or order_subtotal < MEMBER_DISCOUNT_THRESHOLD:
        return Decimal("0.00")
    return (order_subtotal * MEMBER_DISCOUNT_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
