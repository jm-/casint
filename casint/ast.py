from .common import *


class AST(object):
    pass


class Comment(AST):
    def __init__(self, token):
        self.comment_text = token.value

    def write_ucb(self, fp, indent):
        fp.write(b'//')
        fp.write(self.comment_text)


class MemoryStructure(AST):
    def __init__(self, op, token):
        self.op = op
        self.value = token.value

    def write_ucb(self, fp, indent):
        fp.write(self.op.value)
        fp.write(self.value)


class MemoryIndex(AST):
    """e.g. Mat A[1, 1]"""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def write_ucb(self, fp, indent):
        self.left.write_ucb(fp, indent)
        fp.write(b'[')
        self.right[0].write_ucb(fp, indent)
        fp.write(b', ')
        self.right[1].write_ucb(fp, indent)
        fp.write(b']')


class BinOp(AST):
    def __init__(self, left, op, right, ucb_repr):
        self.left = left
        self.op = op
        self.right = right
        self.ucb_repr = ucb_repr

    def write_ucb(self, fp, indent):
        if type(self.left) is BinOp:
            fp.write(b'(')
            self.left.write_ucb(fp, indent)
            fp.write(b')')
        else:
            self.left.write_ucb(fp, indent)
        fp.write(b' ')
        fp.write(self.ucb_repr)
        fp.write(b' ')
        if type(self.right) is BinOp:
            fp.write(b'(')
            self.right.write_ucb(fp, indent)
            fp.write(b')')
        else:
            self.right.write_ucb(fp, indent)


class Num(AST):
    def __init__(self, token):
        self.value = token.value

    def write_ucb(self, fp, indent):
        val = self.value
        if type(val) is float and val.is_integer():
            val = int(val)
        fp.write(bytes(str(val), 'ascii'))


class StringLit(AST):
    def __init__(self, token):
        self.value = token.value

    def write_ucb(self, fp, indent):
        fp.write(b'"')
        fp.write(translate_casio_bytes_to_ascii(self.value))
        fp.write(b'"')


class Var(AST):
    def __init__(self, token):
        self.value = token.value

    def write_ucb(self, fp, indent):
        fp.write(translate_alpha_mem_char_to_ucb(self.value))


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def write_ucb(self, fp, indent):
        fp.write(self.op.value)
        self.expr.write_ucb(fp, indent)


class Program(AST):
    def __init__(self):
        self.children = []

    def write_ucb(self, fp, indent):
        for child in self.children:
            child.write_ucb(fp, indent)


class IfThen(AST):
    def __init__(self, condition):
        self.condition = condition
        self.if_clause = []
        self.else_clause = []

    def write_ucb(self, fp, indent):
        fp.write(b'if (')
        self.condition.write_ucb(fp, indent)
        fp.write(b') {\n')
        for child in self.if_clause:
            fp.write(b' ' * UCB_INDENTATION * (indent + 1))
            child.write_ucb(fp, indent + 1)
        if self.else_clause:
            fp.write(b' ' * UCB_INDENTATION * (indent))
            fp.write(b'} else {\n')
            for child in self.else_clause:
                fp.write(b' ' * UCB_INDENTATION * (indent + 1))
                child.write_ucb(fp, indent)
        fp.write(b' ' * UCB_INDENTATION * (indent))
        fp.write(b'}\n')


class ForTo(AST):
    def __init__(self, start, end, step, var):
        self.start = start
        self.end = end
        self.step = step
        self.var = var
        self.children = []

    def write_ucb(self, fp, indent):
        fp.write(b'for (')
        self.var.write_ucb(fp, indent)
        fp.write(b' = ')
        self.start.write_ucb(fp, indent)
        fp.write(b' to ')
        self.end.write_ucb(fp, indent)
        if self.step:
            fp.write(b' step ')
            self.step.write_ucb(fp, indent)
        fp.write(b') {\n')
        for child in self.children:
            fp.write(b' ' * UCB_INDENTATION * (indent + 1))
            child.write_ucb(fp, indent + 1)
        fp.write(b' ' * UCB_INDENTATION * (indent))
        fp.write(b'}\n')


class WhileLoop(AST):
    def __init__(self):
        self.condition = None
        self.children = []

    def write_ucb(self, fp, indent):
        fp.write(b'while (')
        self.condition.write_ucb(fp, indent)
        fp.write(b') {\n')
        for child in self.children:
            fp.write(b' ' * UCB_INDENTATION * (indent + 1))
            child.write_ucb(fp, indent + 1)
        fp.write(b' ' * UCB_INDENTATION * (indent))
        fp.write(b'}\n')


