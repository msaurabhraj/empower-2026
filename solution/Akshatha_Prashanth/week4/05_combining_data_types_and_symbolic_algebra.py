"""
GOAL / INTENT
-------------
This is the Month 1 wrap-up exercise. Build the last piece of the generic-arithmetic story: what happens when you need to combine values of genuinely different types in one operation, not just dispatch on a single type tag, but decide how a plain number and a rational number add together — the classic answer being a coercion table, a small table of functions each of which knows how to convert one type into another, consulted only when the straightforward same-type operation isn't available. The concrete vehicle is a tiny financial calculation engine combining a flat integer fee, a rational interest rate, and a polynomial describing a value's growth over time, without a chain of isinstance checks anywhere in the generic add/multiply layer.

TASK / IMPLEMENTATION
----------------------
Implement every function below. Everything from add_generic and mul_generic onward must be reached only through the tagged constructors, generic selectors, and add_generic/mul_generic — never by branching on isinstance or a raw tuple shape outside the type-specific helper functions.
"""

from collections.abc import Callable
from math import gcd

type PlainNumber = tuple[str, int]
type RationalNumber = tuple[str, tuple[int, int]]
type Polynomial = tuple[str, tuple[str, tuple[tuple[int, float], ...]]]
type TaggedValue = PlainNumber | RationalNumber | Polynomial

type BinaryOperationTable = dict[tuple[str, str, str], Callable[[TaggedValue, TaggedValue], TaggedValue]]
type CoercionTable = dict[tuple[str, str], Callable[[TaggedValue], TaggedValue]]

_binary_operation_table: BinaryOperationTable = {}
_coercion_table: CoercionTable = {}


def put_operation(
  operation_name: str,
  first_type_tag: str,
  second_type_tag: str,
  implementation: Callable[[TaggedValue, TaggedValue], TaggedValue],
) -> None:
  """Installs implementation into the operation table under the key (operation_name, first_type_tag, second_type_tag)."""
  if (operation_name, first_type_tag, second_type_tag) in _binary_operation_table:
    raise ValueError(f"Operation {operation_name} for types {first_type_tag} and {second_type_tag} is already installed.")
  _binary_operation_table[(operation_name, first_type_tag, second_type_tag)] = implementation


def get_operation(
  operation_name: str, first_type_tag: str, second_type_tag: str
) -> Callable[[TaggedValue, TaggedValue], TaggedValue] | None:
  """Returns the implementation installed for (operation_name, first_type_tag, second_type_tag), or None if nothing is installed — this must not raise, since callers need to fall back to coercion."""
  return _binary_operation_table.get((operation_name, first_type_tag, second_type_tag))


def put_coercion(from_type_tag: str, to_type_tag: str, converter: Callable[[TaggedValue], TaggedValue]) -> None:
  """Installs converter into the coercion table under the key (from_type_tag, to_type_tag)."""
  _coercion_table[(from_type_tag, to_type_tag)] = converter


def get_coercion(from_type_tag: str, to_type_tag: str) -> Callable[[TaggedValue], TaggedValue] | None:
  """Returns the converter installed for (from_type_tag, to_type_tag), or None if no such coercion is installed."""
  return _coercion_table.get((from_type_tag, to_type_tag))


def type_tag(tagged_value: TaggedValue) -> str:
  """Selector. Returns the type tag, the first element, of any tagged value."""
  return tagged_value[0]


def contents(tagged_value: TaggedValue) -> object:
  """Selector. Returns the untagged payload, the second element, of any tagged value."""
  return tagged_value[1]


def make_plain_number(value: int) -> PlainNumber:
  """Constructor. Tags a raw int as a 'plain-number' TaggedValue."""
  return ("plain-number", value)


def make_rational(numerator: int, denominator: int) -> RationalNumber:
  """Constructor. Tags a (numerator, denominator) pair as a 'rational' TaggedValue, reduced to lowest terms via gcd, with the sign normalized onto the numerator so the denominator is always positive."""
  if denominator == 0:
    raise ZeroDivisionError("denominator must be non-zero")
  common_divisor = gcd(numerator, denominator)
  numerator_value = numerator // common_divisor
  denominator_value = denominator // common_divisor
  if denominator_value < 0:
    numerator_value = -numerator_value
    denominator_value = -denominator_value
  return ("rational", (numerator_value, denominator_value))


def numerator(rational_value: RationalNumber) -> int:
  """Selector. Only valid on a 'rational'-tagged TaggedValue."""
  return contents(rational_value)[0]


def denominator(rational_value: RationalNumber) -> int:
  """Selector. Only valid on a 'rational'-tagged TaggedValue."""
  return contents(rational_value)[1]


