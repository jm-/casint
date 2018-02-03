# define token types
VARIABLE = 'VARIABLE'
ASSIGN = 'ASSIGN'
INTEGER = 'INTEGER'
PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
DIV = 'DIV'
LPAREN = '('
RPAREN = ')'
CLS = 'CLS'
RCLPICT = 'RCLPICT'
VIEWWINDOW = 'VIEWWINDOW'
IF = 'IF'
DO = 'DO'
EOF = 'EOF'
SEMI = 'SEMI'


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
    return char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_null(self):
        while self.current_char is not None and self.current_char == '\x00':
            self.advance()

    def integer(self):
        """Return a (multidigit) integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            print repr(self.current_char)

            if self.current_char == '\xd1':
                self.advance()
                return Token(CLS, 'Cls')

            if self.current_char == '\xeb':
                self.advance()
                return Token(VIEWWINDOW, 'ViewWindow')

            if self.current_char == '\xf7' and self.peek() == '\x94':
                self.advance()
                self.advance()
                return Token(RCLPICT, 'RclPict')

            if self.current_char == '\xf7' and self.peek() == '\x00':
                self.advance()
                self.advance()
                return Token(IF, 'If')

            if self.current_char == '\xf7' and self.peek() == '\x0a':
                self.advance()
                self.advance()
                return Token(DO, 'Do')

            if self.current_char == '\x00':
                self.skip_null()
                continue

            if self.current_char == ':':
                self.advance()
                return Token(SEMI, ':')

            if self.current_char == '\x0d':
                self.advance()
                return Token(SEMI, 'EOL')

            if is_variable(self.current_char):
                self.advance()
                return Token(VARIABLE, self.current_char)

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            self.error()

        return Token(EOF, None)


class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Program(AST):
    def __init__(self):
        self.children = []


class DoLpWhile(AST):
    def __init__(self):


        # todo...

        self.children = []


class NullaryBuiltin(AST):
    def __init__(self, op):
        self.token = self.op = op


class UnaryBuiltin(AST):
    def __init__(self, op, arg1):
        self.token = self.op = op
        self.arg1 = arg1


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    """The Var node is constructed out of ID token."""
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NoOp(AST):
    pass


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

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
            results.append(self.statement())

        print 'returning from statement_list:', results, self.current_token

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

        elif token.type == RCLPICT:
            self.eat(RCLPICT)
            node = UnaryBuiltin(token, self.num_limited(1, 6))

        elif token.type == DO:
            self.eat(DO)

        else:
            node = self.empty()

        return node

    def num_limited(self, lower, upper):
        node = Num(self.current_token)
        self.eat(INTEGER)
        if node.value < lower or node.value > upper:
            self.error()
        return node

    def assignment_statement(self):
        """
        assignment_statement : variable ASSIGN expr
        """
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
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
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor : PLUS factor
                  | MINUS factor
                  | INTEGER
                  | LPAREN expr RPAREN
                  | variable
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
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node
