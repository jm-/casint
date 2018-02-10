import ctypes
import sdl2

def setpixel(renderer, x, y):
	sdl2.SDL_RenderDrawPoint(renderer, x, y)

def pxltest(renderer, x, y):
    """
    Checks the pixel at (x, y).
    Returns True if it is dark (#101010), else False.
    NB: this is an expensive method to call. Would be good to cache if possible
    """
    # define a rectangle around the pixel
    pxl = sdl2.SDL_Rect(x, y, 1, 1)
    # create a pointer to where SDL will store the pixel data
    p = ctypes.c_void_p()
    # get the pixel
    sdl2.SDL_RenderReadPixels(renderer, pxl, 0, ctypes.byref(p), 512)
    p_bytes = ctypes.cast(p, ctypes.POINTER(ctypes.c_uint8 * 4))
    m = memoryview(p_bytes)
    b = m.tobytes()
    return b == '\x10\x10\x10\x00'

def fline(renderer, x0, y0, x1, y1):
    """
    Modified Bresenham's line algorithm
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    c = 0
    points = (sdl2.SDL_Point * 128)()

    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points[c] = sdl2.SDL_Point(x, y)
            c += 1
            err -= dy
            if err <= 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points[c] = sdl2.SDL_Point(x, y)
            c += 1
            err -= dx
            if err <= 0:
                x += sx
                err += dy
            y += sy        
    points[c] = sdl2.SDL_Point(x, y)
    c += 1
    ptr = ctypes.cast(points, ctypes.POINTER(sdl2.SDL_Point))
    sdl2.SDL_RenderDrawPoints(renderer, ptr, c)

TEXT_RECTS = {
    'A':        sdl2.SDL_Rect(0,  0,  4,  6),
    'B':        sdl2.SDL_Rect(6,  0,  4,  6),
    'C':        sdl2.SDL_Rect(12, 0,  4,  6),
    'D':        sdl2.SDL_Rect(18, 0,  4,  6),
    'E':        sdl2.SDL_Rect(24, 0,  4,  6),
    'F':        sdl2.SDL_Rect(30, 0,  4,  6),
    'G':        sdl2.SDL_Rect(36, 0,  4,  6),
    'H':        sdl2.SDL_Rect(42, 0,  4,  6),
    'I':        sdl2.SDL_Rect(48, 0,  4,  6),
    'J':        sdl2.SDL_Rect(54, 0,  4,  6),
    'K':        sdl2.SDL_Rect(60, 0,  6,  6),
    'L':        sdl2.SDL_Rect(66, 0,  4,  6),
    'M':        sdl2.SDL_Rect(72, 0,  6,  6),
    'N':        sdl2.SDL_Rect(78, 0,  6,  6),
    'O':        sdl2.SDL_Rect(84, 0,  4,  6),
    'P':        sdl2.SDL_Rect(90, 0,  4,  6),
    'Q':        sdl2.SDL_Rect(0,  6,  6,  6),
    'R':        sdl2.SDL_Rect(6,  6,  4,  6),
    'S':        sdl2.SDL_Rect(12, 6,  4,  6),
    'T':        sdl2.SDL_Rect(18, 6,  4,  6),
    'U':        sdl2.SDL_Rect(24, 6,  4,  6),
    'V':        sdl2.SDL_Rect(30, 6,  4,  6),
    'W':        sdl2.SDL_Rect(36, 6,  6,  6),
    'X':        sdl2.SDL_Rect(42, 6,  4,  6),
    'Y':        sdl2.SDL_Rect(48, 6,  4,  6),
    'Z':        sdl2.SDL_Rect(54, 6,  4,  6),
    ' ':        sdl2.SDL_Rect(60, 6,  4,  6),
    'a':        sdl2.SDL_Rect(0,  24, 4,  6),
    'b':        sdl2.SDL_Rect(6,  24, 4,  6),
    'c':        sdl2.SDL_Rect(12, 24, 4,  6),
    'd':        sdl2.SDL_Rect(18, 24, 4,  6),
    'e':        sdl2.SDL_Rect(24, 24, 4,  6),
    'f':        sdl2.SDL_Rect(30, 24, 4,  6),
    'g':        sdl2.SDL_Rect(36, 24, 4,  6),
    'h':        sdl2.SDL_Rect(42, 24, 4,  6),
    'i':        sdl2.SDL_Rect(48, 24, 2,  6),
    'j':        sdl2.SDL_Rect(54, 24, 4,  6),
    'k':        sdl2.SDL_Rect(60, 24, 6,  6),
    'l':        sdl2.SDL_Rect(66, 24, 4,  6),
    'm':        sdl2.SDL_Rect(72, 24, 6,  6),
    'n':        sdl2.SDL_Rect(78, 24, 5,  6),
    'o':        sdl2.SDL_Rect(84, 24, 4,  6),
    'p':        sdl2.SDL_Rect(90, 24, 4,  6),
    'q':        sdl2.SDL_Rect(0,  30, 6,  6),
    'r':        sdl2.SDL_Rect(6,  30, 5,  6),
    's':        sdl2.SDL_Rect(12, 30, 4,  6),
    't':        sdl2.SDL_Rect(18, 30, 4,  6),
    'u':        sdl2.SDL_Rect(24, 30, 4,  6),
    'v':        sdl2.SDL_Rect(30, 30, 4,  6),
    'w':        sdl2.SDL_Rect(36, 30, 6,  6),
    'x':        sdl2.SDL_Rect(42, 30, 4,  6),
    'y':        sdl2.SDL_Rect(48, 30, 4,  6),
    'z':        sdl2.SDL_Rect(54, 30, 4,  6),
    '0':        sdl2.SDL_Rect(0,  12, 4,  6),
    '1':        sdl2.SDL_Rect(6,  12, 4,  6),
    '2':        sdl2.SDL_Rect(12, 12, 4,  6),
    '3':        sdl2.SDL_Rect(18, 12, 4,  6),
    '4':        sdl2.SDL_Rect(24, 12, 4,  6),
    '5':        sdl2.SDL_Rect(30, 12, 4,  6),
    '6':        sdl2.SDL_Rect(36, 12, 4,  6),
    '7':        sdl2.SDL_Rect(42, 12, 4,  6),
    '8':        sdl2.SDL_Rect(48, 12, 4,  6),
    '9':        sdl2.SDL_Rect(54, 12, 4,  6),
    '.':        sdl2.SDL_Rect(60, 12, 4,  6),
    ':':        sdl2.SDL_Rect(66, 18, 3,  6),
    '\'':       sdl2.SDL_Rect(90, 18, 3,  6),
    '<':        sdl2.SDL_Rect(78, 18, 4,  6),
    '>':        sdl2.SDL_Rect(84, 18, 4,  6),
    '(':        sdl2.SDL_Rect(0,  18, 3,  6),
    ')':        sdl2.SDL_Rect(6,  18, 3,  6),
    '/':        sdl2.SDL_Rect(60, 30, 4,  6),
    '=':        sdl2.SDL_Rect(72, 30, 4,  6),
    '?':        sdl2.SDL_Rect(84, 30, 4,  6),
    ',':        sdl2.SDL_Rect(48, 18, 3,  6),
    '\x89':     sdl2.SDL_Rect(72, 12, 4,  6),    # +
    '\x99':     sdl2.SDL_Rect(84, 12, 4,  6),    # -
    '\xa9':     sdl2.SDL_Rect(66, 12, 4,  6),    # *
    '\xb9':     sdl2.SDL_Rect(78, 12, 4,  6),    # /
    '\x0e':     sdl2.SDL_Rect(42, 18, 6,  6),    # ->
    '\x99':     sdl2.SDL_Rect(84, 12, 4,  6),    # -
    '\xab':     sdl2.SDL_Rect(72, 18, 2,  6),    # !
    '\xa8':     sdl2.SDL_Rect(36, 18, 4,  6),    # ^
    '\xa9':     sdl2.SDL_Rect(66, 12, 4,  6),    # x
    '\xe6\x90': sdl2.SDL_Rect(90, 6,  6,  6),    # <-
    '\x7f\x40': sdl2.SDL_Rect(0,  36, 18, 6)     # Mat
}

def text(renderer, font, x, y, message):
    i = 0
    while i < len(message):
        c = message[i]
        if c in ('\x7f', '\xe6', '\xf7'):
            i += 1
            c += message[i]
        src = TEXT_RECTS[c]
        dst = sdl2.SDL_Rect(x, y, src.w, src.h)
        sdl2.SDL_RenderCopy(renderer, font, src, dst)
        x += src.w
        i += 1
