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

type BinaryOperationTable = dict[
    tuple[str, str, str],
    Callable[[TaggedValue, TaggedValue], TaggedValue],
]
type CoercionTable = dict[
    tuple[str, str],
    Callable[[TaggedValue], TaggedValue],
]

_binary_operation_table: BinaryOperationTable = {}
_coercion_table: CoercionTable = {}


def put_operation(
    operation_name: str,
    first_type_tag: str,
    second_type_tag: str,
    implementation: Callable[[TaggedValue, TaggedValue], TaggedValue],
) -> None:
    """Installs implementation into the operation table under the key (operation_name, first_type_tag, second_type_tag)."""
    _binary_operation_table[
        (operation_name, first_type_tag, second_type_tag)
    ] = implementation


def get_operation(
    operation_name: str,
    first_type_tag: str,
    second_type_tag: str,
) -> Callable[[TaggedValue, TaggedValue], TaggedValue] | None:
    """Returns the implementation installed for (operation_name, first_type_tag, second_type_tag), or None if nothing is installed — this must not raise, since callers need to fall back to coercion."""
    return _binary_operation_table.get(
        (operation_name, first_type_tag, second_type_tag)
    )


def put_coercion(
    from_type_tag: str,
    to_type_tag: str,
    converter: Callable[[TaggedValue], TaggedValue],
) -> None:
    """Installs converter into the coercion table under the key (from_type_tag, to_type_tag)."""
    _coercion_table[(from_type_tag, to_type_tag)] = converter


def get_coercion(
    from_type_tag: str,
    to_type_tag: str,
) -> Callable[[TaggedValue], TaggedValue] | None:
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

    divisor = gcd(abs(numerator), abs(denominator))
    numerator //= divisor
    denominator //= divisor

    if denominator < 0:
        numerator = -numerator
        denominator = -denominator

    return ("rational", (numerator, denominator))


def numerator(rational_value: RationalNumber) -> int:
    """Selector. Only valid on a 'rational'-tagged TaggedValue."""
    return contents(rational_value)[0]


def denominator(rational_value: RationalNumber) -> int:
    """Selector. Only valid on a 'rational'-tagged TaggedValue."""
    return contents(rational_value)[1]


def make_polynomial(
    variable_name: str,
    terms: tuple[tuple[int, float], ...],
) -> Polynomial:
    """Constructor. Tags (variable_name, terms) as a 'polynomial' TaggedValue after dropping any zero-coefficient terms and sorting the remaining terms by descending order. Terms are (order, coefficient) pairs."""
    cleaned_terms = tuple(
        sorted(
            ((order, coeff) for order, coeff in terms if coeff != 0),
            key=lambda term: term[0],
            reverse=True,
        )
    )
    return ("polynomial", (variable_name, cleaned_terms))


def polynomial_variable(polynomial_value: Polynomial) -> str:
    """Selector. Only valid on a 'polynomial'-tagged TaggedValue."""
    return contents(polynomial_value)[0]


def polynomial_terms(
    polynomial_value: Polynomial,
) -> tuple[tuple[int, float], ...]:
    """Selector. Only valid on a 'polynomial'-tagged TaggedValue."""
    return contents(polynomial_value)[1]


def evaluate_polynomial(
    polynomial_value: Polynomial,
    input_value: float,
) -> float:
    """Evaluates a 'polynomial'-tagged TaggedValue at input_value, returning a plain float — this one function is allowed to leave the tagged world, since a numeric evaluation result is the point."""
    total = 0.0

    for order, coefficient in polynomial_terms(polynomial_value):
        total += coefficient * (input_value ** order)

    return total


def plain_number_to_rational(
    plain_number_value: PlainNumber,
) -> RationalNumber:
    """Converts a 'plain-number'-tagged TaggedValue into an equivalent 'rational'-tagged TaggedValue with denominator 1."""
    return make_rational(contents(plain_number_value), 1)


def add_generic(
    first_value: TaggedValue,
    second_value: TaggedValue,
) -> TaggedValue:
    """Adds two tagged values: first tries get_operation('add', tag1, tag2) directly, and if that returns None, tries coercing first_value into second_value's type and retrying, then coercing second_value into first_value's type and retrying, raising TypeError naming both type tags if nothing works."""
    tag1 = type_tag(first_value)
    tag2 = type_tag(second_value)

    operation = get_operation("add", tag1, tag2)

    if operation is not None:
        return operation(first_value, second_value)

    coercion = get_coercion(tag1, tag2)
    if coercion is not None:
        return add_generic(coercion(first_value), second_value)

    coercion = get_coercion(tag2, tag1)
    if coercion is not None:
        return add_generic(first_value, coercion(second_value))

    raise TypeError(f"No add implementation for {tag1} and {tag2}")


