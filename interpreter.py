from common import *
from ast import *


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
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos:self.pos+1]
        if self.current_char == b'\x00':
            self.current_char = None


    def error(self):
        raise LexerException(
            f'Invalid character:'
            f' pos={self.pos}'
            f' chrs={self.text[self.pos:self.pos+20]}'
        )


    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos:self.pos+1]
            if self.current_char == b'\x00':
                self.current_char = None


    def freeze(self):
        return self.pos


    def seek(self, pos):
        self.pos = pos
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
        pos = self.freeze()
        self.advance()
        token = self.get_next_token()
        self.seek(pos)
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
            f' pos={self.lexer.pos}'
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
        pos = self.lexer.freeze()
        token = self.current_token
        try:
            parse_func()
        except:
            return False
        else:
            return True
        finally:
            self.lexer.seek(pos)
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
            self.eat(CLS)
            node = NullaryBuiltin(token, b'Cls')

        elif token.type == COORDOFF:
            self.eat(COORDOFF)
            node = NullaryBuiltin(token, b'CoordOff')

        elif token.type == GRIDOFF:
            self.eat(GRIDOFF)
            node = NullaryBuiltin(token, b'GridOff')

        elif token.type == AXESOFF:
            self.eat(AXESOFF)
            node = NullaryBuiltin(token, b'AxesOff')

        elif token.type == LABELOFF:
            self.eat(LABELOFF)
            node = NullaryBuiltin(token, b'LabelOff')

        elif token.type == CLRTEXT:
            self.eat(CLRTEXT)
            node = NullaryBuiltin(token, b'ClrText')

        elif token.type == STRING:
            node = UnaryBuiltin(token, b'Print', self.string_literal())

        elif token.type == COMMENT:
            self.eat(COMMENT)
            # don't propagate comments to special AST nodes
            node = self.empty()

        elif token.type == RETURN:
            self.eat(RETURN)
            node = KeywordBuiltin(token, b'return')

        elif token.type == BREAK:
            self.eat(BREAK)
            node = KeywordBuiltin(token, b'break')

        elif token.type == STOP:
            self.eat(STOP)
            node = KeywordBuiltin(token, b'stop')

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
            self.eat(DSZ)
            node = UnaryBuiltin(token, b'Dsz', self.factor_ref())

        elif token.type == ISZ:
            self.eat(ISZ)
            node = UnaryBuiltin(token, b'Isz', self.factor_ref())

        elif token.type == STOPICT:
            node = self.stopict(token)

        elif token.type == RCLPICT:
            node = self.rclpict(token)

        elif token.type == TEXT:
            node = self.text(token)

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
            node = TernaryBuiltin(token, b'Locate', arg1, arg2, arg3)

        elif token.type == FLINE:
            node = self.quaternary_builtin(token, b'F_Line')

        elif token.type == CIRCLE:
            self.eat(CIRCLE)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            self.eat(COMMA)
            arg3 = self.expr()
            node = TernaryBuiltin(token, b'Circle', arg1, arg2, arg3)

        elif token.type == HORIZONTAL:
            self.eat(HORIZONTAL)
            node = UnaryBuiltin(token, b'Horizontal', self.expr())

        elif token.type == PLOTON:
            self.eat(PLOTON)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            node = BinaryBuiltin(token, b'PlotOn', arg1, arg2)

        elif token.type == GRAPHYEQ:
            self.eat(GRAPHYEQ)
            node = UnaryBuiltin(token, b'GraphYEq', self.expr())

        elif token.type == PXLON:
            node = self.binary_builtin(token, b'PxlOn')

        elif token.type == PXLOFF:
            node = self.binary_builtin(token, b'PxlOff')

        elif token.type == PXLCHG:
            node = self.binary_builtin(token, b'PxlChg')

        elif token.type == VIEWWINDOW:
            node = self.senary_builtin(token, b'ViewWindow')

        elif token.type == LBRACE:
            node = self.initialize_memory()

        elif token.type == LBRACKET:
            node = self.initialize_memory_values()

        else:
            # read ahead.
            if self.try_parse(self.assignment_statement):
                node = self.assignment_statement()

            elif self.try_parse(self.condition) or self.try_parse(self.expr):
                node = self.inline_if()

            else:
                node = self.empty()

        return node

    def inline_if(self):
        condition = None
        if self.try_parse(self.condition):
            condition = self.condition()
        else:
            condition = self.expr()
        root = IfThen(condition)
        self.eat(INLINEIF)
        statement = self.statement()
        if statement:
            root.if_clause.append(statement)
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

    def initialize_memory(self):
        self.eat(LBRACE)
        x = self.expr()
        self.eat(COMMA)
        y = self.expr()
        self.eat(RBRACE)
        self.eat(ASSIGN)
        self.eat(DIM)
        right = self.memory_structure()
        node = Initialize((x, y), right)
        return node

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

    def condition(self):
        node = self.and_condition()

        while self.current_token.type == OR:
            token = self.current_token
            self.eat(OR)

            node = BinOp(left=node, op=token, right=self.and_condition(), ucb_repr=b'or')

        return node

    def and_condition(self):
        node = self.bexp()

        while self.current_token.type == AND:
            token = self.current_token
            self.eat(AND)

            node = BinOp(left=node, op=token, right=self.bexp(), ucb_repr=b'and')

        return node

    def bexp(self):
        token = self.current_token
        if token.type == NOT:
            self.eat(NOT)
            node = UnaryOp(token, self.bexp())
            return node
        #elif token.type == LPAREN:
        #    self.eat(LPAREN)
        #    node = self.condition()
        #    self.eat(RPAREN)
        #    return node

        left = self.expr()
        token = self.current_token
        ucb_repr = None

        if token.type == EQ:
            self.eat(EQ)
            ucb_repr = b'=='
        elif token.type == NEQ:
            self.eat(NEQ)
            ucb_repr = b'!='
        elif token.type == GT:
            self.eat(GT)
            ucb_repr = b'>'
        elif token.type == LT:
            self.eat(LT)
            ucb_repr = b'<'
        elif token.type == GTE:
            self.eat(GTE)
            ucb_repr = b'>='
        else:
            self.eat(LTE)
            ucb_repr = b'<='

        node = BinOp(left=left, op=token, right=self.expr(), ucb_repr=ucb_repr)
        return node

    def expr(self):
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            ucb_repr = None
            if token.type == PLUS:
                self.eat(PLUS)
                ucb_repr = b'+'
            elif token.type == MINUS:
                self.eat(MINUS)
                ucb_repr = b'-'

            node = BinOp(left=node, op=token, right=self.term(), ucb_repr=ucb_repr)

        return node

    def term(self):
        node = self.expo()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            ucb_repr = None
            if token.type == MUL:
                self.eat(MUL)
                ucb_repr = b'*'
            elif token.type == DIV:
                self.eat(DIV)
                ucb_repr = b'/'

            node = BinOp(left=node, op=token, right=self.expo(), ucb_repr=ucb_repr)

        return node

    def expo(self):
        node = self.term_shorthand()

        while self.current_token.type in (POWER, SQUARED):
            token = self.current_token
            ucb_repr = None
            if token.type == POWER:
                self.eat(POWER)
                ucb_repr = b'**'
            if token.type == SQUARED:
                self.eat(SQUARED)
                ucb_repr = b'** 2'

            node = BinOp(left=node, op=token, right=self.term_shorthand(), ucb_repr=ucb_repr)

        return node

    def term_shorthand(self):
        node = self.factor()

        while True:
            token = self.current_token
            if token.type in (RANDNUM, PROMPT, GETKEY, PXLTEST, INTG, FRAC, LPAREN):
                token = Token(MUL, b'*')
                node = BinOp(left=node, op=token, right=self.factor(), ucb_repr=b'*')
            elif self.try_parse(self.factor_ref):
                token = Token(MUL, b'*')
                node = BinOp(left=node, op=token, right=self.factor_ref(), ucb_repr=b'*')
            else:
                break

        return node

    def factor(self):
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == NUMBER:
            self.eat(NUMBER)
            return Num(token)
        elif token.type == RANDNUM:
            self.eat(RANDNUM)
            node = NullaryFunc(token, b'RandNum')
            return node
        elif token.type == PROMPT:
            self.eat(PROMPT)
            node = NullaryFunc(token, b'Prompt')
            return node
        elif token.type == GETKEY:
            return self.nullary_func(token, b'GetKey')
        elif token.type == PXLTEST:
            self.eat(PXLTEST)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            self.eat(RPAREN)
            node = BinaryFunc(token, b'PxlTest', arg1, arg2)
            return node
        elif token.type == LOG:
            self.eat(LOG)
            node = UnaryFunc(token, b'Log', self.term_shorthand())
            return node
        elif token.type == INTG:
            self.eat(INTG)
            node = UnaryFunc(token, b'Intg', self.term_shorthand())
            return node
        elif token.type == FRAC:
            self.eat(FRAC)
            node = UnaryFunc(token, b'Frac', self.term_shorthand())
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
            if token.type != VARIABLE or node.value[0] > upper.value[0]:
                self.error()
            node = VariableRange(node, upper)
        return node

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node
