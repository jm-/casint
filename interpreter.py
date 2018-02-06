from common import *

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


def is_variable(char):
    return char in ALPHA_MEM_CHARS


def is_numeric(char):
    return char in '01234567890.'

class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        if self.current_char == '\x00':
            self.current_char = None

    def error(self):
        raise Exception('Invalid character: pos=%d chrs=%r' % (self.pos, self.text[self.pos:self.pos+5]))

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]
            if self.current_char == '\x00':
                self.current_char = None

    def freeze(self):
        return self.pos

    def seek(self, pos):
        self.pos = pos
        self.current_char = self.text[self.pos]
        if self.current_char == '\x00':
            self.current_char = None

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def numeric(self):
        """Return a (multidigit) integer consumed from the input."""
        result = ''
        while self.current_char is not None and is_numeric(self.current_char):
            result += self.current_char
            self.advance()
        if '.' in result:
            return float(result)
        return int(result)

    def string(self):
        result = ''
        self.advance()
        while self.current_char is not None and self.current_char != '"':
            # todo: process non-characters into string
            result += self.current_char
            self.advance()
        self.advance()
        return result

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            #print repr(self.current_char)

            if self.current_char == '\xd1':
                self.advance()
                return Token(CLS, 'Cls')

            if self.current_char == '\xe8':
                self.advance()
                return Token(DSZ, 'Dsz ')

            if self.current_char == '\xe9':
                self.advance()
                return Token(ISZ, 'Isz ')

            if self.current_char == '\xeb':
                self.advance()
                return Token(VIEWWINDOW, 'ViewWindow')

            if self.current_char == '\xec':
                self.advance()
                return Token(GOTO, 'Goto ')

            if self.current_char == '\xed':
                self.advance()
                return Token(PROG, 'Prog')

            if self.current_char == '\xe2':
                self.advance()
                return Token(LBL, 'Lbl ')

            if self.current_char == '\xde':
                self.advance()
                return Token(INTG, 'Intg ')

            if self.current_char == '\xb6':
                self.advance()
                return Token(FRAC, 'Frac ')

            if self.current_char == '\xc1':
                self.advance()
                return Token(RANDNUM, 'Ran# ')

            if self.current_char == '\x7f' and self.peek() == '\x40':
                self.advance()
                self.advance()
                return Token(MAT, 'Mat ')

            if self.current_char == '\x7f' and self.peek() == '\x46':
                self.advance()
                self.advance()
                return Token(DIM, 'Dim')

            if self.current_char == '\x7f' and self.peek() == '\x8f':
                self.advance()
                self.advance()
                return Token(GETKEY, 'Getkey')

            if self.current_char == '\x7f' and self.peek() == '\xb0':
                self.advance()
                self.advance()
                return Token(AND, ' And ')

            if self.current_char == '\x7f' and self.peek() == '\xb1':
                self.advance()
                self.advance()
                return Token(OR, ' Or ')

            if self.current_char == '\xf7' and self.peek() == '\x00':
                self.advance()
                self.advance()
                return Token(IF, 'If ')

            if self.current_char == '\xf7' and self.peek() == '\x01':
                self.advance()
                self.advance()
                return Token(THEN, 'Then ')

            if self.current_char == '\xf7' and self.peek() == '\x02':
                self.advance()
                self.advance()
                return Token(ELSE, 'Else')

            if self.current_char == '\xf7' and self.peek() == '\x03':
                self.advance()
                self.advance()
                return Token(IFEND, 'IfEnd')

            if self.current_char == '\xf7' and self.peek() == '\x04':
                self.advance()
                self.advance()
                return Token(FOR, 'For ')

            if self.current_char == '\xf7' and self.peek() == '\x05':
                self.advance()
                self.advance()
                return Token(TO, 'To ')

            if self.current_char == '\xf7' and self.peek() == '\x06':
                self.advance()
                self.advance()
                return Token(STEP, 'Step ')

            if self.current_char == '\xf7' and self.peek() == '\x07':
                self.advance()
                self.advance()
                return Token(NEXT, 'Next')

            if self.current_char == '\xf7' and self.peek() == '\x08':
                self.advance()
                self.advance()
                return Token(WHILE, 'While ')

            if self.current_char == '\xf7' and self.peek() == '\x09':
                self.advance()
                self.advance()
                return Token(WHILEEND, 'WhileEnd')

            if self.current_char == '\xf7' and self.peek() == '\x0a':
                self.advance()
                self.advance()
                return Token(DO, 'Do')

            if self.current_char == '\xf7' and self.peek() == '\x0b':
                self.advance()
                self.advance()
                return Token(LPWHILE, 'LpWhile ')

            if self.current_char == '\xf7' and self.peek() == '\x0c':
                self.advance()
                self.advance()
                return Token(RETURN, 'Return')

            if self.current_char == '\xf7' and self.peek() == '\x0d':
                self.advance()
                self.advance()
                return Token(BREAK, 'Break')

            if self.current_char == '\xf7' and self.peek() == '\x0e':
                self.advance()
                self.advance()
                return Token(STOP, 'Stop')

            if self.current_char == '\xf7' and self.peek() == '\x10':
                self.advance()
                self.advance()
                return Token(LOCATE, 'Locate ')

            if self.current_char == '\xf7' and self.peek() == '\x18':
                self.advance()
                self.advance()
                return Token(CLRTEXT, 'ClrText')

            if self.current_char == '\xf7' and self.peek() == '\x93':
                self.advance()
                self.advance()
                return Token(STOPICT, 'StoPict ')

            if self.current_char == '\xf7' and self.peek() == '\x94':
                self.advance()
                self.advance()
                return Token(RCLPICT, 'RclPict ')

            if self.current_char == '\xf7' and self.peek() == '\xa4':
                self.advance()
                self.advance()
                return Token(HORIZONTAL, 'Horizontal ')

            if self.current_char == '\xf7' and self.peek() == '\xa5':
                self.advance()
                self.advance()
                return Token(TEXT, 'Text ')

            if self.current_char == '\xf7' and self.peek() == '\xa7':
                self.advance()
                self.advance()
                return Token(FLINE, 'F-Line ')

            if self.current_char == '\xf7' and self.peek() == '\xab':
                self.advance()
                self.advance()
                return Token(PXLON, 'PxlOn ')

            if self.current_char == '\xf7' and self.peek() == '\xac':
                self.advance()
                self.advance()
                return Token(PXLOFF, 'PxlOff ')

            if self.current_char == '\xf7' and self.peek() == '\xad':
                self.advance()
                self.advance()
                return Token(PXLCHG, 'PxlChg ')

            if self.current_char == '\xf7' and self.peek() == '\xaf':
                self.advance()
                self.advance()
                return Token(PXLTEST, 'PxlTest(')

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == ':':
                self.advance()
                return Token(SEMI, ':')

            if self.current_char == '=':
                self.advance()
                return Token(EQ, '==')

            if self.current_char == '\x10':
                self.advance()
                return Token(LTE, '<=')

            if self.current_char == '\x11':
                self.advance()
                return Token(NEQ, '!=')

            if self.current_char == '\x3c':
                self.advance()
                return Token(LT, '<')

            if self.current_char == '\x3e':
                self.advance()
                return Token(GT, '>')

            if self.current_char == '\x13':
                self.advance()
                return Token(INLINEIF, '=>')

            if self.current_char == '\x0d':
                self.advance()
                return Token(SEMI, 'EOL')

            if self.current_char == '\x0e':
                self.advance()
                return Token(ASSIGN, '->')

            if is_variable(self.current_char):
                token = Token(VARIABLE, self.current_char)
                self.advance()
                return token

            if is_numeric(self.current_char):
                return Token(INTEGER, self.numeric())

            if self.current_char == '"':
                return Token(STRING, self.string())

            if self.current_char == '\x89':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char in ('\x99', '\x87'):
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '\xa9':
                self.advance()
                return Token(MUL, 'x')

            if self.current_char == '\xb9':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == '{':
                self.advance()
                return Token(LBRACE, '{')

            if self.current_char == '}':
                self.advance()
                return Token(RBRACE, '}')

            if self.current_char == '[':
                self.advance()
                return Token(LBRACKET, '[')

            if self.current_char == ']':
                self.advance()
                return Token(RBRACKET, ']')

            if self.current_char == '~':
                self.advance()
                return Token(VARIABLERANGE, '~')

            self.error()

        return Token(EOF, None)


