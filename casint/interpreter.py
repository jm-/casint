from .common import *
from .ast import *


class LexerException(Exception):
    pass


class ParserException(Exception):
    pass


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
    return char in b'01234567890.'


def is_ucb_word_character(char):
    return char in UCB_WORD_CHARACTERS


def parse_word_as_number(word):
    if b'.' in word:
        return float(word)
    return float(int(word))


class Lexer():
    def __init__(self, text, filepath):
        self.text = text
        self.filepath = filepath
        self.pos = 0
        self.pos_ln = 1
        self.pos_col = 1
        self.current_char = self.text[self.pos:self.pos+1]
        if self.current_char == b'\x00':
            self.current_char = None


    def error(self):
        raise LexerException(
            f'Invalid character:'
            f' filepath={self.filepath}'
            f' pos={self.pos} ln={self.pos_ln} col={self.pos_col}'
            f' chrs={self.text[self.pos:self.pos+20]}'
        )


    def advance(self):
        """Advance the `pos` pointers and set the `current_char` variable."""
        self.pos += 1
        if self.current_char == b'\n':
            self.pos_ln += 1
            self.pos_col = 1
        else:
            self.pos_col += 1

        if self.pos >= len(self.text):
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos:self.pos+1]
            if self.current_char == b'\x00':
                self.current_char = None


    def freeze(self):
        return self.pos, self.pos_ln, self.pos_col


    def seek(self, pos, ln, col):
        self.pos = pos
        self.pos_ln = ln
        self.pos_col = col
        self.current_char = self.text[self.pos:self.pos+1]
        if self.current_char == b'\x00':
            self.current_char = None


    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        char = self.text[peek_pos:peek_pos+1]
        return char


    def peek_next_token(self):
        pos, ln, col = self.freeze()
        self.advance()
        token = self.get_next_token()
        self.seek(pos, ln, col)
        return token


