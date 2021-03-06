# define token types
COMMENT = b'COMMENT'
VARIABLE = b'VARIABLE'
PROMPT = b'PROMPT'
ASSIGN = b'ASSIGN'
NUMBER = b'NUMBER'
STRING = b'STRING'
PLUS = b'PLUS'
MINUS = b'MINUS'
MUL = b'MUL'
DIV = b'DIV'
POWER = b'POWER'
LPAREN = b'('
RPAREN = b')'
LBRACE = b'{'
RBRACE = b'}'
LBRACKET = b'['
RBRACKET = b']'
VARIABLERANGE = b'VARIABLERANGE'
MAT = b'MAT'
COMMA = b'COMMA'
AND = b'AND'
OR = b'OR'
NOT = b'NOT'
EQ = b'EQ'
NEQ = b'NEQ'
GT = b'GT'
LT = b'LT'
GTE = b'GTE'
LTE = b'LTE'
DIM = b'DIM'
LOCATE = b'LOCATE'
CLRTEXT = b'CLRTEXT'
CLS = b'CLS'
STOPICT = b'STOPICT'
RCLPICT = b'RCLPICT'
COORDOFF = b'COORDOFF'
GRIDOFF = b'GRIDOFF'
AXESOFF = b'AXESOFF'
LABELOFF = b'LABELOFF'
GRAPHYEQ = b'GRAPHYEQ'
VIEWWINDOW = b'VIEWWINDOW'
FLINE = b'FLINE'
HORIZONTAL = b'HORIZONTAL'
CIRCLE = b'CIRCLE'
PLOTON = b'PLOTON'
PXLON = b'PXLON'
PXLOFF = b'PXLOFF'
PXLCHG = b'PXLCHG'
PXLTEST = b'PXLTEST'
INLINEIF = b'INLINEIF'
ISZ = b'ISZ'
DSZ = b'DSZ'
LOG = b'LOG'
SQUARED = b'SQUARED'
INTG = b'INTG'
FRAC = b'FRAC'
RANDNUM = b'RANDNUM'
GETKEY = b'GETKEY'
IF = b'IF'
THEN = b'THEN'
ELSE = b'ELSE'
IFEND = b'IFEND'
FOR = b'FOR'
TO = b'TO'
STEP = b'STEP'
NEXT = b'NEXT'
WHILE = b'WHILE'
WHILEEND = b'WHILEEND'
DO = b'DO'
LPWHILE = b'LPWHILE'
RETURN = b'RETURN'
BREAK = b'BREAK'
STOP = b'STOP'
LBL = b'LBL'
GOTO = b'GOTO'
EOF = b'EOF'
DISP = b'DISP'
SEMI = b'SEMI'
PROG = b'PROG'
TEXT = b'TEXT'

# special token types (debugging etc.)
SPECIAL_DEBUG = b'SPECIAL_DEBUG'

ALPHA_MEM_CHARS = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ\xcd\xce\xd0'

# table for G1M character set
CASIO_CHARS = b'\x89\x99\xab'
ASCII_CHARS = b'\x2b\x7e\x21'
CASIO_TO_ASCII_TABLE = bytes.maketrans(CASIO_CHARS, ASCII_CHARS)
ASCII_TO_CASIO_TABLE = bytes.maketrans(ASCII_CHARS, CASIO_CHARS)

UCB_INDENTATION = 4
UCB_WORD_CHARACTERS = (
    b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    b'abcdefghijklmnopqrstuvwxyz'
    b'0123456789_.'
)


def translate_casio_bytes_to_ascii(b):
    return b.translate(CASIO_TO_ASCII_TABLE)


def translate_ascii_bytes_to_casio(b):
    return b.translate(ASCII_TO_CASIO_TABLE)


def translate_alpha_mem_char_to_ucb(c):
    if c == b'\xcd':
        return b'rad'
    if c == b'\xce':
        return b'theta'
    return c
