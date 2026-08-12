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
    implementation: Callable[
        [TaggedValue, TaggedValue],
        TaggedValue,
    ],
) -> None:
    """Installs implementation into the operation table."""
    _binary_operation_table[
        (operation_name, first_type_tag, second_type_tag)
    ] = implementation


def get_operation(
    operation_name: str,
    first_type_tag: str,
    second_type_tag: str,
) -> Callable[[TaggedValue, TaggedValue], TaggedValue] | None:
    """
    Returns the implementation installed for the given
    operation and type tags, or None if no implementation exists.
    """
    return _binary_operation_table.get(
        (operation_name, first_type_tag, second_type_tag)
    )


def put_coercion(
    from_type_tag: str,
    to_type_tag: str,
    converter: Callable[[TaggedValue], TaggedValue],
) -> None:
    """Installs a coercion function into the coercion table."""
    _coercion_table[
        (from_type_tag, to_type_tag)
    ] = converter


def get_coercion(
    from_type_tag: str,
    to_type_tag: str,
) -> Callable[[TaggedValue], TaggedValue] | None:
    """
    Returns the coercion function for the given type conversion,
    or None if no coercion exists.
    """
    return _coercion_table.get(
        (from_type_tag, to_type_tag)
    )


def type_tag(tagged_value: TaggedValue) -> str:
    """Returns the type tag of a tagged value."""
    return tagged_value[0]


def contents(tagged_value: TaggedValue) -> object:
    """Returns the untagged payload of a tagged value."""
    return tagged_value[1]


def make_plain_number(value: int) -> PlainNumber:
    """Creates a tagged plain-number value."""
    return ("plain-number", value)


def make_rational(
    numerator: int,
    denominator: int,
) -> RationalNumber:
    """
    Creates a reduced rational number.

    The denominator must not be zero.
    The denominator is always kept positive.
    """
    if denominator == 0:
        raise ValueError("Denominator cannot be zero")

    divisor = gcd(
        abs(numerator),
        abs(denominator),
    )

    numerator //= divisor
    denominator //= divisor

    if denominator < 0:
        numerator = -numerator
        denominator = -denominator

    return (
        "rational",
        (numerator, denominator),
    )


def numerator(
    rational_value: RationalNumber,
) -> int:
    """Returns the numerator of a rational value."""
    return contents(rational_value)[0]


def denominator(
    rational_value: RationalNumber,
) -> int:
    """Returns the denominator of a rational value."""
    return contents(rational_value)[1]


def make_polynomial(
    variable_name: str,
    terms: tuple[tuple[int, float], ...],
) -> Polynomial:
    """
    Creates a polynomial after removing zero coefficients
    and sorting terms by descending order.
    """
    cleaned_terms = tuple(
        sorted(
            (
                (order, coefficient)
                for order, coefficient in terms
                if coefficient != 0
            ),
            key=lambda term: term[0],
            reverse=True,
        )
    )

    return (
        "polynomial",
        (variable_name, cleaned_terms),
    )


def polynomial_variable(
    polynomial_value: Polynomial,
) -> str:
    """Returns the variable name of a polynomial."""
    return contents(polynomial_value)[0]


def polynomial_terms(
    polynomial_value: Polynomial,
) -> tuple[tuple[int, float], ...]:
    """Returns the terms of a polynomial."""
    return contents(polynomial_value)[1]


def evaluate_polynomial(
    polynomial_value: Polynomial,
    input_value: float,
) -> float:
    """
    Evaluates a polynomial at input_value.

    This function intentionally returns a raw float because
    numeric evaluation is the purpose of this operation.
    """
    total = 0.0

    for order, coefficient in polynomial_terms(
        polynomial_value
    ):
        total += coefficient * (input_value ** order)

    return total


def plain_number_to_rational(
    plain_number_value: PlainNumber,
) -> RationalNumber:
    """
    Converts a plain-number into an equivalent rational
    with denominator 1.
    """
    return make_rational(
        contents(plain_number_value),
        1,
    )


