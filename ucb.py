from common import *
from ast import *
from interpreter import *


class UcbLexer(Lexer):
    def string(self):
        result = b''
        self.advance()
        while self.current_char is not None and self.current_char != b'"':
            result += self.current_char
            self.advance()
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
            print(f'{self.current_char}')

            if self.current_char in (b' ', b'\n'):
                # ignore whitespace
                self.advance()
                continue

            if is_ucb_word_character(self.current_char):
                word = self.ucb_word()
                print(f'word: {word}')

                if word == b'label':
                    return Token(LBL, b'Lbl ')

                if word == b'goto':
                    return Token(GOTO, b'Goto ')

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

                if word == b'StoPict':
                    return Token(STOPICT, b'StoPict ')

                if word == b'RclPict':
                    return Token(RCLPICT, b'RclPict ')

                if word == b'GetKey':
                    return Token(GETKEY, b'Getkey')

                if word == b'Prog':
                    return Token(PROG, b'Prog')

                if word == b'Text':
                    return Token(TEXT, b'Text ')

                if word == b'F_Line':
                    return Token(FLINE, b'F-Line ')

                if word == b'PxlOn':
                    return Token(PXLON, b'PxlOn ')

                if word == b'PxlOff':
                    return Token(PXLOFF, b'PxlOff ')

                if word == b'PxlChg':
                    return Token(PXLCHG, b'PxlChg ')

                if word == b'ViewWindow':
                    return Token(VIEWWINDOW, b'ViewWindow')

                if word == b'theta':
                    return Token(VARIABLE, b'\xcd')

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
                return Token(MUL, b'x')

            if self.current_char == b'/':
                self.advance()
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
            # consume semicolons
            while self.current_token.type == SEMI:
                self.eat(SEMI)

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


    def if_then(self):
        self.eat(IF)
        self.eat(LPAREN)
        condition = None
        if self.try_parse(self.condition):
            condition = self.condition()
        else:
            condition = self.expr()
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
        var = self.factor_ref()
        self.eat(ASSIGN)
        start = self.expr()
        self.eat(TO)
        end = self.expr()
        step = Num(Token(NUMBER, 1.0))
        if self.current_token.type == STEP:
            self.eat(STEP)
            step = self.expr()
        self.eat(RPAREN)
        root = ForTo(start, end, step, var)
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
        if self.try_parse(self.condition):
            root.condition = self.condition()
        else:
            root.condition = self.expr()
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


    def nullary_func(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
        self.eat(RPAREN)
        return NullaryFunc(token, name)


    def binary_builtin(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
        arg1 = self.expr()
        self.eat(COMMA)
        arg2 = self.expr()
        self.eat(RPAREN)
        return BinaryBuiltin(token, name, arg1, arg2)


    def text(self, token):
        self.eat(TEXT)
        self.eat(LPAREN)
        arg1 = self.expr()
        self.eat(COMMA)
        arg2 = self.expr()
        self.eat(COMMA)
        arg3 = None
        if self.current_token.type == STRING:
            arg3 = self.string_literal()
        else:
            arg3 = self.expr()
        self.eat(RPAREN)
        return TernaryBuiltin(token, b'Text', arg1, arg2, arg3)


    def quaternary_builtin(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
        arg1 = self.expr()
        self.eat(COMMA)
        arg2 = self.expr()
        self.eat(COMMA)
        arg3 = self.expr()
        self.eat(COMMA)
        arg4 = self.expr()
        self.eat(RPAREN)
        return QuaternaryBuiltin(token, name, arg1, arg2, arg3, arg4)


    def senary_builtin(self, token, name):
        self.eat(token.type)
        self.eat(LPAREN)
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
        self.eat(RPAREN)
        return SenaryBuiltin(token, name, arg1, arg2, arg3, arg4, arg5, arg6)


    def assignment_statement(self):
        left = self.assignment_factor_ref()
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, right)
        return node
