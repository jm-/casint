import sdl2

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
LBRACKET = '['
RBRACKET = ']'
VARIABLERANGE = 'VARIABLERANGE'
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
LOCATE = 'LOCATE'
CLRTEXT = 'CLRTEXT'
CLS = 'CLS'
STOPICT = 'STOPICT'
RCLPICT = 'RCLPICT'
VIEWWINDOW = 'VIEWWINDOW'
FLINE = 'FLINE'
HORIZONTAL = 'HORIZONTAL'
PXLON = 'PXLON'
PXLOFF = 'PXLOFF'
PXLCHG = 'PXLCHG'
PXLTEST = 'PXLTEST'
INLINEIF = 'INLINEIF'
ISZ = 'ISZ'
DSZ = 'DSZ'
INTG = 'INTG'
FRAC = 'FRAC'
RANDNUM = 'RANDNUM'
GETKEY = 'GETKEY'
IF = 'IF'
THEN = 'THEN'
ELSE = 'ELSE'
IFEND = 'IFEND'
FOR = 'FOR'
TO = 'TO'
STEP = 'STEP'
NEXT = 'NEXT'
WHILE = 'WHILE'
WHILEEND = 'WHILEEND'
DO = 'DO'
LPWHILE = 'LPWHILE'
RETURN = 'RETURN'
BREAK = 'BREAK'
STOP = 'STOP'
LBL = 'LBL'
GOTO = 'GOTO'
EOF = 'EOF'
SEMI = 'SEMI'
PROG = 'PROG'
TEXT = 'TEXT'

ALPHA_MEM_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ\xcd\xce\xd0'

SDL_CASIO_KEYMAP = {
	sdl2.SDLK_UP		: 28,
	sdl2.SDLK_RIGHT		: 27,
	sdl2.SDLK_DOWN		: 37,
	sdl2.SDLK_LEFT		: 38,
	sdl2.SDLK_RETURN	: 31,
	sdl2.SDLK_0			: 71,
	sdl2.SDLK_1			: 72,
	sdl2.SDLK_2			: 62,
	sdl2.SDLK_3			: 52,
	sdl2.SDLK_4			: 73,
	sdl2.SDLK_5			: 63,
	sdl2.SDLK_6			: 53,
	sdl2.SDLK_7			: 74,
	sdl2.SDLK_8			: 64,
	sdl2.SDLK_9			: 54,
	sdl2.SDLK_PERIOD	: 61,
	sdl2.SDLK_KP_0		: 71,
	sdl2.SDLK_KP_1		: 72,
	sdl2.SDLK_KP_2		: 62,
	sdl2.SDLK_KP_3		: 52,
	sdl2.SDLK_KP_4		: 73,
	sdl2.SDLK_KP_5		: 63,
	sdl2.SDLK_KP_6		: 53,
	sdl2.SDLK_KP_7		: 74,
	sdl2.SDLK_KP_8		: 64,
	sdl2.SDLK_KP_9		: 54,
	sdl2.SDLK_KP_PERIOD	: 61,
	sdl2.SDLK_F1		: 79,
	sdl2.SDLK_F2		: 69,
	sdl2.SDLK_F3		: 59,
	sdl2.SDLK_F4		: 49,
	sdl2.SDLK_F5		: 39,
	sdl2.SDLK_F6		: 29,
	sdl2.SDLK_ESCAPE	: 47,
	sdl2.SDLK_LCTRL		: 48,
	sdl2.SDLK_RCTRL		: 48
}

DEFAULT_CASIO_GETKEY = 0
