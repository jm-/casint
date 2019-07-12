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
    sdl2.SDL_RenderReadPixels(renderer, pxl, sdl2.SDL_PIXELFORMAT_RGBA8888, ctypes.byref(p), 512)
    p_bytes = ctypes.cast(p, ctypes.POINTER(ctypes.c_uint8 * 4))
    m = memoryview(p_bytes)
    b = m.tobytes()
    return b[1:4] == b'\x10\x10\x10'

def fline(renderer, x0, y0, x1, y1):
    """
    Modified Bresenham's line algorithm.
    Renders points to form a line between two positions.
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

def fill(renderer, x0, y0, x1, y1):
    rect = sdl2.SDL_Rect(x0, y0, x1-x0, y1-y0)
    sdl2.SDL_RenderFillRect(renderer, rect)

GRAPH_RECTS = {
    b'A':        sdl2.SDL_Rect(0,  0,  4,  6),
    b'B':        sdl2.SDL_Rect(6,  0,  4,  6),
    b'C':        sdl2.SDL_Rect(12, 0,  4,  6),
    b'D':        sdl2.SDL_Rect(18, 0,  4,  6),
    b'E':        sdl2.SDL_Rect(24, 0,  4,  6),
    b'F':        sdl2.SDL_Rect(30, 0,  4,  6),
    b'G':        sdl2.SDL_Rect(36, 0,  4,  6),
    b'H':        sdl2.SDL_Rect(42, 0,  4,  6),
    b'I':        sdl2.SDL_Rect(48, 0,  4,  6),
    b'J':        sdl2.SDL_Rect(54, 0,  4,  6),
    b'K':        sdl2.SDL_Rect(60, 0,  6,  6),
    b'L':        sdl2.SDL_Rect(66, 0,  4,  6),
    b'M':        sdl2.SDL_Rect(72, 0,  6,  6),
    b'N':        sdl2.SDL_Rect(78, 0,  6,  6),
    b'O':        sdl2.SDL_Rect(84, 0,  4,  6),
    b'P':        sdl2.SDL_Rect(90, 0,  4,  6),
    b'Q':        sdl2.SDL_Rect(0,  6,  6,  6),
    b'R':        sdl2.SDL_Rect(6,  6,  4,  6),
    b'S':        sdl2.SDL_Rect(12, 6,  4,  6),
    b'T':        sdl2.SDL_Rect(18, 6,  4,  6),
    b'U':        sdl2.SDL_Rect(24, 6,  4,  6),
    b'V':        sdl2.SDL_Rect(30, 6,  4,  6),
    b'W':        sdl2.SDL_Rect(36, 6,  6,  6),
    b'X':        sdl2.SDL_Rect(42, 6,  4,  6),
    b'Y':        sdl2.SDL_Rect(48, 6,  4,  6),
    b'Z':        sdl2.SDL_Rect(54, 6,  4,  6),
    b' ':        sdl2.SDL_Rect(60, 6,  4,  6),
    b'a':        sdl2.SDL_Rect(0,  24, 4,  6),
    b'b':        sdl2.SDL_Rect(6,  24, 4,  6),
    b'c':        sdl2.SDL_Rect(12, 24, 4,  6),
    b'd':        sdl2.SDL_Rect(18, 24, 4,  6),
    b'e':        sdl2.SDL_Rect(24, 24, 4,  6),
    b'f':        sdl2.SDL_Rect(30, 24, 4,  6),
    b'g':        sdl2.SDL_Rect(36, 24, 4,  6),
    b'h':        sdl2.SDL_Rect(42, 24, 4,  6),
    b'i':        sdl2.SDL_Rect(48, 24, 2,  6),
    b'j':        sdl2.SDL_Rect(54, 24, 4,  6),
    b'k':        sdl2.SDL_Rect(60, 24, 6,  6),
    b'l':        sdl2.SDL_Rect(66, 24, 4,  6),
    b'm':        sdl2.SDL_Rect(72, 24, 6,  6),
    b'n':        sdl2.SDL_Rect(78, 24, 5,  6),
    b'o':        sdl2.SDL_Rect(84, 24, 4,  6),
    b'p':        sdl2.SDL_Rect(90, 24, 4,  6),
    b'q':        sdl2.SDL_Rect(0,  30, 6,  6),
    b'r':        sdl2.SDL_Rect(6,  30, 5,  6),
    b's':        sdl2.SDL_Rect(12, 30, 4,  6),
    b't':        sdl2.SDL_Rect(18, 30, 4,  6),
    b'u':        sdl2.SDL_Rect(24, 30, 4,  6),
    b'v':        sdl2.SDL_Rect(30, 30, 4,  6),
    b'w':        sdl2.SDL_Rect(36, 30, 6,  6),
    b'x':        sdl2.SDL_Rect(42, 30, 4,  6),
    b'y':        sdl2.SDL_Rect(48, 30, 4,  6),
    b'z':        sdl2.SDL_Rect(54, 30, 4,  6),
    b'0':        sdl2.SDL_Rect(0,  12, 4,  6),
    b'1':        sdl2.SDL_Rect(6,  12, 4,  6),
    b'2':        sdl2.SDL_Rect(12, 12, 4,  6),
    b'3':        sdl2.SDL_Rect(18, 12, 4,  6),
    b'4':        sdl2.SDL_Rect(24, 12, 4,  6),
    b'5':        sdl2.SDL_Rect(30, 12, 4,  6),
    b'6':        sdl2.SDL_Rect(36, 12, 4,  6),
    b'7':        sdl2.SDL_Rect(42, 12, 4,  6),
    b'8':        sdl2.SDL_Rect(48, 12, 4,  6),
    b'9':        sdl2.SDL_Rect(54, 12, 4,  6),
    b'.':        sdl2.SDL_Rect(60, 12, 4,  6),
    b':':        sdl2.SDL_Rect(66, 18, 3,  6),
    b'\'':       sdl2.SDL_Rect(90, 18, 3,  6),
    b'<':        sdl2.SDL_Rect(78, 18, 4,  6),
    b'>':        sdl2.SDL_Rect(84, 18, 4,  6),
    b'(':        sdl2.SDL_Rect(0,  18, 3,  6),
    b')':        sdl2.SDL_Rect(6,  18, 3,  6),
    b'[':        sdl2.SDL_Rect(24, 18, 3,  6),
    b']':        sdl2.SDL_Rect(30, 18, 3,  6),
    b'/':        sdl2.SDL_Rect(60, 30, 4,  6),
    b'=':        sdl2.SDL_Rect(72, 30, 4,  6),
    b'?':        sdl2.SDL_Rect(84, 30, 4,  6),
    b',':        sdl2.SDL_Rect(48, 18, 3,  6),
    b'*':        sdl2.SDL_Rect(66, 30, 6,  6),
    b'#':        sdl2.SDL_Rect(90, 30, 6,  6),
    b'-':        sdl2.SDL_Rect(84, 12, 4,  6),
    b'\x89':     sdl2.SDL_Rect(72, 12, 4,  6),    # +
    b'\x99':     sdl2.SDL_Rect(84, 12, 4,  6),    # -
    b'\xa9':     sdl2.SDL_Rect(66, 12, 4,  6),    # *
    b'\xb9':     sdl2.SDL_Rect(78, 12, 4,  6),    # /
    b'\x0e':     sdl2.SDL_Rect(42, 18, 6,  6),    # ->
    b'\x99':     sdl2.SDL_Rect(84, 12, 4,  6),    # -
    b'\xab':     sdl2.SDL_Rect(72, 18, 2,  6),    # !
    b'\xa8':     sdl2.SDL_Rect(36, 18, 4,  6),    # ^
    b'\xa9':     sdl2.SDL_Rect(66, 12, 4,  6),    # x
    b'\xe6\x90': sdl2.SDL_Rect(90, 6,  6,  6),    # <-
    b'\x7f\x40': sdl2.SDL_Rect(0,  36, 18, 6)     # Mat
}

GRAPH_RECT_DEFAULT = GRAPH_RECTS[b' ']

def text(renderer, texture, x, y, message):
    i = 0
    while i < len(message):
        c = message[i:i+1]
        if c in (b'\x7f', b'\xe6', b'\xf7'):
            i += 1
            c += message[i:i+1]
        src = GRAPH_RECTS.get(c, GRAPH_RECT_DEFAULT)
        dst = sdl2.SDL_Rect(x, y, src.w, src.h)
        sdl2.SDL_RenderCopy(renderer, texture, src, dst)
        x += src.w
        i += 1

TEXT_RECTS = {
    b'A':        sdl2.SDL_Rect(0,  0,  6,  8),
    b'B':        sdl2.SDL_Rect(6,  0,  6,  8),
    b'C':        sdl2.SDL_Rect(12, 0,  6,  8),
    b'D':        sdl2.SDL_Rect(18, 0,  6,  8),
    b'E':        sdl2.SDL_Rect(24, 0,  6,  8),
    b'F':        sdl2.SDL_Rect(30, 0,  6,  8),
    b'G':        sdl2.SDL_Rect(36, 0,  6,  8),
    b'H':        sdl2.SDL_Rect(42, 0,  6,  8),
    b'I':        sdl2.SDL_Rect(48, 0,  6,  8),
    b'J':        sdl2.SDL_Rect(54, 0,  6,  8),
    b'K':        sdl2.SDL_Rect(60, 0,  6,  8),
    b'L':        sdl2.SDL_Rect(66, 0,  6,  8),
    b'M':        sdl2.SDL_Rect(72, 0,  6,  8),
    b'N':        sdl2.SDL_Rect(78, 0,  6,  8),
    b'O':        sdl2.SDL_Rect(84, 0,  6,  8),
    b'P':        sdl2.SDL_Rect(90, 0,  6,  8),
    b'Q':        sdl2.SDL_Rect(0,  8,  6,  8),
    b'R':        sdl2.SDL_Rect(6,  8,  6,  8),
    b'S':        sdl2.SDL_Rect(12, 8,  6,  8),
    b'T':        sdl2.SDL_Rect(18, 8,  6,  8),
    b'U':        sdl2.SDL_Rect(24, 8,  6,  8),
    b'V':        sdl2.SDL_Rect(30, 8,  6,  8),
    b'W':        sdl2.SDL_Rect(36, 8,  6,  8),
    b'X':        sdl2.SDL_Rect(42, 8,  6,  8),
    b'Y':        sdl2.SDL_Rect(48, 8,  6,  8),
    b'Z':        sdl2.SDL_Rect(54, 8,  6,  8),
    b' ':        sdl2.SDL_Rect(60, 8,  6,  8),
    b'a':        sdl2.SDL_Rect(0,  32, 6,  8),
    b'b':        sdl2.SDL_Rect(6,  32, 6,  8),
    b'c':        sdl2.SDL_Rect(12, 32, 6,  8),
    b'd':        sdl2.SDL_Rect(18, 32, 6,  8),
    b'e':        sdl2.SDL_Rect(24, 32, 6,  8),
    b'f':        sdl2.SDL_Rect(30, 32, 6,  8),
    b'g':        sdl2.SDL_Rect(36, 32, 6,  8),
    b'h':        sdl2.SDL_Rect(42, 32, 6,  8),
    b'i':        sdl2.SDL_Rect(48, 32, 6,  8),
    b'j':        sdl2.SDL_Rect(54, 32, 6,  8),
    b'k':        sdl2.SDL_Rect(60, 32, 6,  8),
    b'l':        sdl2.SDL_Rect(66, 32, 6,  8),
    b'm':        sdl2.SDL_Rect(72, 32, 6,  8),
    b'n':        sdl2.SDL_Rect(78, 32, 6,  8),
    b'o':        sdl2.SDL_Rect(84, 32, 6,  8),
    b'p':        sdl2.SDL_Rect(90, 32, 6,  8),
    b'q':        sdl2.SDL_Rect(0,  40, 6,  8),
    b'r':        sdl2.SDL_Rect(6,  40, 6,  8),
    b's':        sdl2.SDL_Rect(12, 40, 6,  8),
    b't':        sdl2.SDL_Rect(18, 40, 6,  8),
    b'u':        sdl2.SDL_Rect(24, 40, 6,  8),
    b'v':        sdl2.SDL_Rect(30, 40, 6,  8),
    b'w':        sdl2.SDL_Rect(36, 40, 6,  8),
    b'x':        sdl2.SDL_Rect(42, 40, 6,  8),
    b'y':        sdl2.SDL_Rect(48, 40, 6,  8),
    b'z':        sdl2.SDL_Rect(54, 40, 6,  8),
    b'0':        sdl2.SDL_Rect(0,  16, 6,  8),
    b'1':        sdl2.SDL_Rect(6,  16, 6,  8),
    b'2':        sdl2.SDL_Rect(12, 16, 6,  8),
    b'3':        sdl2.SDL_Rect(18, 16, 6,  8),
    b'4':        sdl2.SDL_Rect(24, 16, 6,  8),
    b'5':        sdl2.SDL_Rect(30, 16, 6,  8),
    b'6':        sdl2.SDL_Rect(36, 16, 6,  8),
    b'7':        sdl2.SDL_Rect(42, 16, 6,  8),
    b'8':        sdl2.SDL_Rect(48, 16, 6,  8),
    b'9':        sdl2.SDL_Rect(54, 16, 6,  8),
    b'.':        sdl2.SDL_Rect(60, 16, 6,  8),
    b':':        sdl2.SDL_Rect(66, 24, 6,  8),
    b'\'':       sdl2.SDL_Rect(90, 24, 6,  8),
    b'<':        sdl2.SDL_Rect(78, 24, 6,  8),
    b'>':        sdl2.SDL_Rect(84, 24, 6,  8),
    b'(':        sdl2.SDL_Rect(0,  24, 6,  8),
    b')':        sdl2.SDL_Rect(6,  24, 6,  8),
    b'[':        sdl2.SDL_Rect(24, 24, 6,  8),
    b']':        sdl2.SDL_Rect(30, 24, 6,  8),
    b'/':        sdl2.SDL_Rect(60, 40, 6,  8),
    b'=':        sdl2.SDL_Rect(72, 40, 6,  8),
    b'?':        sdl2.SDL_Rect(84, 40, 6,  8),
    b',':        sdl2.SDL_Rect(48, 24, 6,  8),
    b'*':        sdl2.SDL_Rect(66, 40, 6,  8),
    b'#':        sdl2.SDL_Rect(90, 40, 6,  8),
    b'-':        sdl2.SDL_Rect(84, 16, 6,  8),
    b'\x89':     sdl2.SDL_Rect(72, 16, 6,  8),    # +
    b'\x99':     sdl2.SDL_Rect(84, 16, 6,  8),    # -
    b'\xa9':     sdl2.SDL_Rect(66, 16, 6,  8),    # *
    b'\xb9':     sdl2.SDL_Rect(78, 16, 6,  8),    # /
    b'\x0e':     sdl2.SDL_Rect(42, 24, 6,  8),    # ->
    b'\x99':     sdl2.SDL_Rect(84, 16, 6,  8),    # -
    b'\xab':     sdl2.SDL_Rect(72, 24, 6,  8),    # !
    b'\xa8':     sdl2.SDL_Rect(36, 24, 6,  8),    # ^
    b'\xa9':     sdl2.SDL_Rect(66, 16, 6,  8),    # x
    b'\xe6\x90': sdl2.SDL_Rect(90, 8,  6,  8),    # <-
    b'\x7f\x40': sdl2.SDL_Rect(0,  48, 24, 8)     # Mat
}

TEXT_RECT_DEFAULT = TEXT_RECTS[b' ']

def locate(renderer, texture, x, y, message):
    i = 0
    while i < len(message):
        c = message[i:i+1]
        if c in (b'\x7f', b'\xe6', b'\xf7'):
            i += 1
            c += message[i:i+1]
        src = TEXT_RECTS.get(c, TEXT_RECT_DEFAULT)
        dst = sdl2.SDL_Rect((x-1) * 6 + 1, (y-1) * 8, src.w, src.h)
        sdl2.SDL_RenderCopy(renderer, texture, src, dst)
        x += 1
        i += 1