class AST(object):
    pass


class MemoryStructure(AST):
    def __init__(self, op, token):
        self.op = op
        self.token = token


class MemoryIndex(AST):
    """e.g. Mat A[1, 1]"""
    def __init__(self, left, right):
        self.left = left
        self.right = right


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.value = token.value


class StringLit(AST):
    def __init__(self, token):
        self.value = token.value


class Var(AST):
    def __init__(self, token):
        self.value = token.value


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


class Program(AST):
    def __init__(self):
        self.children = []


class IfThen(AST):
    def __init__(self, condition):
        self.condition = condition
        self.if_clause = []
        self.else_clause = []


class ForTo(AST):
    def __init__(self, start, end, step, var):
        self.start = start
        self.end = end
        self.step = step
        self.var = var
        self.children = []


class WhileLoop(AST):
    def __init__(self):
        self.condition = None
        self.children = []


class DoLpWhile(AST):
    def __init__(self):
        self.children = []
        self.condition = None


class NullaryBuiltin(AST):
    def __init__(self, op):
        self.op = op


class NullaryFunc(AST):
    def __init__(self, op):
        self.op = op


class UnaryBuiltin(AST):
    def __init__(self, op, arg1):
        self.op = op
        self.arg1 = arg1


class UnaryFunc(AST):
    def __init__(self, op, arg1):
        self.op = op
        self.arg1 = arg1