class Parser():
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()


    def error(self, message=''):
        raise ParserException(
            f'Invalid syntax:'
            f' tok={self.current_token}'
            f' filepath={self.lexer.filepath}'
            f' pos={self.lexer.pos} ln={self.lexer.pos_ln} col={self.lexer.pos_col}'
            f' chr={self.lexer.current_char}'
            f' msg={message}'
        )


    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f'expected {token_type} token')


    def try_parse(self, parse_func):
        pos, ln, col = self.lexer.freeze()
        token = self.current_token
        try:
            parse_func()
        except Exception as e:
            return False
        else:
            return True
        finally:
            self.lexer.seek(pos, ln, col)
            self.current_token = token


    def program(self):
        root = Program()
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        return root


    def statement(self):
        token = self.current_token

        if token.type == CLS:
            node = self.nullary_builtin(token, b'Cls', b'\xd1')

        elif token.type == COORDOFF:
            self.eat(COORDOFF)
            node = NullaryBuiltin(token, b'CoordOff', b'\xf7\xd3')

        elif token.type == GRIDOFF:
            self.eat(GRIDOFF)
            node = NullaryBuiltin(token, b'GridOff', b'\xf7\x7a')

        elif token.type == AXESOFF:
            self.eat(AXESOFF)
            node = NullaryBuiltin(token, b'AxesOff', b'\xf7\xd2')

        elif token.type == LABELOFF:
            self.eat(LABELOFF)
            node = NullaryBuiltin(token, b'LabelOff', b'\xf7\xd4')

        elif token.type == CLRTEXT:
            node = self.nullary_builtin(token, b'ClrText', b'\xf7\x18')

        elif token.type == STRING:
            node = UnaryBuiltin(token, b'Print', b'', self.string_literal())

        elif token.type == COMMENT:
            self.eat(COMMENT)
            node = Comment(token)

        elif token.type == RETURN:
            self.eat(RETURN)
            node = KeywordBuiltin(token, b'return', b'\xf7\x0c')

        elif token.type == BREAK:
            self.eat(BREAK)
            node = KeywordBuiltin(token, b'break', b'\xf7\x0d')

        elif token.type == STOP:
            self.eat(STOP)
            node = KeywordBuiltin(token, b'stop', b'\xf7\x0e')

        elif token.type == LBL:
            self.eat(LBL)
            if self.current_token.type == NUMBER:
                node = Label(self.num())
            else:
                node = Label(self.variable())

        elif token.type == GOTO:
            self.eat(GOTO)
            if self.current_token.type == NUMBER:
                node = Goto(self.num())
            else:
                node = Goto(self.variable())

        elif token.type == IF:
            node = self.if_then()

        elif token.type == FOR:
            node = self.for_to()

        elif token.type == WHILE:
            node = self.while_loop()

        elif token.type == DO:
            node = self.do_loop_while()

        elif token.type == PROG:
            node = self.prog(token)

        elif token.type == DSZ:
            node = self.unary_builtin(token, b'Dsz', b'\xe8', self.variable_or_mat_get)

        elif token.type == ISZ:
            node = self.unary_builtin(token, b'Isz', b'\xe9', self.variable_or_mat_get)

        elif token.type == STOPICT:
            node = self.stopict(token)

        elif token.type == RCLPICT:
            node = self.rclpict(token)

        elif token.type == TEXT:
            node = self.text(token)

        elif token.type == LOCATE:
            node = self.locate(token)

        elif token.type == FLINE:
            node = self.quaternary_builtin(token, b'F_Line', b'\xf7\xa7')

        elif token.type == CIRCLE:
            self.eat(CIRCLE)
            arg1 = self.expression()
            self.eat(COMMA)
            arg2 = self.expression()
            self.eat(COMMA)
            arg3 = self.expression()
            node = TernaryBuiltin(token, b'Circle', b'\xf7\xa6', arg1, arg2, arg3)

        elif token.type == HORIZONTAL:
            return self.unary_builtin(token, b'Horizontal', b'\xf7\xa4', self.expression)

        elif token.type == PLOTON:
            self.eat(PLOTON)
            arg1 = self.expression()
            self.eat(COMMA)
            arg2 = self.expression()
            node = BinaryBuiltin(token, b'PlotOn', b'\xf7\xa8', arg1, arg2)

        elif token.type == GRAPHYEQ:
            return self.unary_builtin(token, b'GraphYEq', b'\xee', self.expression)

        elif token.type == PXLON:
            node = self.binary_builtin(token, b'PxlOn', b'\xf7\xab')

        elif token.type == PXLOFF:
            node = self.binary_builtin(token, b'PxlOff', b'\xf7\xac')

        elif token.type == PXLCHG:
            node = self.binary_builtin(token, b'PxlChg', b'\xf7\xad')

        elif token.type == VIEWWINDOW:
            node = self.senary_builtin(token, b'ViewWindow', b'\xeb')

        elif token.type == LBRACKET:
            node = self.initialize_memory_values()

        else:
            # read ahead.
            if self.try_parse(self.assignment_statement):
                node = self.assignment_statement()

            elif self.try_parse(self.expression):
                node = self.expression()

                if self.current_token.type == INLINEIF:
                    # conditional jump, i.e. inline-if
                    node = self.inline_if(node)

            else:
                node = self.empty()

        return node


    def inline_if(self, condition):
        root = IfThen(condition)
        self.eat(INLINEIF)
        statement = self.statement()
        if statement:
            root.if_clause.append(statement)
        return root


    def initialize_memory_values(self):
        rows = []
        self.eat(LBRACKET)
        while self.current_token.type not in (RBRACKET, ASSIGN):
            row = []
            self.eat(LBRACKET)
            while self.current_token.type not in (RBRACKET, ASSIGN):
                row.append(self.num())
                if self.current_token.type == COMMA:
                    self.eat(COMMA)
            if self.current_token.type == RBRACKET:
                self.eat(RBRACKET)
            rows.append(row)
        if self.current_token.type == RBRACKET:
            self.eat(RBRACKET)
        self.eat(ASSIGN)
        right = self.memory_structure()
        node = Initialize(rows, right)
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
        # TODO: support list too!
        left = self.memory_structure()
        self.eat(LBRACKET)
        x = self.expression()
        self.eat(COMMA)
        y = self.expression()
        self.eat(RBRACKET)
        node = MemoryIndex(left, (x, y))
        return node


    def num(self):
        node = Num(self.current_token)
        self.eat(NUMBER)
        return node


    def num_limited(self, lower, upper):
        node = Num(self.current_token)
        self.eat(NUMBER)
        if node.value < lower or node.value > upper:
            self.error()
        return node


    def string_literal(self):
        node = StringLit(self.current_token)
        self.eat(STRING)
        return node


    def variable(self):
        node = Var(self.current_token)
        self.eat(VARIABLE)
        return node


    def empty(self):
        return None


    def expression(self):
        node = self.and_expression()

        while self.current_token.type == OR:
            token = self.current_token
            self.eat(OR)

            node = BinOp(left=node, op=token, right=self.and_expression(), ucb_repr=b'or', g1m_repr=b'\x7f\xb1')

        return node


    def and_expression(self):
        node = self.compare_eq_neq_expression()

        while self.current_token.type == AND:
            token = self.current_token
            self.eat(AND)

            node = BinOp(left=node, op=token, right=self.compare_eq_neq_expression(), ucb_repr=b'and', g1m_repr=b'\x7f\xb0')

        return node


    def compare_eq_neq_expression(self):
        node = self.compare_lt_gt_expression()

        while self.current_token.type in (EQ, NEQ):
            token = self.current_token
            ucb_repr = None
            g1m_repr = None

            if token.type == EQ:
                self.eat(EQ)
                ucb_repr = b'=='
                g1m_repr = b'='
            else:
                self.eat(NEQ)
                ucb_repr = b'!='
                g1m_repr = b'\x11'

            node = BinOp(left=node, op=token, right=self.compare_lt_gt_expression(), ucb_repr=ucb_repr, g1m_repr=g1m_repr)

        return node


    def compare_lt_gt_expression(self):
        node = self.addition_subtraction_expression()

        while self.current_token.type in (LT, LTE, GTE, GT):
            token = self.current_token
            ucb_repr = None
            g1m_repr = None

            if token.type == LT:
                self.eat(LT)
                ucb_repr = b'<'
                g1m_repr = b'\x3c'
            elif token.type == LTE:
                self.eat(LTE)
                ucb_repr = b'<='
                g1m_repr = b'\x10'
            elif token.type == GTE:
                self.eat(GTE)
                ucb_repr = b'>='
                g1m_repr = b'\x12'
            else:
                self.eat(GT)
                ucb_repr = b'>'
                g1m_repr = b'\x3e'

            node = BinOp(left=node, op=token, right=self.addition_subtraction_expression(), ucb_repr=ucb_repr, g1m_repr=g1m_repr)

        return node


    def addition_subtraction_expression(self):
        node = self.multiplication_division_expression()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            ucb_repr = None
            g1m_repr = None

            if token.type == PLUS:
                self.eat(PLUS)
                ucb_repr = b'+'
                g1m_repr = b'\x89'
            else:
                self.eat(MINUS)
                ucb_repr = b'-'
                g1m_repr = b'\x99'

            node = BinOp(left=node, op=token, right=self.multiplication_division_expression(), ucb_repr=ucb_repr, g1m_repr=g1m_repr)

        return node


    def multiplication_division_expression(self):
        node = self.unary_expression()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            ucb_repr = None
            g1m_repr = None

            if token.type == MUL:
                self.eat(MUL)
                ucb_repr = b'*'
                g1m_repr = b'\xa9'
            else:
                self.eat(DIV)
                ucb_repr = b'/'
                g1m_repr = b'\xb9'

            node = BinOp(left=node, op=token, right=self.unary_expression(), ucb_repr=ucb_repr, g1m_repr=g1m_repr)

        return node


    def unary_expression(self):
        if self.current_token.type in (PLUS, MINUS, NOT):
            token = self.current_token
            ucb_repr = None
            g1m_repr = None

            if token.type == PLUS:
                self.eat(PLUS)
                ucb_repr = b'+'
                g1m_repr = b'\x89'
            elif token.type == MINUS:
                self.eat(MINUS)
                ucb_repr = b'-'
                g1m_repr = b'\x87'
            else:
                self.eat(NOT)
                ucb_repr = b'!'
                g1m_repr = b'!'

            return UnaryOp(op=token, expr=self.exponentiation_expression(), ucb_repr=ucb_repr, g1m_repr=g1m_repr)

        return self.exponentiation_expression()


    def exponentiation_expression(self):
        node = self.implicit_multiplication_expression()

        while self.current_token.type in (POWER,):
            token = self.current_token
            ucb_repr = None
            g1m_repr = None

            self.eat(POWER)
            ucb_repr = b'**'
            g1m_repr = b'\xa8'

            node = BinOp(left=node, op=token, right=self.implicit_multiplication_expression(), ucb_repr=ucb_repr, g1m_repr=g1m_repr)

        return node


    def implicit_multiplication_expression(self):
        node = self.nullary_expression()

        # multiply adjacent highest-precedence nodes
        while self.current_token.type in (LPAREN, RANDNUM, PROMPT, GETKEY, LOG, INTG, FRAC, PXLTEST, NUMBER, MAT, VARIABLE):
            token = Token(MUL, b'*')
            node = BinOp(left=node, op=token, right=self.nullary_expression(), ucb_repr=b'*', g1m_repr=b'')

        return node


    def nullary_expression(self):
        '''
        Returns a node that is not a bin_op or unary_op
        '''
        token = self.current_token
        # scope
        if token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expression()
            self.eat(RPAREN)
            return node

        # function call (produces a value)
        elif token.type == RANDNUM:
            return self.nullary_func(token, b'RandNum', b'\xc1')
        elif token.type == PROMPT:
            return self.nullary_func(token, b'Prompt', b'?')
        elif token.type == GETKEY:
            return self.nullary_func(token, b'GetKey', b'\x7f\x8f')
        elif token.type == LOG:
            return self.unary_func(token, b'Log', b'\x95')
        elif token.type == INTG:
            return self.unary_func(token, b'Intg', b'\xde')
        elif token.type == FRAC:
            return self.unary_func(token, b'Frac', b'\xb6')
        elif token.type == PXLTEST:
            return self.pxltest(token)

        # literal
        elif token.type == NUMBER:
            self.eat(NUMBER)
            return Num(token)

        # variable/mat
        else:
            return self.variable_or_mat_get()


    def variable_or_mat_get(self):
        token = self.current_token
        if token.type == MAT:
            return self.memory_index()
        else:
            return self.variable()


    def variable_or_mat_set(self):
        token = self.current_token
        node = self.variable_or_mat_get()
        if token.type == VARIABLE and self.current_token.type == VARIABLERANGE:
            self.eat(VARIABLERANGE)
            token = self.current_token
            upper = self.variable()
            if node.value[0] > upper.value[0]:
                self.error()
            node = VariableRange(node, upper)
        return node


    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node
