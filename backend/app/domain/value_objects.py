from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "EGP"

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __mul__(self, factor: object) -> Money:
        return Money(amount=self.amount * Decimal(str(factor)), currency=self.currency)

    def __neg__(self) -> Money:
        return Money(amount=-self.amount, currency=self.currency)


@dataclass(frozen=True)
class Address:
    street: str = ""
    city: str = ""
    governorate: str = ""
    country: str = "Egypt"
    postal_code: Optional[str] = None


@dataclass(frozen=True)
class ContactInfo:
    phone: str = ""
    email: Optional[str] = None
    address: Optional[Address] = None
