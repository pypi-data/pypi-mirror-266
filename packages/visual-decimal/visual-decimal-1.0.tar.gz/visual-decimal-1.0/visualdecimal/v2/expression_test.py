import unittest
from decimal import Decimal

from visualdecimal.v2.expression import symbols, Mul, Add, Div, ExpressionVisitor, Expression, Const


class ExpressionTestCase(unittest.TestCase):
    def test_multiply(self):
        x, = symbols('x')
        expr = Mul(Const(Decimal(23)), x)
        result = expr.eval(variables={
            'x': Decimal(42),
        })
        self.assertEqual(result, Decimal(966))

    def test_multiply_multiple_variables(self):
        x, y = symbols('x y')
        expr = Mul(x, y)
        result = expr.eval(variables={
            'x': Decimal(42),
            'y': Decimal(23),
        })
        self.assertEqual(result, Decimal(966))

    def test_nested(self):
        x, y = symbols('x y')
        expr = Mul(
            Add(
                Div(Const(Decimal(1)), Const(Decimal(3))),
                Div(y, Const(Decimal(3)))
            ),
            x
        )
        result = expr.eval(variables={
            'x': Decimal(2),
            'y': Decimal(5)
        })
        self.assertEqual(Decimal(4), result)

    def test_more_than_two_operands(self):
        expr = Mul(
            Const(Decimal(23), meta={"name": "first"}),
            Const(Decimal(42)),
            Add(Const(Decimal(1)), Const(Decimal(11))),
        )
        result = expr.eval()
        self.assertEqual(Decimal(11592), result)


class VisitorTestCase(unittest.TestCase):
    class ExampleVisitor(ExpressionVisitor):
        def __init__(self):
            self.before_count = 0
            self.after_count = 0
            self.decimal_count = 0

        def before_expression(self, expression: Expression):
            self.before_count += 1

        def after_expression(self, expression: Expression):
            self.after_count += 1

        def on_decimal(self, value: Decimal):
            self.decimal_count += 1

    def test_visitor(self):
        visitor = self.ExampleVisitor()
        expr = Add(
            Mul(
                Const(Decimal(1), meta={"name": "hello"}),
                Const(Decimal(42)),
            ),
            Const(Decimal(2)),
        )
        expr.accept(visitor)
        self.assertEqual(5, visitor.before_count)
        self.assertEqual(5, visitor.after_count)
        self.assertEqual(3, visitor.decimal_count)


class NamedExpressionTestCase(unittest.TestCase):
    def test_expression_with_label(self):
        expr = Add(
            Const(Decimal(23), meta={"name": "hello"}),
            Const(Decimal(42), meta={"name": "world"}),
            meta={"name": "add greeting"},
        )
        self.assertEqual(65, expr.eval())


if __name__ == '__main__':
    unittest.main()
