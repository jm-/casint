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
    is_ucb_word_character,
    parse_word_as_number
)


class UcbLexer(Lexer):
    def string(self):
        result = b''
        self.advance()
        while self.current_char is not None and self.current_char != b'"':
            result += self.current_char
            self.advance()
        self.advance()
        return translate_ascii_bytes_to_casio(result)


    def comment(self):
        result = b''
        # read until the line end
        while self.current_char is not None and self.current_char not in (b'\r', b'\n'):
            result += self.current_char
            self.advance()
        return result


    def ucb_word(self):
        result = b''
        while self.current_char is not None and is_ucb_word_character(self.current_char):
            result += self.current_char
            self.advance()
        return result


    def get_next_token(self):
        while self.current_char is not None:
            #print(f'{self.current_char}')

            if self.current_char in (b' ', b'\r', b'\n'):
                # ignore whitespace
                self.advance()
                continue

            if is_ucb_word_character(self.current_char):
                word = self.ucb_word()
                #print(f'word: {word}')

                if word == b'label':
                    return Token(LBL, b'Lbl ')

                if word == b'goto':
                    return Token(GOTO, b'Goto ')

                if word == b'return':
                    return Token(RETURN, b'Return')

                if word == b'break':
                    return Token(BREAK, b'Break')

                if word == b'stop':
                    return Token(STOP, b'Stop')

                if word == b'dim':
                    return Token(DIM, b'Dim ')

                if word == b'and':
                    return Token(AND, b' And ')

                if word == b'or':
                    return Token(OR, b' Or ')

                if word == b'if':
                    return Token(IF, b'If ')

                if word == b'else':
                    return Token(ELSE, b'Else')

                if word == b'for':
                    return Token(FOR, b'For ')

                if word == b'to':
                    return Token(TO, b'To ')

                if word == b'step':
                    return Token(STEP, b'Step ')

                if word == b'do':
                    return Token(DO, b'Do')

                if word == b'while':
                    return Token(WHILE, b'While ')

                if word == b'Isz':
                    return Token(ISZ, b'Isz ')

                if word == b'Dsz':
                    return Token(DSZ, b'Dsz ')

                if word == b'StoPict':
                    return Token(STOPICT, b'StoPict ')

                if word == b'RclPict':
                    return Token(RCLPICT, b'RclPict ')

                if word == b'Cls':
                    return Token(CLS, b'Cls')

                if word == b'log':
                    return Token(LOG, b'log ')

                if word == b'Intg':
                    return Token(INTG, b'Intg ')

                if word == b'Frac':
                    return Token(FRAC, b'Frac ')

                if word == b'RandNum':
                    return Token(RANDNUM, b'Ran# ')

                if word == b'GetKey':
                    return Token(GETKEY, b'Getkey')

                if word == b'Prog':
                    return Token(PROG, b'Prog')

                if word == b'Text':
                    return Token(TEXT, b'Text ')

                if word == b'F_Line':
                    return Token(FLINE, b'F-Line ')

                if word == b'Horizontal':
                    return Token(HORIZONTAL, b'Horizontal ')

                if word == b'PxlOn':
                    return Token(PXLON, b'PxlOn ')

                if word == b'PxlOff':
                    return Token(PXLOFF, b'PxlOff ')

                if word == b'PxlChg':
                    return Token(PXLCHG, b'PxlChg ')

                if word == b'PxlTest':
                    return Token(PXLTEST, b'PxlTest(')

                if word == b'ViewWindow':
                    return Token(VIEWWINDOW, b'ViewWindow')

                if word == b'Locate':
                    return Token(LOCATE, b'Locate ')

                if word == b'ClrText':
                    return Token(CLRTEXT, b'ClrText')

                if word == b'rad':
                    return Token(VARIABLE, b'\xcd')

                if word == b'theta':
                    return Token(VARIABLE, b'\xce')

                if word == b'Mat':
                    return Token(MAT, b'Mat ')

                if len(word) == 1 and is_variable(word):
                    return Token(VARIABLE, word)

                if is_numeric(word[0]):
                    return Token(NUMBER, parse_word_as_number(word))

                else:
                    self.error()

            if self.current_char == b'"':
                return Token(STRING, self.string())

            if self.current_char == b',':
                self.advance()
                return Token(COMMA, b',')

            if self.current_char == b';':
                self.advance()
                return Token(SEMI, b'EOL')

            if self.current_char == b'=':
                self.advance()
                if self.current_char == b'=':
                    self.advance()
                    return Token(EQ, b'==')
                return Token(ASSIGN, b'->')

            if self.current_char == b'<':
                self.advance()
                if self.current_char == b'=':
                    self.advance()
                    return Token(LTE, b'<=')
                return Token(LT, b'<')

            if self.current_char == b'>':
                self.advance()
                if self.current_char == b'=':
                    self.advance()
                    return Token(GTE, b'>=')
                return Token(GT, b'>')

            if self.current_char == b'!' and self.peek() == b'=':
                self.advance()
                self.advance()
                return Token(NEQ, b'!=')

            if self.current_char == b'+':
                self.advance()
                return Token(PLUS, b'+')

            if self.current_char == b'-':
                self.advance()
                return Token(MINUS, b'-')

            if self.current_char == b'*':
                self.advance()
                if self.current_char == b'*':
                    self.advance()
                    return Token(POWER, b'^')
                return Token(MUL, b'x')

            if self.current_char == b'/':
                self.advance()
                if self.current_char == b'/':
                    self.advance()
                    return Token(COMMENT, self.comment())
                return Token(DIV, b'/')

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


