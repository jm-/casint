from .common import *
from .ast import *
from .interpreter import (
    Lexer,
    Parser,
    LexerException,
    ParserException,
    Token,
    is_variable,
    is_numeric,
    parse_word_as_number
)


class G1mLexer(Lexer):
    def numeric(self):
        """Return a (multidigit) integer consumed from the input."""
        result = b''
        while self.current_char is not None and is_numeric(self.current_char):
            result += self.current_char
            self.advance()
        #print(f'numeric: {result}')
        return parse_word_as_number(result)


    def string(self):
        result = b''
        self.advance()
        while self.current_char is not None and self.current_char != b'"':
            result += self.current_char
            self.advance()
        self.advance()
        #print(f'string lit: {result}')
        return result


    def comment(self):
        result = b''
        while self.current_char is not None and self.current_char not in (b':', b'\x0d'):
            result += self.current_char
            self.advance()
        return result


    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:
            #print(f'{self.current_char}')

            if self.current_char == b'\xd1':
                self.advance()
                return Token(CLS, b'Cls')

            if self.current_char == b'\xe8':
                self.advance()
                return Token(DSZ, b'Dsz ')

            if self.current_char == b'\xe9':
                self.advance()
                return Token(ISZ, b'Isz ')

            if self.current_char == b'\xeb':
                self.advance()
                return Token(VIEWWINDOW, b'ViewWindow')

            if self.current_char == b'\xec':
                self.advance()
                return Token(GOTO, b'Goto ')

            if self.current_char == b'\xed':
                self.advance()
                return Token(PROG, b'Prog')

            if self.current_char == b'\xee':
                self.advance()
                return Token(GRAPHYEQ, b'Graph Y=')

            if self.current_char == b'\xe2':
                self.advance()
                return Token(LBL, b'Lbl ')

            if self.current_char == b'\x95':
                self.advance()
                return Token(LOG, b'log ')

            if self.current_char == b'\xde':
                self.advance()
                return Token(INTG, b'Intg ')

            if self.current_char == b'\xb6':
                self.advance()
                return Token(FRAC, b'Frac ')

            if self.current_char == b'\xc1':
                self.advance()
                return Token(RANDNUM, b'Ran# ')

            if self.current_char == b'\x7f' and self.peek() == b'\x40':
                self.advance()
                self.advance()
                return Token(MAT, b'Mat ')

            if self.current_char == b'\x7f' and self.peek() == b'\x46':
                self.advance()
                self.advance()
                return Token(DIM, b'Dim ')

            if self.current_char == b'\x7f' and self.peek() == b'\x8f':
                self.advance()
                self.advance()
                return Token(GETKEY, b'Getkey')

            if self.current_char == b'\x7f' and self.peek() == b'\xb0':
                self.advance()
                self.advance()
                return Token(AND, b' And ')

            if self.current_char == b'\x7f' and self.peek() == b'\xb1':
                self.advance()
                self.advance()
                return Token(OR, b' Or ')

            if self.current_char == b'\xf7' and self.peek() == b'\x00':
                self.advance()
                self.advance()
                return Token(IF, b'If ')

            if self.current_char == b'\xf7' and self.peek() == b'\x01':
                self.advance()
                self.advance()
                return Token(THEN, b'Then ')

            if self.current_char == b'\xf7' and self.peek() == b'\x02':
                self.advance()
                self.advance()
                return Token(ELSE, b'Else')

            if self.current_char == b'\xf7' and self.peek() == b'\x03':
                self.advance()
                self.advance()
                return Token(IFEND, b'IfEnd')

            if self.current_char == b'\xf7' and self.peek() == b'\x04':
                self.advance()
                self.advance()
                return Token(FOR, b'For ')

            if self.current_char == b'\xf7' and self.peek() == b'\x05':
                self.advance()
                self.advance()
                return Token(TO, b'To ')

            if self.current_char == b'\xf7' and self.peek() == b'\x06':
                self.advance()
                self.advance()
                return Token(STEP, b'Step ')

            if self.current_char == b'\xf7' and self.peek() == b'\x07':
                self.advance()
                self.advance()
                return Token(NEXT, b'Next')

            if self.current_char == b'\xf7' and self.peek() == b'\x08':
                self.advance()
                self.advance()
                return Token(WHILE, b'While ')

            if self.current_char == b'\xf7' and self.peek() == b'\x09':
                self.advance()
                self.advance()
                return Token(WHILEEND, b'WhileEnd')

            if self.current_char == b'\xf7' and self.peek() == b'\x0a':
                self.advance()
                self.advance()
                return Token(DO, b'Do')

            if self.current_char == b'\xf7' and self.peek() == b'\x0b':
                self.advance()
                self.advance()
                return Token(LPWHILE, b'LpWhile ')

            if self.current_char == b'\xf7' and self.peek() == b'\x0c':
                self.advance()
                self.advance()
                return Token(RETURN, b'Return')

            if self.current_char == b'\xf7' and self.peek() == b'\x0d':
                self.advance()
                self.advance()
                return Token(BREAK, b'Break')

            if self.current_char == b'\xf7' and self.peek() == b'\x0e':
                self.advance()
                self.advance()
                return Token(STOP, b'Stop')

            if self.current_char == b'\xf7' and self.peek() == b'\x10':
                self.advance()
                self.advance()
                return Token(LOCATE, b'Locate ')

            if self.current_char == b'\xf7' and self.peek() == b'\x18':
                self.advance()
                self.advance()
                return Token(CLRTEXT, b'ClrText')

            if self.current_char == b'\xf7' and self.peek() == b'\x93':
                self.advance()
                self.advance()
                return Token(STOPICT, b'StoPict ')

            if self.current_char == b'\xf7' and self.peek() == b'\x94':
                self.advance()
                self.advance()
                return Token(RCLPICT, b'RclPict ')

            if self.current_char == b'\xf7' and self.peek() == b'\xa4':
                self.advance()
                self.advance()
                return Token(HORIZONTAL, b'Horizontal ')

            if self.current_char == b'\xf7' and self.peek() == b'\xa5':
                self.advance()
                self.advance()
                return Token(TEXT, b'Text ')

            if self.current_char == b'\xf7' and self.peek() == b'\xa6':
                self.advance()
                self.advance()
                return Token(CIRCLE, b'Circle ')

            if self.current_char == b'\xf7' and self.peek() == b'\xa7':
                self.advance()
                self.advance()
                return Token(FLINE, b'F-Line ')

            if self.current_char == b'\xf7' and self.peek() == b'\xa8':
                self.advance()
                self.advance()
                return Token(PLOTON, b'PlotOn ')

            if self.current_char == b'\xf7' and self.peek() == b'\xab':
                self.advance()
                self.advance()
                return Token(PXLON, b'PxlOn ')

            if self.current_char == b'\xf7' and self.peek() == b'\xac':
                self.advance()
                self.advance()
                return Token(PXLOFF, b'PxlOff ')

            if self.current_char == b'\xf7' and self.peek() == b'\xad':
                self.advance()
                self.advance()
                return Token(PXLCHG, b'PxlChg ')

            if self.current_char == b'\xf7' and self.peek() == b'\xaf':
                self.advance()
                self.advance()
                return Token(PXLTEST, b'PxlTest(')

            if self.current_char == b'\xf7' and self.peek() == b'\xd3':
                self.advance()
                self.advance()
                return Token(COORDOFF, b'CoordOff')

            if self.current_char == b'\xf7' and self.peek() == b'\x7a':
                self.advance()
                self.advance()
                return Token(GRIDOFF, b'GridOff')

            if self.current_char == b'\xf7' and self.peek() == b'\xd2':
                self.advance()
                self.advance()
                return Token(AXESOFF, b'AxesOff')

            if self.current_char == b'\xf7' and self.peek() == b'\xd4':
                self.advance()
                self.advance()
                return Token(LABELOFF, b'LabelOff')

            if self.current_char == b',':
                self.advance()
                return Token(COMMA, b',')

            if self.current_char == b':':
                self.advance()
                return Token(SEMI, b':')

            if self.current_char == b'=':
                self.advance()
                return Token(EQ, b'==')

            if self.current_char == b'\x10':
                self.advance()
                return Token(LTE, b'<=')

            if self.current_char == b'\x12':
                self.advance()
                return Token(GTE, b'>=')

            if self.current_char == b'\x11':
                self.advance()
                return Token(NEQ, b'!=')

            if self.current_char == b'\x3c':
                self.advance()
                return Token(LT, b'<')

            if self.current_char == b'\x3e':
                self.advance()
                return Token(GT, b'>')

            if self.current_char == b'\x13':
                self.advance()
                return Token(INLINEIF, b'=>')

            if self.current_char == b'\x0c':
                self.advance()
                return Token(DISP, b'DISP')

            if self.current_char == b'\x0d':
                self.advance()
                return Token(SEMI, b'EOL')

            if self.current_char == b'?':
                self.advance()
                return Token(PROMPT, b'?')

            if self.current_char == b'\x0e':
                self.advance()
                return Token(ASSIGN, b'->')

            if is_variable(self.current_char):
                token = Token(VARIABLE, self.current_char)
                self.advance()
                return token

            if is_numeric(self.current_char):
                return Token(NUMBER, self.numeric())

            if self.current_char == b'"':
                return Token(STRING, self.string())

            if self.current_char == b'\'':
                return Token(COMMENT, self.comment())

            if self.current_char == b'\x89':
                self.advance()
                return Token(PLUS, b'+')

            if self.current_char in (b'\x99', b'\x87'):
                self.advance()
                return Token(MINUS, b'-')

            if self.current_char == b'\xa9':
                self.advance()
                return Token(MUL, b'x')

            if self.current_char == b'\xb9':
                self.advance()
                return Token(DIV, b'/')

            if self.current_char == b'\xa6':
                self.advance()
                return Token(INTG, b'Int ')

            if self.current_char == b'\xa8':
                self.advance()
                return Token(POWER, b'^')

            if self.current_char == b'\x8b':
                self.advance()
                return Token(SQUARED, b'^2')

            if self.current_char == b'(':
                self.advance()
                return Token(LPAREN, b'(')

            if self.current_char == b')':
                self.advance()
                return Token(RPAREN, b')')

            if self.current_char == b'{':
                self.advance()
                return Token(LBRACE, b'{')

            if self.current_char == b'}':
                self.advance()
                return Token(RBRACE, b'}')

            if self.current_char == b'[':
                self.advance()
                return Token(LBRACKET, b'[')

            if self.current_char == b']':
                self.advance()
                return Token(RBRACKET, b']')

            if self.current_char == b'~':
                self.advance()
                return Token(VARIABLERANGE, b'~')

            self.error()

        return Token(EOF, None)


