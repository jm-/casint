import ctypes
import sdl2

def setpixel(renderer, x, y):
	sdl2.SDL_RenderDrawPoint(renderer, x, y)

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

def text(renderer, font, x, y, message):
    src = sdl2.SDL_Rect(0, 0, 6, 6)
    dst = sdl2.SDL_Rect(x, y, src.w, src.h)
    sdl2.SDL_RenderCopy(renderer, font, src, dst)
