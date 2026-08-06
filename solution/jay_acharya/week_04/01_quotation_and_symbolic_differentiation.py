"""
GOAL / INTENT
-------------
Build the distinction between evaluating an expression and quoting it — treating it as inert data you can inspect, take apart, and rebuild — using symbolic differentiation as the concrete vehicle, since a differentiation program never "runs" the arithmetic it is handed, it only pattern-matches on the shape of an expression and produces a new expression as data.

TASK / IMPLEMENTATION
----------------------
An expression is one of: a number, a variable name (a string), a sum tuple ('+', addend, augend), or a product tuple ('*', multiplier, multiplicand). Implement every function below. Everything from derivative() onward must be built exclusively out of is_number, is_variable, is_same_variable, is_sum, make_sum, addend, augend, is_product, make_product, multiplier, and multiplicand — never by pattern-matching on a raw tuple's shape directly.
"""

type Expression = int | float | str | tuple[str, "Expression", "Expression"]


def is_number(expression: Expression) -> bool:
    """True if expression is a plain numeric literal."""
    return isinstance(expression, (int, float))


def is_variable(expression: Expression) -> bool:
    """True if expression is a bare variable name."""
    return (
        isinstance(expression, str)
        and expression not in ("+", "*")
    )


def is_same_variable(first_variable: Expression, second_variable: Expression) -> bool:
    """True if both arguments are the same variable."""
    return (
        is_variable(first_variable)
        and is_variable(second_variable)
        and first_variable == second_variable
    )


def is_sum(expression: Expression) -> bool:
    """True if expression is a sum expression."""
    return (
        isinstance(expression, tuple)
        and len(expression) == 3
        and expression[0] == "+"
    )


def make_sum(addend: Expression, augend: Expression) -> Expression:
    """Constructor."""
    return ("+", addend, augend)


def addend(sum_expression: Expression) -> Expression:
    """Selector."""
    return sum_expression[1]


def augend(sum_expression: Expression) -> Expression:
    """Selector."""
    return sum_expression[2]


def is_product(expression: Expression) -> bool:
    """True if expression is a product expression."""
    return (
        isinstance(expression, tuple)
        and len(expression) == 3
        and expression[0] == "*"
    )


def make_product(multiplier: Expression, multiplicand: Expression) -> Expression:
    """Constructor."""
    return ("*", multiplier, multiplicand)


def multiplier(product_expression: Expression) -> Expression:
    """Selector."""
    return product_expression[1]


def multiplicand(product_expression: Expression) -> Expression:
    """Selector."""
    return product_expression[2]


def derivative(expression: Expression, variable_name: str) -> Expression:
    """
    Symbolic differentiation using only predicates,
    constructors, and selectors.
    """
    if is_number(expression):
        return 0

    if is_variable(expression):
        return 1 if is_same_variable(expression, variable_name) else 0

    if is_sum(expression):
        return make_sum(
            derivative(addend(expression), variable_name),
            derivative(augend(expression), variable_name),
        )

    if is_product(expression):
        return make_sum(
            make_product(
                multiplier(expression),
                derivative(multiplicand(expression), variable_name),
            ),
            make_product(
                multiplicand(expression),
                derivative(multiplier(expression), variable_name),
            ),
        )

    raise ValueError(f"Unknown expression type: {expression}")


# Billing requirement encoded as quoted data
total_charge_formula: Expression = make_sum(
    "base_fee",
    make_product("usage_rate", "usage_amount"),
)

marginal_cost_formula: Expression = derivative(
    total_charge_formula,
    "usage_amount",
)


print(is_number(3))  # True
print(is_variable("x"))  # True
print(is_variable(3))  # False
print(is_same_variable("x", "x"))  # True
print(is_same_variable("x", "y"))  # False

sum_example = make_sum("x", 3)
print(is_sum(sum_example))  # True
print(addend(sum_example))  # 'x'
print(augend(sum_example))  # 3

product_example = make_product("x", "y")
print(is_product(product_example))  # True
print(multiplier(product_example))  # 'x'
print(multiplicand(product_example))  # 'y'

print(derivative(make_sum("x", 3), "x"))
# ('+', 1, 0)

print(derivative(make_product("x", "y"), "x"))
# ('+', ('*', 'x', 0), ('*', 'y', 1))

print(derivative("x", "y"))
# 0

print(derivative(3, "x"))
# 0

print(marginal_cost_formula)  # expect a tree that, read literally, equals 'usage_rate'

# Once you see marginal_cost_formula, it comes out to exactly "usage_rate" — but that is only correct if usage_rate is a true constant with respect to usage_amount, and the original prose requirement never actually said that; it is equally consistent with a tiered or graduated pricing scheme where usage_rate itself depends on how much has already been used. Evaluating the requirement literally, as a symbolic expression, is what exposes this ambiguity — the prose alone let it hide. Write 2-3 sentences identifying the follow-up question you would need to ask a stakeholder to resolve it.