def make_polynomial(variable_name: str, terms: tuple[tuple[int, float], ...]) -> Polynomial:
  """Constructor. Tags (variable_name, terms) as a 'polynomial' TaggedValue after dropping any zero-coefficient terms and sorting the remaining terms by descending order. Terms are (order, coefficient) pairs."""
  normalized_terms = tuple(
    (order, coefficient)
    for order, coefficient in sorted(terms, key=lambda term: -term[0])
    if coefficient != 0
  )
  return ("polynomial", (variable_name, normalized_terms))


def polynomial_variable(polynomial_value: Polynomial) -> str:
  """Selector. Only valid on a 'polynomial'-tagged TaggedValue."""
  return contents(polynomial_value)[0]


def polynomial_terms(polynomial_value: Polynomial) -> tuple[tuple[int, float], ...]:
  """Selector. Only valid on a 'polynomial'-tagged TaggedValue."""
  return contents(polynomial_value)[1]


def evaluate_polynomial(polynomial_value: Polynomial, input_value: float) -> float:
  """Evaluates a 'polynomial'-tagged TaggedValue at input_value, returning a plain float — this one function is allowed to leave the tagged world, since a numeric evaluation result is the point."""
  return sum(coefficient * (input_value ** order) for order, coefficient in polynomial_terms(polynomial_value))


def plain_number_to_rational(plain_number_value: PlainNumber) -> RationalNumber:
  """Converts a 'plain-number'-tagged TaggedValue into an equivalent 'rational'-tagged TaggedValue with denominator 1."""
  return make_rational(contents(plain_number_value), 1)


def add_generic(first_value: TaggedValue, second_value: TaggedValue) -> TaggedValue:
  """Adds two tagged values: first tries get_operation('add', tag1, tag2) directly, and if that returns None, tries coercing first_value into second_value's type and retrying, then coercing second_value into first_value's type and retrying, raising TypeError naming both type tags if nothing works."""
  first_tag = type_tag(first_value)
  second_tag = type_tag(second_value)
  operation = get_operation("add", first_tag, second_tag)
  if operation is not None:
    return operation(first_value, second_value)
  coercion = get_coercion(first_tag, second_tag)
  if coercion is not None:
    coerced_first_value = coercion(first_value)
    coerced_operation = get_operation("add", second_tag, second_tag)
    if coerced_operation is not None:
      return coerced_operation(coerced_first_value, second_value)
  reverse_coercion = get_coercion(second_tag, first_tag)
  if reverse_coercion is not None:
    coerced_second_value = reverse_coercion(second_value)
    coerced_operation = get_operation("add", first_tag, first_tag)
    if coerced_operation is not None:
      return coerced_operation(first_value, coerced_second_value)
  raise TypeError(f"No method for adding {first_tag} and {second_tag}")


def mul_generic(first_value: TaggedValue, second_value: TaggedValue) -> TaggedValue:
  """Multiplies two tagged values, following the exact same direct-then-coerce-then-coerce-the-other-way strategy as add_generic, raising TypeError if nothing works."""
  first_tag = type_tag(first_value)
  second_tag = type_tag(second_value)
  operation = get_operation("mul", first_tag, second_tag)
  if operation is not None:
    return operation(first_value, second_value)
  coercion = get_coercion(first_tag, second_tag)
  if coercion is not None:
    coerced_first_value = coercion(first_value)
    coerced_operation = get_operation("mul", second_tag, second_tag)
    if coerced_operation is not None:
      return coerced_operation(coerced_first_value, second_value)
  reverse_coercion = get_coercion(second_tag, first_tag)
  if reverse_coercion is not None:
    coerced_second_value = reverse_coercion(second_value)
    coerced_operation = get_operation("mul", first_tag, first_tag)
    if coerced_operation is not None:
      return coerced_operation(first_value, coerced_second_value)
  raise TypeError(f"No method for multiplying {first_tag} and {second_tag}")


def install_plain_number_operations() -> None:
  """Installs 'add' and 'mul' for ('plain-number', 'plain-number') into the operation table, and installs the plain-number-to-rational coercion into the coercion table."""
  put_operation('add', 'plain-number', 'plain-number', lambda x, y: make_plain_number(contents(x) + contents(y)))
  put_operation('mul', 'plain-number', 'plain-number', lambda x, y: make_plain_number(contents(x) * contents(y)))
  put_coercion('plain-number', 'rational', plain_number_to_rational)


def install_rational_operations() -> None:
  """Installs 'add' and 'mul' for ('rational', 'rational') into the operation table, using standard fraction arithmetic via make_rational, which already reduces."""
  put_operation('add', 'rational', 'rational', lambda x, y: make_rational(numerator(x) * denominator(y) + numerator(y) * denominator(x), denominator(x) * denominator(y)))
  put_operation('mul', 'rational', 'rational', lambda x, y: make_rational(numerator(x) * numerator(y), denominator(x) * denominator(y)))