def mul_generic(
    first_value: TaggedValue,
    second_value: TaggedValue,
) -> TaggedValue:
    """Multiplies two tagged values, following the exact same direct-then-coerce-then-coerce-the-other-way strategy as add_generic, raising TypeError if nothing works."""
    tag1 = type_tag(first_value)
    tag2 = type_tag(second_value)

    operation = get_operation("mul", tag1, tag2)

    if operation is not None:
        return operation(first_value, second_value)

    coercion = get_coercion(tag1, tag2)
    if coercion is not None:
        return mul_generic(coercion(first_value), second_value)

    coercion = get_coercion(tag2, tag1)
    if coercion is not None:
        return mul_generic(first_value, coercion(second_value))

    raise TypeError(f"No mul implementation for {tag1} and {tag2}")


def install_plain_number_operations() -> None:
    """Installs 'add' and 'mul' for ('plain-number', 'plain-number') into the operation table, and installs the plain-number-to-rational coercion into the coercion table."""

    def add_plain(
        first: TaggedValue,
        second: TaggedValue,
    ) -> TaggedValue:
        return make_plain_number(
            contents(first) + contents(second)
        )

    def mul_plain(
        first: TaggedValue,
        second: TaggedValue,
    ) -> TaggedValue:
        return make_plain_number(
            contents(first) * contents(second)
        )

    put_operation(
        "add",
        "plain-number",
        "plain-number",
        add_plain,
    )
    put_operation(
        "mul",
        "plain-number",
        "plain-number",
        mul_plain,
    )

    put_coercion(
        "plain-number",
        "rational",
        plain_number_to_rational,
    )


def install_rational_operations() -> None:
    """Installs 'add' and 'mul' for ('rational', 'rational') into the operation table, using standard fraction arithmetic via make_rational, which already reduces."""

    def add_rational(
        first: TaggedValue,
        second: TaggedValue,
    ) -> TaggedValue:
        return make_rational(
            numerator(first) * denominator(second)
            + numerator(second) * denominator(first),
            denominator(first) * denominator(second),
        )

    def mul_rational(
        first: TaggedValue,
        second: TaggedValue,
    ) -> TaggedValue:
        return make_rational(
            numerator(first) * numerator(second),
            denominator(first) * denominator(second),
        )

    put_operation(
        "add",
        "rational",
        "rational",
        add_rational,
    )
    put_operation(
        "mul",
        "rational",
        "rational",
        mul_rational,
    )


def install_polynomial_operations() -> None:
    """Installs 'add' for ('polynomial', 'polynomial') into the operation table: same-variable-name polynomials add term-by-term by order, combining coefficients for matching orders, raising ValueError if the two polynomials have different variable_name."""

    def add_polynomial(
        first: TaggedValue,
        second: TaggedValue,
    ) -> TaggedValue:
        if polynomial_variable(first) != polynomial_variable(second):
            raise ValueError(
                "Polynomial variables must match"
            )

        combined: dict[int, float] = {}

        for order, coefficient in polynomial_terms(first):
            combined[order] = combined.get(order, 0.0) + coefficient

        for order, coefficient in polynomial_terms(second):
            combined[order] = combined.get(order, 0.0) + coefficient

        return make_polynomial(
            polynomial_variable(first),
            tuple(combined.items()),
        )

    put_operation(
        "add",
        "polynomial",
        "polynomial",
        add_polynomial,
    )


# --------- EXTRA FOR build_growth_projection ---------

def rational_to_plain_number(
    rational_value: RationalNumber,
) -> PlainNumber:
    num = numerator(rational_value)
    den = denominator(rational_value)

    if den != 1:
        raise ValueError(
            "Cannot coerce non-integer rational to plain-number"
        )

    return make_plain_number(num)


put_coercion(
    "rational",
    "plain-number",
    rational_to_plain_number,
)


# REAL-WORLD SEQUENCE TASK

setup_fee: PlainNumber = make_plain_number(50)
interest_rate: RationalNumber = make_rational(7, 200)
growth_polynomial: Polynomial = make_polynomial(
    "t",
    ((1, 1000.0), (0, 200.0)),
)

install_plain_number_operations()
install_rational_operations()
install_polynomial_operations()

fee_plus_rate: TaggedValue = add_generic(
    setup_fee,
    interest_rate,
)

projected_balance_at_year_three: float = evaluate_polynomial(
    growth_polynomial,
    3.0,
)


def build_growth_projection(
    projected_balance: float,
    fee_and_rate: TaggedValue,
) -> TaggedValue:
    projected_balance_tagged = make_plain_number(
        int(projected_balance)
    )

    fee_and_rate_integer = make_plain_number(
        numerator(fee_and_rate)
        // denominator(fee_and_rate)
    )

    return add_generic(
        projected_balance_tagged,
        fee_and_rate_integer,
    )


total_obligation_estimate = build_growth_projection(
    projected_balance_at_year_three,
    fee_plus_rate,
)

print(contents(total_obligation_estimate))  # 3250