class G1mParser(Parser):
    '''
    G1M has different syntax from UCB, but parses to the same AST tree.
    '''
    def statement_list(self):
        results = []
        node = self.statement()
        if node:
            results.append(node)

        while self.current_token.type in (SEMI, DISP):
            if self.current_token.type == SEMI:
                self.eat(SEMI)
            else:
                results.append(NullaryBuiltin(self.current_token))
                self.eat(DISP)

            if self.current_token.type != EOF:
                statement = self.statement()
                if statement:
                    results.append(statement)

        return results


    def statement(self):
        token = self.current_token

        if token.type == LBRACE:
            return self.initialize_memory()

        return super().statement()


    def if_then(self):
        self.eat(IF)
        condition = self.expression()
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


    def for_to(self):
        self.eat(FOR)
        start = self.expression()
        self.eat(ASSIGN)
        var = self.variable_or_mat_get()
        self.eat(TO)
        end = self.expression()
        step = Num(Token(NUMBER, 1.0))
        if self.current_token.type == STEP:
            self.eat(STEP)
            step = self.expression()
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
        root.condition = self.expression()
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
        root.condition = self.expression()
        return root


    def stopict(self, token):
        self.eat(STOPICT)
        arg1 = self.num_limited(1, 20)
        return UnaryBuiltin(token, b'StoPict', arg1)


    def rclpict(self, token):
        self.eat(RCLPICT)
        arg1 = self.num_limited(1, 20)
        return UnaryBuiltin(token, b'RclPict', arg1)


    def prog(self, token):
        self.eat(PROG)
        arg1 = self.string_literal()
        return UnaryBuiltin(token, b'Prog', arg1)


    def nullary_builtin(self, token, name):
        self.eat(token.type)
        return NullaryBuiltin(token, name)


    def nullary_func(self, token, name):
        self.eat(token.type)
        return NullaryFunc(token, name)


    def unary_builtin(self, token, name, fn1):
        self.eat(token.type)
        arg1 = fn1()
        return UnaryBuiltin(token, name, arg1)


    def unary_func(self, token, name):
        self.eat(token.type)
        arg1 = self.expression()
        return UnaryFunc(token, name, arg1)


    def binary_builtin(self, token, name):
        self.eat(token.type)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        return BinaryBuiltin(token, name, arg1, arg2)


    def pxltest(self, token):
        self.eat(PXLTEST)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(RPAREN)
        return BinaryFunc(token, b'PxlTest', arg1, arg2)


    def text(self, token):
        self.eat(TEXT)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(COMMA)
        arg3 = None
        if self.current_token.type == STRING:
            arg3 = self.string_literal()
        else:
            arg3 = self.expression()
        return TernaryBuiltin(token, b'Text', arg1, arg2, arg3)


    def locate(self, token):
        self.eat(LOCATE)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(COMMA)
        arg3 = None
        if self.current_token.type == STRING:
            arg3 = self.string_literal()
        else:
            arg3 = self.expression()
        return TernaryBuiltin(token, b'Locate', arg1, arg2, arg3)


    def quaternary_builtin(self, token, name):
        self.eat(token.type)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(COMMA)
        arg3 = self.expression()
        self.eat(COMMA)
        arg4 = self.expression()
        return QuaternaryBuiltin(token, name, arg1, arg2, arg3, arg4)


    def senary_builtin(self, token, name):
        self.eat(token.type)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(COMMA)
        arg3 = self.expression()
        self.eat(COMMA)
        arg4 = self.expression()
        self.eat(COMMA)
        arg5 = self.expression()
        self.eat(COMMA)
        arg6 = self.expression()
        return SenaryBuiltin(token, name, arg1, arg2, arg3, arg4, arg5, arg6)


    def assignment_statement(self):
        expr = self.expression()
        self.eat(ASSIGN)
        var = self.variable_or_mat_set()
        node = Assign(expr, var)
        return node


    def initialize_memory(self):
        self.eat(LBRACE)
        x = self.expression()
        self.eat(COMMA)
        y = self.expression()
        self.eat(RBRACE)
        self.eat(ASSIGN)
        self.eat(DIM)
        right = self.memory_structure()
        node = Initialize((x, y), right)
        return node