class UcbParser(Parser):
    '''
    UCB has different syntax from G1M, but parses to the same AST tree.
    '''
    def statement_list(self):
        results = []

        in_braces = self.current_token.type == LBRACE
        if in_braces:
            self.eat(LBRACE)

        while True:
            # consume tokens we don't need in the AST
            while self.current_token.type in (SEMI,):
                self.eat(self.current_token.type)

            if self.current_token.type == EOF:
                break

            if self.current_token.type == RBRACE and in_braces:
                # this brace is the end of the current statement list
                self.eat(RBRACE)
                break

            statement = self.statement()
            if not statement:
                break

            results.append(statement)

        return results


    def statement(self):
        token = self.current_token

        if token.type == DIM:
            return self.initialize_memory()

        return super().statement()


    def if_then(self):
        self.eat(IF)
        self.eat(LPAREN)
        condition = self.expression()
        root = IfThen(condition)
        self.eat(RPAREN)
        nodes = self.statement_list()
        for node in nodes:
            root.if_clause.append(node)
        if self.current_token.type == ELSE:
            self.eat(ELSE)
            nodes = self.statement_list()
            for node in nodes:
                root.else_clause.append(node)
        return root


    def for_to(self):
        self.eat(FOR)
        self.eat(LPAREN)
        var = self.variable_or_mat_get()
        self.eat(ASSIGN)
        start = self.expression()
        self.eat(TO)
        end = self.expression()
        step = Num(Token(NUMBER, 1.0))
        if self.current_token.type == STEP:
            self.eat(STEP)
            step = self.expression()
        self.eat(RPAREN)
        root = ForTo(start, end, step, var)
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        return root


    def while_loop(self):
        root = WhileLoop()
        self.eat(WHILE)
        self.eat(LPAREN)
        root.condition = self.expression()
        self.eat(RPAREN)
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        return root


    def do_loop_while(self):
        root = DoLpWhile()
        self.eat(DO)
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        self.eat(WHILE)
        self.eat(LPAREN)
        root.condition = self.expression()
        self.eat(RPAREN)
        return root


    def stopict(self, token):
        self.eat(token.type)
        self.eat(LPAREN)
        arg1 = self.num_limited(1, 20)
        self.eat(RPAREN)
        return UnaryBuiltin(token, b'StoPict', arg1)


    def rclpict(self, token):
        self.eat(token.type)
        self.eat(LPAREN)
        arg1 = self.num_limited(1, 20)
        self.eat(RPAREN)
        return UnaryBuiltin(token, b'RclPict', arg1)


    def prog(self, token):
        self.eat(PROG)
        self.eat(LPAREN)
        arg1 = self.string_literal()
        self.eat(RPAREN)
        return UnaryBuiltin(token, b'Prog', arg1)


    def nullary_builtin(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
        self.eat(RPAREN)
        return NullaryBuiltin(token, name)


    def nullary_func(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
        self.eat(RPAREN)
        return NullaryFunc(token, name)


    def unary_builtin(self, token, name, fn1):
        self.eat(token.type)
        self.eat(LPAREN)
        arg1 = fn1()
        self.eat(RPAREN)
        return UnaryBuiltin(token, name, arg1)


    def unary_func(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
        arg1 = self.expression()
        self.eat(RPAREN)
        return UnaryFunc(token, name, arg1)


    def binary_builtin(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(RPAREN)
        return BinaryBuiltin(token, name, arg1, arg2)


    def pxltest(self, token):
        self.eat(PXLTEST)
        self.eat(LPAREN)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(RPAREN)
        return BinaryFunc(token, b'PxlTest', arg1, arg2)


    def text(self, token):
        self.eat(TEXT)
        self.eat(LPAREN)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(COMMA)
        arg3 = None
        if self.current_token.type == STRING:
            arg3 = self.string_literal()
        else:
            arg3 = self.expression()
        self.eat(RPAREN)
        return TernaryBuiltin(token, b'Text', arg1, arg2, arg3)


    def locate(self, token):
        self.eat(LOCATE)
        self.eat(LPAREN)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(COMMA)
        arg3 = None
        if self.current_token.type == STRING:
            arg3 = self.string_literal()
        else:
            arg3 = self.expression()
        self.eat(RPAREN)
        return TernaryBuiltin(token, b'Locate', arg1, arg2, arg3)


    def quaternary_builtin(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
        arg1 = self.expression()
        self.eat(COMMA)
        arg2 = self.expression()
        self.eat(COMMA)
        arg3 = self.expression()
        self.eat(COMMA)
        arg4 = self.expression()
        self.eat(RPAREN)
        return QuaternaryBuiltin(token, name, arg1, arg2, arg3, arg4)


    def senary_builtin(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
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
        self.eat(RPAREN)
        return SenaryBuiltin(token, name, arg1, arg2, arg3, arg4, arg5, arg6)


    def assignment_statement(self):
        var = self.variable_or_mat_set()
        self.eat(ASSIGN)
        expr = self.expression()
        node = Assign(expr, var)
        return node


    def initialize_memory(self):
        self.eat(DIM)
        mem_struct = self.memory_structure()
        self.eat(ASSIGN)
        self.eat(LPAREN)
        x = self.expression()
        self.eat(COMMA)
        y = self.expression()
        self.eat(RPAREN)
        node = Initialize((x, y), mem_struct)
        return node