class BinaryBuiltin(AST):
    def __init__(self, op, arg1, arg2):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2


class BinaryFunc(AST):
    def __init__(self, op, arg1, arg2):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2


class TernaryBuiltin(AST):
    def __init__(self, op, arg1, arg2, arg3):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3


class QuaternaryBuiltin(AST):
    def __init__(self, op, arg1, arg2, arg3, arg4):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.arg4 = arg4


class SenaryBuiltin(AST):
    def __init__(self, op, arg1, arg2, arg3, arg4, arg5, arg6):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.arg4 = arg4
        self.arg5 = arg5
        self.arg6 = arg6


class Assign(AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class VariableRange(AST):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper


class Initialize(AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Label(AST):
    def __init__(self, op):
        self.op = op


class Goto(AST):
    def __init__(self, op):
        self.op = op


class NoOp(AST):
    pass


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax: tok=%r pos=%d chr=%r' % (self.current_token, self.lexer.pos, self.lexer.current_char))

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def try_parse(self, parse_func):
        pos = self.lexer.freeze()
        token = self.current_token
        try:
            parse_func()
            return True
        except:
            return False
        finally:
            self.lexer.seek(pos)
            self.current_token = token

    def program(self):
        """
        program : statement_list
        """
        root = Program()
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self):
        """
        statement_list : statement
                       | statement SEMI statement_list
        """
        node = self.statement()

        results = [node]

        while self.current_token.type == SEMI:
            self.eat(SEMI)
            if self.current_token.type != EOF:
                results.append(self.statement())

        return results

    def statement(self):
        """
        statement : .....
                  | empty
        """
        token = self.current_token

        if token.type == CLS:
            self.eat(CLS)
            node = NullaryBuiltin(token)

        elif token.type == CLRTEXT:
            self.eat(CLRTEXT)
            node = NullaryBuiltin(token)

        elif token.type == STRING:
            self.eat(STRING)
            node = NullaryBuiltin(token)

        elif token.type == RETURN:
            self.eat(RETURN)
            node = NullaryBuiltin(token)

        elif token.type == BREAK:
            self.eat(BREAK)
            node = NullaryBuiltin(token)

        elif token.type == STOP:
            self.eat(STOP)
            node = NullaryBuiltin(token)

        elif token.type == LBL:
            self.eat(LBL)
            node = Label(self.num())

        elif token.type == GOTO:
            self.eat(GOTO)
            node = Goto(self.num())

        elif token.type == IF:
            node = self.if_then()

        elif token.type == FOR:
            node = self.for_to()

        elif token.type == WHILE:
            node = self.while_loop()

        elif token.type == DO:
            node = self.do_loop_while()

        elif token.type == PROG:
            self.eat(PROG)
            node = UnaryBuiltin(token, self.string_literal())

        elif token.type == DSZ:
            self.eat(DSZ)
            node = UnaryBuiltin(token, self.factor_ref())

        elif token.type == ISZ:
            self.eat(ISZ)
            node = UnaryBuiltin(token, self.factor_ref())

        elif token.type == STOPICT:
            self.eat(STOPICT)
            node = UnaryBuiltin(token, self.num_limited(1, 20))

        elif token.type == RCLPICT:
            self.eat(RCLPICT)
            node = UnaryBuiltin(token, self.num_limited(1, 20))

        elif token.type == TEXT:
            self.eat(TEXT)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            self.eat(COMMA)
            arg3 = None
            if self.current_token.type == STRING:
                arg3 = self.string_literal()
            else:
                arg3 = self.expr()
            node = TernaryBuiltin(token, arg1, arg2, arg3)

        elif token.type == LOCATE:
            self.eat(LOCATE)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            self.eat(COMMA)
            arg3 = None
            if self.current_token.type == STRING:
                arg3 = self.string_literal()
            else:
                arg3 = self.expr()
            node = TernaryBuiltin(token, arg1, arg2, arg3)

        elif token.type == FLINE:
            self.eat(FLINE)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            self.eat(COMMA)
            arg3 = self.expr()
            self.eat(COMMA)
            arg4 = self.expr()
            node = QuaternaryBuiltin(token, arg1, arg2, arg3, arg4)

        elif token.type == HORIZONTAL:
            self.eat(HORIZONTAL)
            node = UnaryBuiltin(token, self.expr())

        elif token.type == PXLON:
            self.eat(PXLON)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            node = BinaryBuiltin(token, arg1, arg2)

        elif token.type == PXLOFF:
            self.eat(PXLOFF)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            node = BinaryBuiltin(token, arg1, arg2)

        elif token.type == PXLCHG:
            self.eat(PXLCHG)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            node = BinaryBuiltin(token, arg1, arg2)

        elif token.type == VIEWWINDOW:
            self.eat(VIEWWINDOW)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            self.eat(COMMA)
            arg3 = self.expr()
            self.eat(COMMA)
            arg4 = self.expr()
            self.eat(COMMA)
            arg5 = self.expr()
            self.eat(COMMA)
            arg6 = self.expr()
            node = SenaryBuiltin(token, arg1, arg2, arg3, arg4, arg5, arg6)

        elif token.type == LBRACE:
            node = self.initialize_memory()

        else:
            # read ahead.
            if self.try_parse(self.assignment_statement):
                node = self.assignment_statement()

            elif self.try_parse(self.condition) or self.try_parse(self.expr):
                node = self.inline_if()

            else:
                node = self.empty()

        #print 'statement ->', node
        return node

    def if_then(self):
        self.eat(IF)
        condition = None
        if self.try_parse(self.condition):
            condition = self.condition()
        else:
            condition = self.expr()
        root = IfThen(condition)
        self.eat(SEMI)
        self.eat(THEN)
        nodes = self.statement_list()
        for node in nodes:
            root.if_clause.append(node)
        if self.current_token.type == ELSE:
            self.eat(ELSE)
            nodes = self.statement_list()
            for node in nodes:
                root.else_clause.append(node)
        self.eat(IFEND)
        return root

    def inline_if(self):
        condition = None
        if self.try_parse(self.condition):
            condition = self.condition()
        else:
            condition = self.expr()
        root = IfThen(condition)
        self.eat(INLINEIF)
        root.if_clause.append(self.statement())
        return root

    def for_to(self):
        self.eat(FOR)
        start = self.expr()
        self.eat(ASSIGN)
        var = self.factor_ref()
        self.eat(TO)
        end = self.expr()
        step = Token(INTEGER, 1)
        if self.current_token.type == STEP:
            self.eat(STEP)
            step = self.expr()
        self.eat(SEMI)
        root = ForTo(start, end, step, var)
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        self.eat(NEXT)
        return root

    def while_loop(self):
        root = WhileLoop()
        self.eat(WHILE)
        if self.try_parse(self.condition):
            root.condition = self.condition()
        else:
            root.condition = self.expr()
        self.eat(SEMI)
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        self.eat(WHILEEND)
        return root

    def do_loop_while(self):
        root = DoLpWhile()
        self.eat(DO)
        self.eat(SEMI)
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        self.eat(LPWHILE)
        if self.try_parse(self.condition):
            root.condition = self.condition()
        else:
            root.condition = self.expr()
        return root

    def initialize_memory(self):
        self.eat(LBRACE)
        x = self.num()
        self.eat(COMMA)
        y = self.num()
        self.eat(RBRACE)
        self.eat(ASSIGN)
        self.eat(DIM)
        right = self.memory_structure()
        node = Initialize((x, y), right)
        return node

    def memory_structure(self):
        # TODO: support list too!
        op = self.current_token
        self.eat(MAT)
        token = self.current_token
        self.eat(VARIABLE)
        node = MemoryStructure(op, token)
        return node

    def memory_index(self):
        left = self.memory_structure()
        self.eat(LBRACKET)
        x = self.expr()
        self.eat(COMMA)
        y = self.expr()
        self.eat(RBRACKET)
        node = MemoryIndex(left, (x, y))
        return node

    def num(self):
        node = Num(self.current_token)
        self.eat(INTEGER)
        return node

    def num_limited(self, lower, upper):
        node = Num(self.current_token)
        self.eat(INTEGER)
        if node.value < lower or node.value > upper:
            self.error()
        return node

    def string_literal(self):
        node = StringLit(self.current_token)
        self.eat(STRING)
        return node

    def assignment_statement(self):
        left = self.expr()
        self.eat(ASSIGN)
        right = self.assignment_factor_ref()
        node = Assign(left, right)
        return node

    def variable(self):
        """
        variable : VARIABLE
        """
        node = Var(self.current_token)
        self.eat(VARIABLE)
        return node

    def empty(self):
        """An empty production"""
        return NoOp()

    def condition(self):
        """
        condition : and_condition (OR and_condition)*
        """
        node = self.and_condition()

        while self.current_token.type == OR:
            token = self.current_token
            self.eat(OR)

            node = BinOp(left=node, op=token, right=self.and_condition())

        return node

    def and_condition(self):
        """
        and_condition : bexp (AND bexp)*
        """
        node = self.bexp()

        while self.current_token.type == AND:
            token = self.current_token
            self.eat(AND)

            node = BinOp(left=node, op=token, right=self.bexp())

        return node

    def bexp(self):
        token = self.current_token
        if token.type == NOT:
            self.eat(NOT)
            node = UnaryOp(token, self.bexp())
            return node
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.condition()
            self.eat(RPAREN)
            return node
        
        left = self.expr()
        token = self.current_token

        if token.type == EQ:
            self.eat(EQ)
        elif token.type == NEQ:
            self.eat(NEQ)
        elif token.type == GT:
            self.eat(GT)
        elif token.type == LT:
            self.eat(LT)
        elif token.type == GTE:
            self.eat(GTE)
        else:
            self.eat(LTE)
        
        node = BinOp(left=left, op=token, right=self.expr())
        return node

    def expr(self):
        """
        expr : term ((PLUS | MINUS) term)*
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """
        term : term_shorthand ((MUL | DIV) term_shorthand)*
        """
        node = self.term_shorthand()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinOp(left=node, op=token, right=self.term_shorthand())

        return node

    def term_shorthand(self):
        """
        term : factor ((expr))*
             | factor (factor_ref)*
        """
        node = self.factor()

        while True:
            token = self.current_token
            if token.type in (RANDNUM, GETKEY, PXLTEST, INTG, FRAC, LPAREN):
                token = Token(MUL, '*')
                node = BinOp(left=node, op=token, right=self.factor())
            elif self.try_parse(self.factor_ref):
                token = Token(MUL, '*')
                node = BinOp(left=node, op=token, right=self.factor_ref())
            else:
                break

        return node

    def factor(self):
        """factor : PLUS factor
                  | MINUS factor
                  | INTEGER
                  | ( expr )
                  | factor_ref
        """
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == RANDNUM:
            self.eat(RANDNUM)
            node = NullaryFunc(token)
            return node
        elif token.type == GETKEY:
            self.eat(GETKEY)
            node = NullaryFunc(token)
            return node
        elif token.type == PXLTEST:
            self.eat(PXLTEST)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            self.eat(RPAREN)
            node = BinaryFunc(token, arg1, arg2)
            return node
        elif token.type == INTG:
            self.eat(INTG)
            node = UnaryFunc(token, self.term_shorthand())
            return node
        elif token.type == FRAC:
            self.eat(FRAC)
            node = UnaryFunc(token, self.term_shorthand())
            return node
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.factor_ref()
            return node

    def factor_ref(self):
        token = self.current_token
        if token.type == MAT:
            node = self.memory_index()
            return node
        else:
            node = self.variable()
            return node

    def assignment_factor_ref(self):
        token = self.current_token
        node = self.factor_ref()
        if token.type == VARIABLE and self.current_token.type == VARIABLERANGE:
            self.eat(VARIABLERANGE)
            token = self.current_token
            upper = self.factor_ref()
            if token.type != VARIABLE or ord(node.value) > ord(upper.value):
                self.error()
            node = VariableRange(node, upper)
        return node

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node
