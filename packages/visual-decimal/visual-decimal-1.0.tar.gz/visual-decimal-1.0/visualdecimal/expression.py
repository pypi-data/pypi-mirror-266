from decimal import Decimal
from functools import reduce
from typing import List, Dict


def _marshal_decimal(value, **kwargs) -> Decimal:
    if isinstance(value, Expression):
        return value.eval(**kwargs)
    elif isinstance(value, Decimal):
        return value
    else:
        raise ValueError("value must be either a decimal or an expression, got {}".format(type(value)))


class Expression:
    """
    Expression is the base class for all mathematical expressions.
    """

    def __init__(self, name: str):
        """
        :param name: optional name, useful for annotations.
        """
        self.name = name

    def eval(self, **kwargs) -> Decimal:
        """
        Evaluates the mathematical expression.
        """
        raise NotImplementedError

    def accept(self, visitor: 'ExpressionVisitor'):
        """
        Accepts the expression visitor, traversing the tree structure.
        """
        visitor.before_expression(self)
        self.accept_children(visitor)
        visitor.after_expression(self)

    def accept_children(self, visitor: 'ExpressionVisitor'):
        raise NotImplementedError


class ExpressionVisitor:
    """
    ExpressionVisitor is the base class for custom visitors of an expression tree.
    """
    def before_expression(self, expression: Expression):
        """
        Called before an expression is encountered.
        """
        return

    def before_children(self, expression: Expression):
        """
        Called before children are visited.
        """
        return

    def after_children(self, expression: Expression):
        """
        Called after children have been visited.
        """
        return

    def after_expression(self, expression: Expression):
        """
        Called after an expression is encountered.
        """
        return

    def on_decimal(self, value: Decimal):
        """
        Called when a Decimal object is encountered inside an expression.
        """
        return


class Const(Expression):
    """
    Const wraps a Decimal, annotating it with a name.
    """
    def __init__(self, name: str, value: Decimal):
        super().__init__(name)
        self.value = value

    def eval(self, **kwargs):
        return self.value

    def accept_children(self, visitor: 'ExpressionVisitor'):
        visitor.on_decimal(self.value)


class NExpression(Expression):
    """
    NExpression is the base class for expressions involving a number of operands.
    """
    def __init__(self, calc, *operands, **kwargs):
        super().__init__(kwargs.pop("name", None))
        self.calc = calc
        self.operands = operands

    def eval(self, **kwargs):
        operands = [_marshal_decimal(op, **kwargs) for op in self.operands]
        return self.calc(*operands)

    def accept_children(self, visitor: 'ExpressionVisitor'):
        visitor.before_children(self)

        for op in self.operands:
            if isinstance(op, Expression):
                op.accept(visitor)
            elif isinstance(op, Decimal):
                visitor.on_decimal(op)

        visitor.after_children(self)


class Mul(NExpression):

    def __init__(self, *operands, **kwargs):
        super().__init__(lambda *ops: reduce(lambda x, y: x * y, ops), *operands, **kwargs)


class Div(NExpression):
    def __init__(self, *operands, **kwargs):
        super().__init__(lambda *ops: reduce(lambda x, y: x / y, ops), *operands, **kwargs)


class Add(NExpression):
    def __init__(self, *operands, **kwargs):
        super().__init__(lambda *ops: reduce(lambda x, y: x + y, ops), *operands, **kwargs)


class Sub(NExpression):
    def __init__(self, *operands, **kwargs):
        super().__init__(lambda *ops: reduce(lambda x, y: x - y, ops), *operands, **kwargs)


class Symbol(Expression):
    def __init__(self, name):
        if not isinstance(name, str):
            raise ValueError("name must be str")
        super().__init__(name)

    def eval(self, **kwargs) -> Decimal:
        variables = kwargs.pop("variables", None)
        if isinstance(variables, dict):
            return self.substitute(variables)
        raise ValueError("Variables must be a dictionary")

    def substitute(self, variables: Dict[str, Decimal]) -> Decimal:
        if self.name not in variables:
            raise ValueError(f'Symbol {self.name} not found in variables')
        return variables[self.name]

    def accept_children(self, visitor: 'ExpressionVisitor'):
        return


def symbols(template: str) -> List[Symbol]:
    return [
        Symbol(name)
        for name in template.split(' ')
    ]
