"""
GOAL / INTENT
-------------
Build data-directed programming: instead of writing one function per operation that contains a growing if/elif chain checking what type a thing is, store implementations in a table keyed by (operation-name, type-tag), and let a single small apply_generic function look up and call the right implementation, so that adding a new type becomes "install a new row in the table, touch nothing else" instead of "find and edit every dispatch chain in the codebase." The concrete vehicle is a shipping cost and delivery-estimate calculator handling standard parcels, express parcels, and freight pallets — three package types with genuinely different cost formulas — without ever writing an if/elif chain on package type anywhere in the generic layer.

TASK / IMPLEMENTATION
----------------------
Implement every function below. Everything in the REAL-WORLD SEQUENCE TASK must be reached only through put, get, and apply_generic — never by importing or calling an installed package's implementation function directly.
"""

from collections.abc import Callable
import math

type OperationTable = dict[tuple[str, str], Callable[..., object]]

_operation_table: OperationTable = {}


def put(operation_name: str, type_tag: str, implementation: Callable[..., object]) -> None:
  """Installs implementation into the global operation table under the key (operation_name, type_tag), overwriting any prior entry for that exact key."""
  _operation_table[(operation_name, type_tag)] = implementation


def get(operation_name: str, type_tag: str) -> Callable[..., object]:
  """Looks up and returns the implementation installed under (operation_name, type_tag), raising KeyError with a clear message if nothing has been installed for that combination."""
  if (operation_name, type_tag) not in _operation_table:
      raise KeyError(f"No implementation for {operation_name} and {type_tag}")
  return _operation_table[(operation_name, type_tag)]


def type_tag(tagged_package: tuple[str, dict[str, float]]) -> str:
  """Selector. Returns the type tag, the first element, of a tagged package record."""
  return tagged_package[0]


def package_contents(tagged_package: tuple[str, dict[str, float]]) -> dict[str, float]:
  """Selector. Returns the contents dict, the second element, of a tagged package record."""
  return tagged_package[1]


def apply_generic(operation_name: str, tagged_package: tuple[str, dict[str, float]]) -> object:
  """Looks up the implementation for (operation_name, type_tag(tagged_package)) via get(), calls it with package_contents(tagged_package), and returns the result — this is the single dispatch point every generic operation in this file goes through."""
  implementation = get(operation_name, type_tag(tagged_package))
  return implementation(package_contents(tagged_package))


def cost(tagged_package: tuple[str, dict[str, float]]) -> float:
  """Generic shipping cost, in dollars, for any installed package type. Must be implemented as apply_generic('cost', tagged_package) — nothing else."""
  return apply_generic("cost", tagged_package)


def delivery_days(tagged_package: tuple[str, dict[str, float]]) -> int:
  """Generic estimated delivery time, in days, for any installed package type. Must be implemented as apply_generic('delivery-days', tagged_package) — nothing else."""
  return apply_generic("delivery-days", tagged_package)


def install_standard_package() -> None:
  """Installs 'cost' and 'delivery-days' implementations for the 'standard' type tag via put(). A standard package's contents dict has key 'weight_pounds'. Cost formula: $4.00 flat plus $0.50 per pound. Delivery estimate: flat 5 days."""

  def standard_cost(data):
      return 4.0 + 0.5 * data["weight_pounds"]

  def standard_delivery(data):
      return 5

  put("cost", "standard", standard_cost)
  put("delivery-days", "standard", standard_delivery)


def install_express_package() -> None:
  """Installs 'cost' and 'delivery-days' implementations for the 'express' type tag via put(). An express package's contents dict has key 'weight_pounds'. Cost formula: $12.00 flat plus $1.25 per pound. Delivery estimate: flat 2 days."""

  def express_cost(data):
      return 12.0 + 1.25 * data["weight_pounds"]

  def express_delivery(data):
      return 2

  put("cost", "express", express_cost)
  put("delivery-days", "express", express_delivery)


def install_freight_package() -> None:
  """Installs 'cost' and 'delivery-days' implementations for the 'freight' type tag via put(). A freight package's contents dict has keys 'weight_pounds' and 'distance_miles'. Cost formula: weight_pounds * (0.10 + 0.02 * distance_miles). Delivery estimate: 3 days plus 1 additional day per 500 miles of distance_miles, rounded up."""

  def freight_cost(data):
      return data["weight_pounds"] * (0.10 + 0.02 * data["distance_miles"])

  def freight_delivery(data):
      return 3 + math.ceil(data["distance_miles"] / 500)

  put("cost", "freight", freight_cost)
  put("delivery-days", "freight", freight_delivery)


"""
REAL-WORLD SEQUENCE TASK
-------------------------
Install all three package types, then, for a batch of orders waiting to ship, compute each order's cost and delivery estimate using only cost() and delivery_days() — never checking type_tag yourself in this section, and never calling an installed implementation function by name.
"""

install_standard_package()
install_express_package()
install_freight_package()

order_batch: tuple[tuple[str, dict[str, float]], ...] = (
  ("standard", {"weight_pounds": 6.0}),
  ("express", {"weight_pounds": 2.0}),
  ("freight", {"weight_pounds": 800.0, "distance_miles": 1200.0}),
)
order_costs: list[float] = [cost(order) for order in order_batch]
order_delivery_days: list[int] = [delivery_days(order) for order in order_batch]
total_shipping_cost: float = sum(order_costs)

print(get("cost", "standard") is not None)  # expect True
print(cost(("standard", {"weight_pounds": 6.0})))  # expect 7.0
print(delivery_days(("standard", {"weight_pounds": 6.0})))  # expect 5
print(cost(("express", {"weight_pounds": 2.0})))  # expect 14.5
print(delivery_days(("express", {"weight_pounds": 2.0})))  # expect 2
print(cost(("freight", {"weight_pounds": 800.0, "distance_miles": 1200.0})))  # expect 19280.0
print(delivery_days(("freight", {"weight_pounds": 800.0, "distance_miles": 1200.0})))  # expect 6

print(order_costs)  # expect [7.0, 14.5, 19280.0]
print(order_delivery_days)  # expect [5, 2, 6]
print(total_shipping_cost)  # expect 19301.5
