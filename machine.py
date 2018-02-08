import ctypes

import sdl2

from common import *
from interpreter import Var, MemoryIndex
from graphics import setpixel, fline, text

SDL_DELAY_MILLIS = 25

class NodeVisitor(object):
    def _visit(self, node):
        method_name = '_visit_' + type(node).__name__
        print 'DBG: invoking %s' % (method_name,)
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        raise Exception('No _visit_{} method'.format(type(node).__name__))


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
            'CASINT: CASIO Basic Interpreter',
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

        self.texture_font = self._load_texture('img/text.bmp')

    def _load_texture(self, filename):
        surface = sdl2.SDL_LoadBMP(filename)
        texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
        # free the surface
        sdl2.SDL_FreeSurface(surface)
        return texture

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
            sdl2.SDL_SetRenderDrawColor(self.renderer, 0xe8, 0xe8, 0xee, sdl2.SDL_ALPHA_OPAQUE)

    def _refresh_screen(self):
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, None)
        sdl2.SDL_RenderPresent(self.renderer)

    def _set_window_title(self, name):
        sdl2.SDL_SetWindowTitle(self.window, name + ' - CASINT: CASIO Basic Interpreter')

    def _handle_events(self):
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                self.running = False
                break

        sdl2.SDL_Delay(SDL_DELAY_MILLIS)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sdl2.SDL_DestroyTexture(self.texture)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_Quit()

    def run(self, name):
        program = self.programs.get(name)
        self._set_window_title(name)
        self._visit(program.tree)

    def idle(self):
        while self.running:
            self._handle_events()

    # =========================================================================
    # Node processing starts here!
    # =========================================================================

    def _assign(self, value, node):
        if type(node) is Var:
            self.vars[node.value] = value

        elif type(node) is MemoryIndex:
            if node.left.op.type == MAT:
                raise Exception('matrix assignment is unimplemented')
            else:
                raise Exception('Unknown memory index assignment: {}'.format(node.left.op.type))

        else:
            raise Exception('Unknown variable assignment node: {}'.format(type(node).__name__))

    def _retrieve(self, node):
        if type(node) is Var:
            return self.vars[node.value]

        elif type(node) is MemoryIndex:
            if node.left.op.type == MAT:
                raise Exception('matrix retrieval is unimplemented')
            else:
                raise Exception('Unknown memory index retrieval: {}'.format(node.left.op.type))

        else:
            raise Exception('Unknown variable retrieval node: {}'.format(type(node).__name__))

    def _visit_NoOp(self, node):
        pass

    def _visit_Program(self, node):
        for statement in node.children:
            self._visit(statement)

    def _visit_SenaryBuiltin(self, node):
        if node.op.type == VIEWWINDOW:
            # check that it matches our implementation
            assert self._visit(node.arg1) == 1
            assert self._visit(node.arg2) == 127
            assert self._visit(node.arg3) == 0
            assert self._visit(node.arg4) == 63
            assert self._visit(node.arg5) == 1
            assert self._visit(node.arg6) == 0
        else:
            raise Exception('Unknown SenaryBuiltin op type: {}'.format(node.op.type))

    def _visit_QuaternaryBuiltin(self, node):
        if node.op.type == FLINE:
            x0 = self._visit(node.arg1)
            y0 = self._visit(node.arg2)
            x1 = self._visit(node.arg3)
            y1 = self._visit(node.arg4)
            self._render_begin()
            self._set_color(True)
            fline(self.renderer, x0, y0, x1, y1)
            self._render_end()
            self._handle_events()
        else:
            raise Exception('Unknown QuaternaryBuiltin op type: {}'.format(node.op.type))

    def _visit_TernaryBuiltin(self, node):
        if node.op.type == TEXT:
            y = self._visit(node.arg1)
            x = self._visit(node.arg2)
            s = self._visit(node.arg3)
            self._render_begin()
            self._set_color(True)
            text(self.renderer, self.texture_font, x, y, s)
            self._render_end()
            self._handle_events()
        else:
            raise Exception('Unknown QuaternaryBuiltin op type: {}'.format(node.op.type))

    def _visit_BinaryBuiltin(self, node):
        if node.op.type == PXLON:
            y = self._visit(node.arg1)
            x = self._visit(node.arg2)
            self._render_begin()
            self._set_color(True)
            setpixel(self.renderer, x, y)
            self._render_end()
            self._handle_events()
        elif node.op.type == PXLOFF:
            y = self._visit(node.arg1)
            x = self._visit(node.arg2)
            self._render_begin()
            self._set_color(False)
            setpixel(self.renderer, x, y)
            self._render_end()
            self._handle_events()
        else:
            raise Exception('Unknown BinaryBuiltin op type: {}'.format(node.op.type))

    def _visit_UnaryBuiltin(self, node):
        if node.op.type == HORIZONTAL:
            y = self._visit(node.arg1)
            self._render_begin()
            self._set_color(True)
            fline(self.renderer, 1, y, 127, y)
            self._render_end()
        else:
            raise Exception('Unknown UnaryBuiltin op type: {}'.format(node.op.type))

    def _visit_Num(self, node):
        return node.value

    def _visit_Var(self, node):
        return self._retrieve(node)

    def _visit_StringLit(self, node):
        return node.value

    def _visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self._visit(node.left) + self._visit(node.right)
        elif node.op.type == MINUS:
            return self._visit(node.left) - self._visit(node.right)
        elif node.op.type == MUL:
            return self._visit(node.left) * self._visit(node.right)
        elif node.op.type == DIV:
            return self._visit(node.left) / self._visit(node.right)
        else:
            raise Exception('Unknown Bin op type: {}'.format(node.op.type))

    def _visit_ForTo(self, node):
        currentvalue = self._visit(node.start)
        stepvalue = self._visit(node.step)
        endvalue = self._visit(node.end)

        self._assign(currentvalue, node.var)

        triggered = False
        while not triggered:
            triggered = endvalue == self._retrieve(node.var)

            for statement in node.children:
                self._visit(statement)

            self._assign(self._retrieve(node.var) + stepvalue, node.var)