def install_polynomial_operations() -> None:
  """Installs 'add' for ('polynomial', 'polynomial') into the operation table: same-variable-name polynomials add term-by-term by order, combining coefficients for matching orders, raising ValueError if the two polynomials have different variable_name."""
  def add_polynomials(first_polynomial: Polynomial, second_polynomial: Polynomial) -> Polynomial:
    if polynomial_variable(first_polynomial) != polynomial_variable(second_polynomial):
      raise ValueError(f"Cannot add polynomials with different variable names: {polynomial_variable(first_polynomial)} and {polynomial_variable(second_polynomial)}")
    combined_terms: dict[int, float] = {}
    for order, coefficient in polynomial_terms(first_polynomial):
      combined_terms[order] = combined_terms.get(order, 0.0) + coefficient
    for order, coefficient in polynomial_terms(second_polynomial):
      combined_terms[order] = combined_terms.get(order, 0.0) + coefficient
    filtered_terms = tuple(
      (order, coefficient)
      for order, coefficient in sorted(combined_terms.items(), key=lambda term: -term[0])
      if coefficient != 0.0
    )
    return make_polynomial(polynomial_variable(first_polynomial), filtered_terms)

  put_operation('add', 'polynomial', 'polynomial', add_polynomials)


"""
REAL-WORLD SEQUENCE TASK
-------------------------
A small financial model needs to combine three genuinely different types into one number: a flat integer setup fee, a rational annual interest rate expressed as an exact fraction rather than a float, and a polynomial modeling how a deposited balance grows over t years under a simplified, non-compounding model. Install all three operation sets, then use add_generic to add the fee and the rate — which only succeeds because of the plain-number-to-rational coercion — and use evaluate_polynomial to project the balance at year three.

This is also the "small build with AI" step that closes out Month 1. Once the stubs above are implemented and passing their sanity checks, define build_growth_projection with AI assistance so that it produces a single combined "total obligation" figure by folding projected_balance_at_year_three together with fee_plus_rate using this file's generic operations — you will likely need one more coercion or one more installed operation pair that is not listed above, and that gap is the point. Implement it, call it, and store its result as total_obligation_estimate.
"""

def build_growth_projection(projected_balance: float, fee_plus_rate_value: TaggedValue) -> TaggedValue:
  projected_balance_plain = make_plain_number(int(projected_balance))
  return add_generic(fee_plus_rate_value, projected_balance_plain)


setup_fee: PlainNumber = make_plain_number(50)
interest_rate: RationalNumber = make_rational(7, 200)
growth_polynomial: Polynomial = make_polynomial("t", ((1, 1000.0), (0, 200.0)))

install_plain_number_operations()
install_rational_operations()
install_polynomial_operations()

fee_plus_rate: TaggedValue = add_generic(setup_fee, interest_rate)
projected_balance_at_year_three: float = evaluate_polynomial(growth_polynomial, 3.0)
total_obligation_estimate: TaggedValue = build_growth_projection(projected_balance_at_year_three, fee_plus_rate)

print(numerator(make_rational(2, 4)))  # expect 1
print(denominator(make_rational(2, 4)))  # expect 2
print(numerator(make_rational(-3, -9)))  # expect 1
print(denominator(make_rational(-3, -9)))  # expect 3

print(evaluate_polynomial(growth_polynomial, 0.0))  # expect 200.0
print(evaluate_polynomial(growth_polynomial, 3.0))  # expect 3200.0

print(contents(add_generic(make_rational(1, 4), make_rational(1, 4))))  # expect (1, 2)
print(contents(fee_plus_rate))  # expect (10007, 200)
print(projected_balance_at_year_three)  # expect 3200.0

# WRITTEN ANSWER: after implementing build_growth_projection with AI assistance, answer here in 4-6 sentences. What extra coercion or operation pair did you end up needing that wasn't installed above, and could you have predicted that gap just from reading the type signatures before writing any code? Did the AI assistant reach for the existing add_generic/mul_generic and coercion-table machinery on its own, or did it default to writing a fresh isinstance chain, and if the latter, what about the interface as specified above made that easier to reach for than the generic path? Where, specifically, did the abstraction barrier — tagged values only manipulated through their constructors, selectors, and generic operations — hold firm under this extension, and where, if anywhere, did you or the assistant end up reaching past it directly at a tuple's contents?
#The extra gap was the plain-number → rational coercion needed to add a flat integer fee to an exact rational rate, since there was no direct mixed add implementation. 
# That gap was predictable from the type tags: add_generic only does same-tag operations directly, so combining different tags needed coercion. The assistant used the existing tagged constructors and generic machinery rather than an isinstance chain. 
# The abstraction barrier held in build_growth_projection because it only created a tagged plain number and invoked add_generic, while raw tuple access stayed inside the type-specific helper functions.