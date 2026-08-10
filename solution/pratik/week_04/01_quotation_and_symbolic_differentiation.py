"""
GOAL / INTENT
-------------
Build the distinction between evaluating an expression and quoting it — treating it as inert data you can inspect, take apart, and rebuild — using symbolic differentiation as the concrete vehicle, since a differentiation program never "runs" the arithmetic it is handed, it only pattern-matches on the shape of an expression and produces a new expression as data.

TASK / IMPLEMENTATION
----------------------
An expression is one of: a number, a variable name (a string), a sum tuple ('+', addend, augend), or a product tuple ('*', multiplier, multiplicand). Implement every function below. Everything from derivative() onward must be built exclusively out of is_number, is_variable, is_same_variable, is_sum, make_sum, addend, augend, is_product, make_product, multiplier, and multiplicand — never by pattern-matching on a raw tuple's shape directly.
"""

type Expression = int | float | str | tuple[str, Expression, Expression]


def is_number(expression: Expression) -> bool:
  """True if expression is a plain numeric literal (int or float), not a variable name or a compound expression."""
  return isinstance(expression, (int, float))



def is_variable(expression: Expression) -> bool:
  """True if expression is a bare variable name, represented as a str that is not one of the compound-expression tags ('+' or '*')."""
  return isinstance(expression, str) and expression not in ('+', '*')


def is_same_variable(first_variable: Expression, second_variable: Expression) -> bool:
  """True if both arguments are variables (per is_variable) and name the same variable."""
  if is_variable(first_variable) and is_variable(second_variable):
    return first_variable == second_variable
  return False


def is_sum(expression: Expression) -> bool:
  """True if expression is a compound sum expression, i.e. a 3-tuple whose first element is the tag '+'."""
  return isinstance(expression, tuple) and len(expression) == 3 and expression[0] == '+'


def make_sum(addend: Expression, augend: Expression) -> Expression:
  """Constructor. No simplification is required (e.g. make_sum(0, x) need not simplify to x)."""
  return ('+', addend, augend)


def addend(sum_expression: Expression) -> Expression:
  """Selector. Only valid when is_sum(sum_expression) is True."""
  if is_sum(sum_expression):
    return sum_expression[1]
  raise ValueError("Expression is not a sum")


def augend(sum_expression: Expression) -> Expression:
  """Selector. Only valid when is_sum(sum_expression) is True."""
  if is_sum(sum_expression):
    return sum_expression[2]
  raise ValueError("Expression is not a sum")


def is_product(expression: Expression) -> bool:
  """True if expression is a compound product expression, i.e. a 3-tuple whose first element is the tag '*'."""
  return isinstance(expression, tuple) and len(expression) == 3 and expression[0] == '*'


def make_product(multiplier: Expression, multiplicand: Expression) -> Expression:
  """Constructor. No simplification is required (e.g. make_product(1, x) need not simplify to x)."""
  return ('*', multiplier, multiplicand)


def multiplier(product_expression: Expression) -> Expression:
  """Selector. Only valid when is_product(product_expression) is True."""
  if is_product(product_expression):
    return product_expression[1]
  raise ValueError("Expression is not a product")


def multiplicand(product_expression: Expression) -> Expression:
  """Selector. Only valid when is_product(product_expression) is True."""
  if is_product(product_expression):
    return product_expression[2]
  raise ValueError("Expression is not a product")


def derivative(expression: Expression, variable_name: str) -> Expression:

    if is_number(expression):
        return 0

    if is_variable(expression):
        return 1 if is_same_variable(
            expression,
            variable_name
        ) else 0

    if is_sum(expression):
        return make_sum(
            derivative(addend(expression), variable_name),
            derivative(augend(expression), variable_name)
        )

    if is_product(expression):
        return make_sum(
            make_product(
                multiplier(expression),
                derivative(
                    multiplicand(expression),
                    variable_name
                )
            ),
            make_product(
                multiplicand(expression),
                derivative(
                    multiplier(expression),
                    variable_name
                )
            )
        )

    raise ValueError("Unknown expression")


"""
REAL-WORLD SEQUENCE TASK
-------------------------
A billing requirement document, written in plain English, says: "the total charge for a customer is the base fee plus the usage rate times the usage amount." Encode this requirement literally as a quoted expression — build it as data, do not evaluate it — over the variable names "base_fee", "usage_rate", and "usage_amount", then use derivative() to compute the marginal cost of usage, the derivative of that expression with respect to "usage_amount".
"""

total_charge_formula: Expression = make_sum("base_fee", make_product("usage_rate", "usage_amount"))
marginal_cost_formula: Expression = derivative(total_charge_formula, "usage_amount")

print(is_number(3))  # expect True
print(is_variable("x"))  # expect True
print(is_variable(3))  # expect False
print(is_same_variable("x", "x"))  # expect True
print(is_same_variable("x", "y"))  # expect False

sum_example = make_sum("x", 3)
print(is_sum(sum_example))  # expect True
print(addend(sum_example))  # expect 'x'
print(augend(sum_example))  # expect 3

product_example = make_product("x", "y")
print(is_product(product_example))  # expect True
print(multiplier(product_example))  # expect 'x'
print(multiplicand(product_example))  # expect 'y'

print(derivative(make_sum("x", 3), "x"))  # expect ('+', 1, 0)
print(derivative(make_product("x", "y"), "x"))  # expect ('+', ('*', 'x', 0), ('*', 'y', 1))
print(derivative("x", "y"))  # expect 0
print(derivative(3, "x"))  # expect 0

print(marginal_cost_formula)  # expect a tree that, read literally, equals 'usage_rate'

# Once you see marginal_cost_formula, it comes out to exactly "usage_rate" — but that is only correct if usage_rate is a true constant with respect to usage_amount, and the original prose requirement never actually said that; it is equally consistent with a tiered or graduated pricing scheme where usage_rate itself depends on how much has already been used. Evaluating the requirement literally, as a symbolic expression, is what exposes this ambiguity — the prose alone let it hide. Write 2-3 sentences identifying the follow-up question you would need to ask a stakeholder to resolve it.

# A key follow-up question would be:
# Does usage_rate remain fixed regardless of the customer's usage, or can it change based on the amount used (for example, through tiered or volume-based pricing)?
# If usage_rate is a constant, then the marginal cost with respect to usage_amount is simply usage_rate. However, if usage_rate itself depends on usage_amount, then the billing formula should represent that dependency explicitly, and the derivative must account for the changing rate rather than treating it as a constant.
