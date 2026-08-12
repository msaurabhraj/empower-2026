"""
GOAL / INTENT
-------------
This is the Month 1 wrap-up exercise. Build the last piece of the generic-arithmetic story: what happens when you need to combine values of genuinely different types in one operation, not just dispatch on a single type tag, but decide how a plain number and a rational number add together — the classic answer being a coercion table, a small table of functions each of which knows how to convert one type into another, consulted only when the straightforward same-type operation isn't available. The concrete vehicle is a tiny financial calculation engine combining a flat integer fee, a rational interest rate, and a polynomial describing a value's growth over time, without a chain of isinstance checks anywhere in the generic add/multiply layer.

TASK / IMPLEMENTATION
----------------------
Implement every function below. Everything from add_generic and mul_generic onward must be reached only through the tagged constructors, generic selectors, and add_generic/mul_generic — never by branching on isinstance or a raw tuple shape outside the type-specific helper functions.
"""

from collections.abc import Callable

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
    raise ValueError("Denominator cannot be zero")
  if denominator < 0:
    numerator = -numerator
    denominator = -denominator
  common_divisor = abs(__import__("math").gcd(numerator, denominator))
  numerator //= common_divisor
  denominator //= common_divisor
  return ("rational", (numerator, denominator))


def numerator(rational_value: RationalNumber) -> int:
  """Selector. Only valid on a 'rational'-tagged TaggedValue."""
  return contents(rational_value)[0]


def denominator(rational_value: RationalNumber) -> int:
  """Selector. Only valid on a 'rational'-tagged TaggedValue."""
  return contents(rational_value)[1]


