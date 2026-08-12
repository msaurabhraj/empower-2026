"""
GOAL / INTENT
-------------
Build interval arithmetic as a data abstraction (a value paired with its uncertainty range), then use it to define a real list-processing task cleanly over a sequence — never by reaching into an interval's bounds by hand.

TASK / IMPLEMENTATION
----------------------
Implement every function below. Everything after the constructor/selector section must be built exclusively out of make_interval, lower_bound, and upper_bound.
"""

from dataclasses import dataclass
from functools import reduce


@dataclass(frozen=True, slots=True)
class Interval:
  """An interval of possible values, from a lower bound to an upper bound."""

  _lower_bound: float
  _upper_bound: float


def make_interval(lower_value: float, upper_value: float) -> Interval:
  """Constructor. Raise ValueError if lower_value > upper_value."""
  raise NotImplementedError


def lower_bound(interval_value: Interval) -> float:
  """Selector."""
  raise NotImplementedError


def upper_bound(interval_value: Interval) -> float:
  """Selector."""
  raise NotImplementedError


def add_interval(first_interval: Interval, second_interval: Interval) -> Interval:
  raise NotImplementedError


def multiply_interval(first_interval: Interval, second_interval: Interval) -> Interval:
  """Result bounds are the min/max over all four combinations of the input bounds (needed because bounds may be negative)."""
  raise NotImplementedError


def divide_interval(first_interval: Interval, second_interval: Interval) -> Interval:
  """Divide by multiplying by the reciprocal interval. Raise ValueError if second_interval spans zero (i.e. lower_bound <= 0 <= upper_bound)."""
  raise NotImplementedError


def width_of_interval(interval_value: Interval) -> float:
  """Half the distance between the bounds — a measure of uncertainty."""
  raise NotImplementedError


"""
REAL-WORLD SEQUENCE TASK
-------------------------
You are computing the combined resistance of an arbitrary number of resistors wired in parallel, where each resistor's true resistance is only known within a tolerance range (an Interval). The parallel-resistance formula is:

    R_parallel = 1 / (1/R_1 + 1/R_2 + ... + 1/R_n)

Implement this over a list of Interval values, using ONLY the interval operations defined above (no direct access to _lower_bound/_upper_bound).
"""


def parallel_resistance(resistors: list[Interval]) -> Interval:
  """Combine an arbitrary-length list of resistor Intervals into one equivalent-resistance Interval, wired in parallel."""
  raise NotImplementedError


resistor_one = make_interval(9.8, 10.2)
resistor_two = make_interval(19.7, 20.3)

combined = add_interval(resistor_one, resistor_two)
print(lower_bound(combined), upper_bound(combined))  # expect ~29.5, 30.5

result = parallel_resistance([resistor_one, resistor_two])
print(lower_bound(result), upper_bound(result))
print(width_of_interval(result))
