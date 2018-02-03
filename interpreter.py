# define token types
VARIABLE = 'VARIABLE'
ASSIGN = 'ASSIGN'
INTEGER = 'INTEGER'
STRING = 'STRING'
PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
DIV = 'DIV'
LPAREN = '('
RPAREN = ')'
LBRACE = '{'
RBRACE = '}'
MAT = 'MAT'
COMMA = 'COMMA'
AND = 'AND'
OR = 'OR'
NOT = 'NOT'
EQ = 'EQ'
NEQ = 'NEQ'
GT = 'GT'
LT = 'LT'
GTE = 'GTE'
LTE = 'LTE'
DIM = 'DIM'
CLS = 'CLS'
RCLPICT = 'RCLPICT'
VIEWWINDOW = 'VIEWWINDOW'
IF = 'IF'
THEN = 'THEN'
ELSE = 'ELSE'
IFEND = 'IFEND'
DO = 'DO'
LPWHILE = 'LPWHILE'
BREAK = 'BREAK'
EOF = 'EOF'
SEMI = 'SEMI'
PROG = 'PROG'
TEXT = 'TEXT'


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
    return char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ\xce'


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

    def freeze(self):
        return self.pos

    def seek(self, pos):
        self.pos = pos
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

            print repr(self.current_char)

            if self.current_char == '\xd1':
                self.advance()
                return Token(CLS, 'Cls')

            if self.current_char == '\xeb':
                self.advance()
                return Token(VIEWWINDOW, 'ViewWindow')

            if self.current_char == '\xed':
                self.advance()
                return Token(PROG, 'Prog')

            if self.current_char == '\x7f' and self.peek() == '\x40':
                self.advance()
                self.advance()
                return Token(MAT, 'Mat')

            if self.current_char == '\x7f' and self.peek() == '\x46':
                self.advance()
                self.advance()
                return Token(DIM, 'Dim')

            if self.current_char == '\xf7' and self.peek() == '\x00':
                self.advance()
                self.advance()
                return Token(IF, 'If')

            if self.current_char == '\xf7' and self.peek() == '\x01':
                self.advance()
                self.advance()
                return Token(THEN, 'Then')

            if self.current_char == '\xf7' and self.peek() == '\x03':
                self.advance()
                self.advance()
                return Token(IFEND, 'IfEnd')

            if self.current_char == '\xf7' and self.peek() == '\x0a':
                self.advance()
                self.advance()
                return Token(DO, 'Do')

            if self.current_char == '\xf7' and self.peek() == '\x0d':
                self.advance()
                self.advance()
                return Token(BREAK, 'Break')

            if self.current_char == '\xf7' and self.peek() == '\x94':
                self.advance()
                self.advance()
                return Token(RCLPICT, 'RclPict')

            if self.current_char == '\xf7' and self.peek() == '\xa5':
                self.advance()
                self.advance()
                return Token(TEXT, 'Text')

            if self.current_char == '\x00':
                self.skip_null()
                continue

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == ':':
                self.advance()
                return Token(SEMI, ':')

            if self.current_char == '=':
                self.advance()
                return Token(EQ, '==')

            if self.current_char == '\x0d':
                self.advance()
                return Token(SEMI, 'EOL')

            if self.current_char == '\x0e':
                self.advance()
                return Token(ASSIGN, '=>')

            if is_variable(self.current_char):
                token = Token(VARIABLE, self.current_char)
                self.advance()
                return token

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char == '"':
                return Token(STRING, self.string())

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

            if self.current_char == '{':
                self.advance()
                return Token(LBRACE, '{')

            if self.current_char == '}':
                self.advance()
                return Token(RBRACE, '}')

            self.error()

        return Token(EOF, None)


class AST(object):
    pass


class MemoryStructure(AST):
    def __init__(self, op, token):
        self.op = op
        self.token = token


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


class DoLpWhile(AST):
    def __init__(self):
        self.children = []
        self.condition = None


class NullaryBuiltin(AST):
    def __init__(self, op):
        self.op = op


class UnaryBuiltin(AST):
    def __init__(self, op, arg1):
        self.op = op
        self.arg1 = arg1


class BinaryBuiltin(AST):
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


class Assign(AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Initialize(AST):
    def __init__(self, left, right):
        self.left = left
        self.right = right


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

    def try_expr(self):
        # tries to read an expression from the lexer
        pos = self.lexer.freeze()
        token = self.current_token
        try:
            self.expr()
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

        elif token.type == BREAK:
            self.eat(BREAK)
            node = NullaryBuiltin(token)

        elif token.type == IF:
            node = self.if_then()

        elif token.type == DO:
            node = self.do_loop_while()

        elif token.type == PROG:
            self.eat(PROG)
            node = UnaryBuiltin(token, self.string_literal())

        elif token.type == RCLPICT:
            self.eat(RCLPICT)
            node = UnaryBuiltin(token, self.num_limited(1, 20))

        elif token.type == TEXT:
            self.eat(TEXT)
            arg1 = self.num()
            self.eat(COMMA)
            arg2 = self.num()
            self.eat(COMMA)
            arg3 = self.string_literal()
            node = TernaryBuiltin(token, arg1, arg2, arg3)

        elif token.type == LBRACE:
            node = self.initialize_memory()

        else:
            # read ahead. it might be part of an assignment statement
            if self.try_expr():
                node = self.assignment_statement()

            else:
                node = self.empty()


        print 'statement ->', node
        return node

    def if_then(self):
        self.eat(IF)
        root = IfThen(self.condition())
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

    def do_loop_while(self):
        root = DoLpWhile()
        self.eat(DO)
        self.eat(SEMI)
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        self.eat(LPWHILE)
        root.condition = self.condition()
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
        right = self.variable()
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
        print token
        if token.type == NOT:
            self.eat(NOT)
            node = UnaryOp(token, self.condition())
            return node
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.condition()
            self.eat(RPAREN)
            return node
        
        left = self.expr()
        token = self.current_token
        print token

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
        print token
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
