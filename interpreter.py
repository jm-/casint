from common import *


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
            f' chrs={self.text[self.pos:self.pos+5]}'
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
                return Token(DIM, b'Dim')

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

                if word == b'for':
                    return Token(FOR, b'For ')

                if word == b'to':
                    return Token(TO, b'To ')

                if word == b'step':
                    return Token(STEP, b'Step ')

                if word == b'Text':
                    return Token(TEXT, b'Text ')

                if word == b'F_Line':
                    return Token(FLINE, b'F-Line ')

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
                if self.peek() == b'=':
                    self.advance()
                    return Token(EQ, b'==')
                return Token(ASSIGN, b'->')

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


class AST(object):
    pass


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
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def write_ucb(self, fp, indent):
        self.left.write_ucb(fp, indent)
        fp.write(b' ')
        fp.write(self.op.value)
        fp.write(b' ')
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
        fp.write(translate_string_literal(self.value))
        fp.write(b'"')


class Var(AST):
    def __init__(self, token):
        self.value = token.value

    def write_ucb(self, fp, indent):
        fp.write(self.value)


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
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def write_ucb(self, fp, indent):
        self.right.write_ucb(fp, indent)
        fp.write(b' = ')
        self.left.write_ucb(fp, indent)
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
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def write_ucb(self, fp, indent):
        fp.write(b'Dim ')
        self.right.write_ucb(fp, indent)
        fp.write(b' = (')
        self.left[0].write_ucb(fp, indent)
        fp.write(b', ')
        self.left[1].write_ucb(fp, indent)
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


class Parser():
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise ParserException(
            f'Invalid syntax:'
            f' tok={self.current_token}'
            f' pos={self.lexer.pos}'
            f' chr={self.lexer.current_char}'
        )

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
            self.eat(PROG)
            node = UnaryBuiltin(token, b'Prog', self.string_literal())

        elif token.type == DSZ:
            self.eat(DSZ)
            node = UnaryBuiltin(token, b'Dsz', self.factor_ref())

        elif token.type == ISZ:
            self.eat(ISZ)
            node = UnaryBuiltin(token, b'Isz', self.factor_ref())

        elif token.type == STOPICT:
            self.eat(STOPICT)
            node = UnaryBuiltin(token, b'StoPict', self.num_limited(1, 20))

        elif token.type == RCLPICT:
            self.eat(RCLPICT)
            node = UnaryBuiltin(token, b'RclPict', self.num_limited(1, 20))

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
            self.eat(FLINE)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            self.eat(COMMA)
            arg3 = self.expr()
            self.eat(COMMA)
            arg4 = self.expr()
            node = QuaternaryBuiltin(token, b'F_Line', arg1, arg2, arg3, arg4)

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
            self.eat(PXLON)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            node = BinaryBuiltin(token, b'PxlOn', arg1, arg2)

        elif token.type == PXLOFF:
            self.eat(PXLOFF)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            node = BinaryBuiltin(token, b'PxlOff', arg1, arg2)

        elif token.type == PXLCHG:
            self.eat(PXLCHG)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            node = BinaryBuiltin(token, b'PxlChg', arg1, arg2)

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
            node = SenaryBuiltin(token, b'ViewWindow', arg1, arg2, arg3, arg4, arg5, arg6)

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

    def assignment_statement(self):
        left = self.expr()
        self.eat(ASSIGN)
        right = self.assignment_factor_ref()
        node = Assign(left, right)
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

            node = BinOp(left=node, op=token, right=self.and_condition())

        return node

    def and_condition(self):
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
        #elif token.type == LPAREN:
        #    self.eat(LPAREN)
        #    node = self.condition()
        #    self.eat(RPAREN)
        #    return node

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
        node = self.expo()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinOp(left=node, op=token, right=self.expo())

        return node

    def expo(self):
        node = self.term_shorthand()

        while self.current_token.type in (POWER, SQUARED):
            token = self.current_token
            if token.type == POWER:
                self.eat(POWER)
            if token.type == SQUARED:
                self.eat(SQUARED)

            node = BinOp(left=node, op=token, right=self.term_shorthand())

        return node

    def term_shorthand(self):
        node = self.factor()

        while True:
            token = self.current_token
            if token.type in (RANDNUM, PROMPT, GETKEY, PXLTEST, INTG, FRAC, LPAREN):
                token = Token(MUL, b'*')
                node = BinOp(left=node, op=token, right=self.factor())
            elif self.try_parse(self.factor_ref):
                token = Token(MUL, b'*')
                node = BinOp(left=node, op=token, right=self.factor_ref())
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
            self.eat(GETKEY)
            node = NullaryFunc(token, b'GetKey')
            return node
        elif token.type == PXLTEST:
            self.eat(PXLTEST)
            arg1 = self.expr()
            self.eat(COMMA)
            arg2 = self.expr()
            self.eat(RPAREN)
            node = BinaryFunc(token, b'PxlText', arg1, arg2)
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


class G1mParser(Parser):
    '''
    G1M has different syntax from UCB, but parses to the same AST tree.
    '''
    def for_to(self):
        self.eat(FOR)
        start = self.expr()
        self.eat(ASSIGN)
        var = self.factor_ref()
        self.eat(TO)
        end = self.expr()
        step = Num(Token(NUMBER, 1.0))
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


    def text(self, token):
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
        return TernaryBuiltin(token, b'Text', arg1, arg2, arg3)


class UcbParser(Parser):
    '''
    UCB has different syntax from G1M, but parses to the same AST tree.
    '''
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
        self.eat(LBRACE)
        root = ForTo(start, end, step, var)
        nodes = self.statement_list()
        for node in nodes:
            root.children.append(node)
        self.eat(RBRACE)
        return root


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
