"""
GOAL / INTENT
-------------
Draw the abstraction barriers in a real module and identify precisely what crosses each one. A "barrier" separates code that depends on a representation from code that only depends on the meaning of the operations above it. This file gives you a small module with three layers on purpose:

    Layer 3: programs that use money            (never sees cents or currency fields)
    ---------------------------------------------------------- barrier
    Layer 2: money operations (add, multiply, compare)
    ---------------------------------------------------------- barrier
    Layer 1: money constructor and selectors (make_money, amount_in_cents, currency_code)
    ---------------------------------------------------------- barrier
    Layer 0: internal representation (the Money dataclass fields)

You will implement Layer 1 and Layer 2, then write a short comment block (inside this file) answering three questions about the barriers you built.


TASK / IMPLEMENTATION
----------------------
Implement every function below. Functions in the "operations" section must be built exclusively out of the constructor/selector section — never touch `_amount_in_cents` or `_currency_code` directly outside Layer 1.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Money:
  """Internal representation — Layer 0. Nothing outside Layer 1 should see these fields."""

  _amount_in_cents: int
  _currency_code: str


# --- Layer 1: constructor and selectors -------------------------------------


def make_money(amount_in_cents: int, currency_code: str) -> Money:
  """Constructor."""
  raise NotImplementedError


def amount_in_cents(money_value: Money) -> int:
  """Selector."""
  raise NotImplementedError


def currency_code(money_value: Money) -> str:
  """Selector."""
  raise NotImplementedError


# --- Layer 2: operations, built only from Layer 1 ----------------------------


def add_money(first_amount: Money, second_amount: Money) -> Money:
  """Add two Money values. Raise ValueError if currency codes differ."""
  raise NotImplementedError


def multiply_money_by_scalar(money_value: Money, scalar: int) -> Money:
  """Scale a Money value by an integer factor (e.g. quantity of items)."""
  raise NotImplementedError


def money_to_string(money_value: Money) -> str:
  """e.g. Money(1050, "USD") -> "10.50 USD"."""
  raise NotImplementedError


"""
REAL-WORLD SEQUENCE TASK
-------------------------
You have a list of Money transactions from a single receipt, all in the same currency. Compute the receipt total using only add_money — never by summing `_amount_in_cents` directly. This proves Layer 3 code can process a whole sequence of Money values without ever knowing they're stored as integer cents.
"""


def receipt_total(transactions: list[Money]) -> Money:
  """Sum every transaction on the receipt into a single Money value."""
  raise NotImplementedError


# --- Written exercise (answer here in comments, no code needed) -------------
#
# 1. What data crosses the Layer 1 <-> Layer 2 barrier?
#    (your answer)
#
# 2. If Money's internal representation switched from integer cents to a
#    float dollar amount, which layers would need to change, and which
#    would not?
#    (your answer)
#
# 3. Where would a unit test for "adding two Money values in different
#    currencies raises an error" belong — which layer is it testing against?
#    (your answer)


coffee = make_money(450, "USD")
pastry = make_money(325, "USD")
print(money_to_string(add_money(coffee, pastry)))  # expect 7.75 USD
print(money_to_string(multiply_money_by_scalar(coffee, 3)))  # expect 13.50 USD

receipt = [coffee, pastry, make_money(200, "USD")]
print(money_to_string(receipt_total(receipt)))  # expect 9.75 USD