def add_generic(
    first_value: TaggedValue,
    second_value: TaggedValue,
) -> TaggedValue:
    """
    Performs generic addition.

    First tries a direct operation.
    If unavailable, tries coercing the first value into
    the second value's type.
    If that is unavailable, tries coercing the second value
    into the first value's type.
    """
    tag1 = type_tag(first_value)
    tag2 = type_tag(second_value)

    operation = get_operation(
        "add",
        tag1,
        tag2,
    )

    if operation is not None:
        return operation(
            first_value,
            second_value,
        )

    coercion = get_coercion(
        tag1,
        tag2,
    )

    if coercion is not None:
        return add_generic(
            coercion(first_value),
            second_value,
        )

    coercion = get_coercion(
        tag2,
        tag1,
    )

    if coercion is not None:
        return add_generic(
            first_value,
            coercion(second_value),
        )

    raise TypeError(
        f"No add implementation for {tag1} and {tag2}"
    )


def mul_generic(
    first_value: TaggedValue,
    second_value: TaggedValue,
) -> TaggedValue:
    """
    Performs generic multiplication.

    First tries a direct operation.
    If unavailable, tries coercing the first value into
    the second value's type.
    If that is unavailable, tries coercing the second value
    into the first value's type.
    """
    tag1 = type_tag(first_value)
    tag2 = type_tag(second_value)

    operation = get_operation(
        "mul",
        tag1,
        tag2,
    )

    if operation is not None:
        return operation(
            first_value,
            second_value,
        )

    coercion = get_coercion(
        tag1,
        tag2,
    )

    if coercion is not None:
        return mul_generic(
            coercion(first_value),
            second_value,
        )

    coercion = get_coercion(
        tag2,
        tag1,
    )

    if coercion is not None:
        return mul_generic(
            first_value,
            coercion(second_value),
        )

    raise TypeError(
        f"No mul implementation for {tag1} and {tag2}"
    )


def install_plain_number_operations() -> None:
    """
    Installs addition and multiplication for plain numbers.

    Also installs the plain-number -> rational coercion.
    """

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
    """Installs addition and multiplication for rational numbers."""

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
    """
    Installs addition for polynomials.

    Polynomials must use the same variable name.
    """

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
            combined[order] = (
                combined.get(order, 0.0)
                + coefficient
            )

        for order, coefficient in polynomial_terms(second):
            combined[order] = (
                combined.get(order, 0.0)
                + coefficient
            )

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


# ---------------------------------------------------------
# REAL-WORLD SEQUENCE TASK
# ---------------------------------------------------------

setup_fee: PlainNumber = make_plain_number(50)

interest_rate: RationalNumber = make_rational(
    7,
    200,
)

growth_polynomial: Polynomial = make_polynomial(
    "t",
    (
        (1, 1000.0),
        (0, 200.0),
    ),
)


# Install all generic operations and coercions.

install_plain_number_operations()
install_rational_operations()
install_polynomial_operations()


# ---------------------------------------------------------
# Combine setup fee and interest rate.
#
# plain-number(50) + rational(7/200)
#
# There is no direct operation for these two types.
# Therefore add_generic() uses:
#
# plain-number -> rational
#
# and performs:
#
# rational(50/1) + rational(7/200)
#
# = rational(10007/200)
# ---------------------------------------------------------

fee_plus_rate: TaggedValue = add_generic(
    setup_fee,
    interest_rate,
)


# ---------------------------------------------------------
# Evaluate growth polynomial at year three.
#
# 1000 * 3 + 200 = 3200
# ---------------------------------------------------------

projected_balance_at_year_three: float = (
    evaluate_polynomial(
        growth_polynomial,
        3.0,
    )
)


# ---------------------------------------------------------
# Build final growth projection.
# ---------------------------------------------------------

def build_growth_projection(
    projected_balance: float,
    fee_and_rate: TaggedValue,
) -> TaggedValue:
    """
    Combines the projected balance with the fee/rate
    using generic arithmetic.

    The function does not inspect the rational's internal
    numerator or denominator and does not manually convert
    the rational to a plain number.
    """

    projected_balance_tagged = make_plain_number(
        int(projected_balance)
    )

    return add_generic(
        projected_balance_tagged,
        fee_and_rate,
    )


total_obligation_estimate: TaggedValue = (
    build_growth_projection(
        projected_balance_at_year_three,
        fee_plus_rate,
    )
)


# ---------------------------------------------------------
# Output
# ---------------------------------------------------------

print(total_obligation_estimate)

print(
    numerator(total_obligation_estimate)
    / denominator(total_obligation_estimate)
)
