import ctypes

import sdl2

from common import *
from graphics import fline

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        print 'DBG: invoking %s' % (method_name,)
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class CasioInterpreter(NodeVisitor):
    def __init__(self, programs):
        self.running = True

        self.programs = {}
        for program in programs:
            self.programs[program.name] = program

        # initialize
        self._initialize_vars()
        self._initialize_mats()
        self._initialize_pics()
        self._initialize_sdl2()

        self._refresh_screen()

    def _initialize_vars(self):
        self.vars = dict((v, 0) for v in ALPHA_MEM_CHARS)

    def _initialize_mats(self):
        self.mats = dict()

    def _initialize_pics(self):
        self.pics = dict()

    def _initialize_sdl2(self):
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

        self.window = sdl2.SDL_CreateWindow(
            "CASINT - CASIO Basic Interpreter - JGames 2018",
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            512, 256, sdl2.SDL_WINDOW_SHOWN)

        self.renderer = sdl2.SDL_CreateRenderer(
            self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)

        sdl2.SDL_RenderSetLogicalSize(self.renderer, 128, 64)

        self.texture = sdl2.SDL_CreateTexture(
            self.renderer, sdl2.SDL_PIXELFORMAT_RGBA8888,
            sdl2.SDL_TEXTUREACCESS_TARGET, 128, 64)

        # render to texture
        sdl2.SDL_SetRenderTarget(self.renderer, self.texture)

        # clear the screen
        self._set_color(False)
        sdl2.SDL_RenderClear(self.renderer)

        # reset render target
        sdl2.SDL_SetRenderTarget(self.renderer, None)

    def _render_begin(self):
        sdl2.SDL_SetRenderTarget(self.renderer, self.texture)

    def _render_end(self):
        sdl2.SDL_SetRenderTarget(self.renderer, None)
        # TODO: should we call this here?
        self._refresh_screen()

    def _set_color(self, is_on):
        if is_on:
            sdl2.SDL_SetRenderDrawColor(self.renderer, 0x10, 0x10, 0x10, sdl2.SDL_ALPHA_OPAQUE)
        else:
            sdl2.SDL_SetRenderDrawColor(self.renderer, 0xf7, 0xe0, 0xbc, sdl2.SDL_ALPHA_OPAQUE)

    def _refresh_screen(self):
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, None)
        sdl2.SDL_RenderPresent(self.renderer)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sdl2.SDL_DestroyTexture(self.texture)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_Quit()

    def run(self, name):
        program = self.programs.get(name)
        self.visit(program.tree)

    def idle(self):
        event = sdl2.SDL_Event()
        while self.running:
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False
                    break

            self._render_begin()
            self._render_end()

            sdl2.SDL_Delay(50)

    # =========================================================================
    # Node processing starts here!
    # =========================================================================

    def visit_Program(self, node):
        for statement in node.children:
            self.visit(statement)

    def visit_SenaryBuiltin(self, node):
        if node.op.type == VIEWWINDOW:
            # check that it matches our implementation
            assert self.visit(node.arg1) == 1
            assert self.visit(node.arg2) == 127
            assert self.visit(node.arg3) == 0
            assert self.visit(node.arg4) == 63
            assert self.visit(node.arg5) == 1
            assert self.visit(node.arg6) == 0
        else:
            raise Exception('Unknown SenaryBuiltin op type: {}'.format(node.op.type))

    def visit_QuaternaryBuiltin(self, node):
        if node.op.type == FLINE:
            x0 = self.visit(node.arg1)
            y0 = self.visit(node.arg2)
            x1 = self.visit(node.arg3)
            y1 = self.visit(node.arg4)
            self._render_begin()
            self._set_color(True)
            fline(self.renderer, x0, y0, x1, y1)
            self._render_end()
        else:
            raise Exception('Unknown QuaternaryBuiltin op type: {}'.format(node.op.type))

    def visit_Num(self, node):
        return node.value