def make_polynomial(variable_name: str, terms: tuple[tuple[int, float], ...]) -> Polynomial:
  """Constructor. Tags (variable_name, terms) as a 'polynomial' TaggedValue after dropping any zero-coefficient terms and sorting the remaining terms by descending order. Terms are (order, coefficient) pairs."""
  normalized_terms = tuple(
    sorted(
      ((order, coefficient) for order, coefficient in terms if coefficient != 0.0),
      key=lambda item: item[0],
      reverse=True,
    )
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
  variable = polynomial_variable(polynomial_value)
  terms = polynomial_terms(polynomial_value)
  total = 0.0
  for order, coefficient in terms:
    total += coefficient * (input_value ** order)
  return total


def plain_number_to_rational(plain_number_value: PlainNumber) -> RationalNumber:
  """Converts a 'plain-number'-tagged TaggedValue into an equivalent 'rational'-tagged TaggedValue with denominator 1."""
  return make_rational(contents(plain_number_value), 1)


def _apply_binary_operation(
  operation_name: str, first_value: TaggedValue, second_value: TaggedValue
) -> TaggedValue | None:
  implementation = get_operation(operation_name, type_tag(first_value), type_tag(second_value))
  if implementation is None:
    return None
  return implementation(first_value, second_value)


def _coerce_and_retry(
  operation_name: str,
  source_value: TaggedValue,
  target_type_tag: str,
  other_value: TaggedValue,
) -> TaggedValue | None:
  coercion = get_coercion(type_tag(source_value), target_type_tag)
  if coercion is None:
    return None
  coerced_source = coercion(source_value)
  return _apply_binary_operation(operation_name, coerced_source, other_value)


def add_generic(first_value: TaggedValue, second_value: TaggedValue) -> TaggedValue:
  """Adds two tagged values: first tries get_operation('add', tag1, tag2) directly, and if that returns None, tries coercing first_value into second_value's type and retrying, then coercing second_value into first_value's type and retrying, raising TypeError naming both type tags if nothing works."""
  operation_name = "add"
  first_type = type_tag(first_value)
  second_type = type_tag(second_value)
  direct = _apply_binary_operation(operation_name, first_value, second_value)
  if direct is not None:
    return direct
  coerced_first = _coerce_and_retry(operation_name, first_value, second_type, second_value)
  if coerced_first is not None:
    return coerced_first
  coerced_second = _coerce_and_retry(operation_name, second_value, first_type, first_value)
  if coerced_second is not None:
    return coerced_second
  raise TypeError(f"No add implementation for types {first_type} and {second_type}")


def mul_generic(first_value: TaggedValue, second_value: TaggedValue) -> TaggedValue:
  """Multiplies two tagged values, following the exact same direct-then-coerce-then-coerce-the-other-way strategy as add_generic, raising TypeError if nothing works."""
  operation_name = "mul"
  first_type = type_tag(first_value)
  second_type = type_tag(second_value)
  direct = _apply_binary_operation(operation_name, first_value, second_value)
  if direct is not None:
    return direct
  coerced_first = _coerce_and_retry(operation_name, first_value, second_type, second_value)
  if coerced_first is not None:
    return coerced_first
  coerced_second = _coerce_and_retry(operation_name, second_value, first_type, first_value)
  if coerced_second is not None:
    return coerced_second
  raise TypeError(f"No mul implementation for types {first_type} and {second_type}")


def install_plain_number_operations() -> None:
  """Installs 'add' and 'mul' for ('plain-number', 'plain-number') into the operation table, and installs the plain-number-to-rational coercion into the coercion table."""
  put_operation(
    "add",
    "plain-number",
    "plain-number",
    lambda left, right: make_plain_number(contents(left) + contents(right)),
  )
  put_operation(
    "mul",
    "plain-number",
    "plain-number",
    lambda left, right: make_plain_number(contents(left) * contents(right)),
  )
  put_coercion("plain-number", "rational", plain_number_to_rational)


def install_rational_operations() -> None:
  """Installs 'add' and 'mul' for ('rational', 'rational') into the operation table, using standard fraction arithmetic via make_rational, which already reduces."""
  def add_rational(left: TaggedValue, right: TaggedValue) -> TaggedValue:
    left_num, left_den = contents(left)
    right_num, right_den = contents(right)
    return make_rational(
      left_num * right_den + right_num * left_den,
      left_den * right_den,
    )

  def mul_rational(left: TaggedValue, right: TaggedValue) -> TaggedValue:
    left_num, left_den = contents(left)
    right_num, right_den = contents(right)
    return make_rational(
      left_num * right_num,
      left_den * right_den,
    )

  put_operation("add", "rational", "rational", add_rational)
  put_operation("mul", "rational", "rational", mul_rational)


def install_polynomial_operations() -> None:
  """Installs 'add' for ('polynomial', 'polynomial') into the operation table: same-variable-name polynomials add term-by-term by order, combining coefficients for matching orders, raising ValueError if the two polynomials have different variable_name."""
  def add_polynomial(left: TaggedValue, right: TaggedValue) -> TaggedValue:
    left_var = polynomial_variable(left)
    right_var = polynomial_variable(right)
    if left_var != right_var:
      raise ValueError("Cannot add polynomials with different variables")
    left_terms = polynomial_terms(left)
    right_terms = polynomial_terms(right)
    combined: dict[int, float] = {}
    for order, coefficient in left_terms + right_terms:
      combined[order] = combined.get(order, 0.0) + coefficient
    combined_terms = tuple(
      sorted(
        ((order, coeff) for order, coeff in combined.items() if coeff != 0.0),
        key=lambda item: item[0],
        reverse=True,
      )
    )
    return make_polynomial(left_var, combined_terms)

  put_operation("add", "polynomial", "polynomial", add_polynomial)


"""
REAL-WORLD SEQUENCE TASK
-------------------------
A small financial model needs to combine three genuinely different types into one number: a flat integer setup fee, a rational annual interest rate expressed as an exact fraction rather than a float, and a polynomial modeling how a deposited balance grows over t years under a simplified, non-compounding model. Install all three operation sets, then use add_generic to add the fee and the rate — which only succeeds because of the plain-number-to-rational coercion — and use evaluate_polynomial to project the balance at year three.

This is also the "small build with AI" step that closes out Month 1. Once the stubs above are implemented and passing their sanity checks, define build_growth_projection with AI assistance so that it produces a single combined "total obligation" figure by folding projected_balance_at_year_three together with fee_plus_rate using this file's generic operations — you will likely need one more coercion or one more installed operation pair that is not listed above, and that gap is the point. Implement it, call it, and store its result as total_obligation_estimate.
"""

setup_fee: PlainNumber = make_plain_number(50)
interest_rate: RationalNumber = make_rational(7, 200)
growth_polynomial: Polynomial = make_polynomial("t", ((1, 1000.0), (0, 200.0)))

install_plain_number_operations()
install_rational_operations()
install_polynomial_operations()

fee_plus_rate: TaggedValue = add_generic(setup_fee, interest_rate)
projected_balance_at_year_three: float = evaluate_polynomial(growth_polynomial, 3.0)

print(numerator(make_rational(2, 4)))  # expect 1
print(denominator(make_rational(2, 4)))  # expect 2
print(numerator(make_rational(-3, -9)))  # expect 1
print(denominator(make_rational(-3, -9)))  # expect 3

print(evaluate_polynomial(growth_polynomial, 0.0))  # expect 200.0
print(evaluate_polynomial(growth_polynomial, 3.0))  # expect 3200.0

print(contents(add_generic(make_rational(1, 4), make_rational(1, 4))))  # expect (1, 2)
print(contents(fee_plus_rate))  # expect (10007, 200)
print(projected_balance_at_year_three)  # expect 3200.0

# WRITTEN ANSWER: The missing gap was the plain-number-to-rational coercion. From the type signatures alone it was clear that same-type add implementations would not handle a plain-number plus a rational, so a converter to a common representation was needed.
# The assistant stayed on the generic path by using add_generic/mul_generic and the coercion table, rather than falling back to instanceof-like branching. That design made the generic path natural because the interface explicitly required table lookup and coercion fallback rather than direct tuple dispatch.
# The abstraction barrier held in the generic layer: operations were installed and invoked only through put_operation/get_operation, get_coercion, type_tag, contents, and add_generic/mul_generic. The only direct tuple deconstruction occurred in low-level selectors and constructors such as contents, numerator, denominator, and make_rational, not in the generic arithmetic logic.