class DoLpWhile(AST):
    def __init__(self):
        self.children = []
        self.condition = None

    def write_ucb(self, fp, indent):
        fp.write(b'do {\n')
        for child in self.children:
            fp.write(b' ' * UCB_INDENTATION * (indent + 1))
            child.write_ucb(fp, indent + 1)
        fp.write(b' ' * UCB_INDENTATION * (indent))
        fp.write(b'} while (')
        self.condition.write_ucb(fp, indent)
        fp.write(b');\n')


class KeywordBuiltin(AST):
    def __init__(self, op, name):
        self.op = op
        self.name = name

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b';\n')


class NullaryBuiltin(AST):
    def __init__(self, op, name):
        self.op = op
        self.name = name

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b'();\n')


class NullaryFunc(AST):
    def __init__(self, op, name):
        self.op = op
        self.name = name

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b'()')


class UnaryBuiltin(AST):
    def __init__(self, op, name, arg1):
        self.op = op
        self.name = name
        self.arg1 = arg1

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b'(')
        self.arg1.write_ucb(fp, indent)
        fp.write(b');\n')


class UnaryFunc(AST):
    def __init__(self, op, name, arg1):
        self.op = op
        self.name = name
        self.arg1 = arg1

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b'(')
        self.arg1.write_ucb(fp, indent)
        fp.write(b')')


class BinaryBuiltin(AST):
    def __init__(self, op, name, arg1, arg2):
        self.op = op
        self.name = name
        self.arg1 = arg1
        self.arg2 = arg2

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b'(')
        self.arg1.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg2.write_ucb(fp, indent)
        fp.write(b');\n')


class BinaryFunc(AST):
    def __init__(self, op, name, arg1, arg2):
        self.op = op
        self.name = name
        self.arg1 = arg1
        self.arg2 = arg2

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b'(')
        self.arg1.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg2.write_ucb(fp, indent)
        fp.write(b')')


class TernaryBuiltin(AST):
    def __init__(self, op, name, arg1, arg2, arg3):
        self.op = op
        self.name = name
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b'(')
        self.arg1.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg2.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg3.write_ucb(fp, indent)
        fp.write(b');\n')


class QuaternaryBuiltin(AST):
    def __init__(self, op, name, arg1, arg2, arg3, arg4):
        self.op = op
        self.name = name
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.arg4 = arg4

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b'(')
        self.arg1.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg2.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg3.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg4.write_ucb(fp, indent)
        fp.write(b');\n')


class SenaryBuiltin(AST):
    def __init__(self, op, name, arg1, arg2, arg3, arg4, arg5, arg6):
        self.op = op
        self.name = name
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.arg4 = arg4
        self.arg5 = arg5
        self.arg6 = arg6

    def write_ucb(self, fp, indent):
        fp.write(self.name)
        fp.write(b'(')
        self.arg1.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg2.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg3.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg4.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg5.write_ucb(fp, indent)
        fp.write(b', ')
        self.arg6.write_ucb(fp, indent)
        fp.write(b');\n')


class Assign(AST):
    def __init__(self, expr, var):
        self.expr = expr
        self.var = var

    def write_ucb(self, fp, indent):
        self.var.write_ucb(fp, indent)
        fp.write(b' = ')
        self.expr.write_ucb(fp, indent)
        fp.write(b';\n')


class VariableRange(AST):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper

    def write_ucb(self, fp, indent):
        self.lower.write_ucb(fp, indent)
        fp.write(b'~')
        self.upper.write_ucb(fp, indent)


class Initialize(AST):
    def __init__(self, dimensions, mem_struct):
        self.dimensions = dimensions
        self.mem_struct = mem_struct

    def write_ucb(self, fp, indent):
        fp.write(b'dim ')
        self.mem_struct.write_ucb(fp, indent)
        fp.write(b' = (')
        self.dimensions[0].write_ucb(fp, indent)
        fp.write(b', ')
        self.dimensions[1].write_ucb(fp, indent)
        fp.write(b');\n')


class Label(AST):
    def __init__(self, op):
        self.op = op

    def write_ucb(self, fp, indent):
        fp.write(b'label ')
        self.op.write_ucb(fp, indent)
        fp.write(b';\n')


class Goto(AST):
    def __init__(self, op):
        self.op = op

    def write_ucb(self, fp, indent):
        fp.write(b'goto ')
        self.op.write_ucb(fp, indent)
        fp.write(b';\n')
