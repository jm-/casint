import ctypes
from random import random as rand_num

import sdl2

from common import *
from interpreter import Var, VariableRange, MemoryIndex, Label
from graphics import setpixel, pxltest, fline, text

SDL_DELAY_MILLIS = 25


class SubroutineReturnException(Exception):
    pass


class ControlLoopBreakException(Exception):
    pass


class ProgramStopException(Exception):
    pass


class GotoException(Exception):
    def __init__(self, node):
        super(GotoException, self).__init__()
        self.node = node


class NodeVisitor(object):
    def _visit(self, node):
        method_name = '_visit_' + type(node).__name__
        #print 'DBG: invoking %s' % (method_name,)
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        raise Exception('No _visit_{} method'.format(type(node).__name__))


class CasioInterpreter(NodeVisitor):
    def __init__(self, programs):
        self.running = True
        self.key = None

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

        # init with a clear screen
        self._render_begin()
        self._clear_screen()
        self._render_end()

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

    def _set_color(self, is_on):
        if is_on:
            sdl2.SDL_SetRenderDrawColor(self.renderer, 0x10, 0x10, 0x10, sdl2.SDL_ALPHA_OPAQUE)
        else:
            sdl2.SDL_SetRenderDrawColor(self.renderer, 0xe8, 0xe8, 0xee, sdl2.SDL_ALPHA_OPAQUE)

    def _clear_screen(self):
        self._set_color(False)
        sdl2.SDL_RenderClear(self.renderer)

    def _refresh_screen(self):
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, None)
        sdl2.SDL_RenderPresent(self.renderer)

    def _set_window_title(self, name):
        sdl2.SDL_SetWindowTitle(self.window, name + ' - CASINT: CASIO Basic Interpreter')

    def _handle_events(self, delay=False):
        self._refresh_screen()
        event = sdl2.SDL_Event()
        setkey = False
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                self.running = False
                return
            elif event.type == sdl2.SDL_KEYDOWN:
                self.key = event.key.keysym.sym
                setkey = True

        if not setkey:
            self.key = None

        if delay:
            sdl2.SDL_Delay(SDL_DELAY_MILLIS)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sdl2.SDL_DestroyTexture(self.texture)
        # clean up stored pics
        for pic in self.pics.values():
            sdl2.SDL_DestroyTexture(pic)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_Quit()

    def run(self, name):
        self.running = True
        program = self.programs.get(name)
        self._set_window_title(name)
        try:
            self._visit(program.tree)
        except ProgramStopException:
            pass

    def idle(self):
        while self.running:
            self._handle_events(delay=True)

    # =========================================================================
    # Node processing starts here!
    # =========================================================================

    def _run_prog(self, name):
        program = self.programs.get(name)
        #print 'DBG: entering subroutine: %r' % (name,)
        try:
            self._visit(program.tree)
        except SubroutineReturnException:
            pass
        #print 'DBG: returned from subroutine: %r' % (name,)

    def _save_pic(self, num):
        pic = sdl2.SDL_CreateTexture(
            self.renderer, sdl2.SDL_PIXELFORMAT_RGBA8888,
            sdl2.SDL_TEXTUREACCESS_TARGET, 128, 64)
        # render to new pic
        sdl2.SDL_SetRenderTarget(self.renderer, pic)
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, None)
        sdl2.SDL_SetRenderTarget(self.renderer, None)

        self.pics[num] = pic

    def _load_pic(self, num):
        pic = self.pics[num]
        # render to existing texture
        self._render_begin()
        sdl2.SDL_RenderCopy(self.renderer, pic, None, None)
        self._render_end()

    def _assign(self, value, node):
        if type(node) is Var:
            self.vars[node.value] = value

        elif type(node) is VariableRange:
            l = ord(node.lower.value)
            u = ord(node.upper.value)
            while l <= u:
                self.vars[chr(l)] = value
                l += 1

        elif type(node) is MemoryIndex:
            if node.left.op.type == MAT:
                x = self._visit(node.right[0])
                y = self._visit(node.right[1])
                self.mats[node.left.value][x-1][y-1] = value
            else:
                raise Exception('Unknown memory index assignment: {}'.format(node.left.op.type))

        else:
            raise Exception('Unknown variable assignment node: {}'.format(type(node).__name__))

    def _retrieve(self, node):
        if type(node) is Var:
            return self.vars[node.value]

        elif type(node) is MemoryIndex:
            if node.left.op.type == MAT:
                x = self._visit(node.right[0])
                y = self._visit(node.right[1])
                return self.mats[node.left.value][x-1][y-1]
            else:
                raise Exception('Unknown memory index retrieval: {}'.format(node.left.op.type))

        else:
            raise Exception('Unknown variable retrieval node: {}'.format(type(node).__name__))

    def _eval_bool(self, node):
        value = self._visit(node)
        return bool(value)

    def _getkey(self):
        self._handle_events(delay=True)
        return SDL_CASIO_KEYMAP.get(self.key, DEFAULT_CASIO_GETKEY)

    def _run_statements(self, statements):
        goto = None
        while True:
            try:
                for statement in statements:
                    if goto:
                        if type(statement) is Label and goto.op.value == statement.op.value:
                            goto = None
                        else:
                            continue
                    self._visit(statement)
                break
            except GotoException as e:
                goto = e.node
        if goto:
            # didn't find it, pass it on
            raise GotoException(goto)

    def _visit_NoOp(self, node):
        pass

    def _visit_Program(self, node):
        #for statement in node.children:
        #    self._visit(statement)
        self._run_statements(node.children)

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
            self._handle_events(delay=True)
        else:
            raise Exception('Unknown QuaternaryBuiltin op type: {}'.format(node.op.type))

    def _visit_TernaryBuiltin(self, node):
        if node.op.type == TEXT:
            y = self._visit(node.arg1)
            x = self._visit(node.arg2)
            s = self._visit(node.arg3)
            if type(s) is not str:
                s = str(s)
            self._render_begin()
            #print 'text:', repr(s)
            text(self.renderer, self.texture_font, x, y, s)
            self._render_end()
            self._handle_events(delay=True)
        else:
            raise Exception('Unknown TernaryBuiltin op type: {}'.format(node.op.type))

    def _visit_BinaryBuiltin(self, node):
        if node.op.type == PXLON:
            y = self._visit(node.arg1)
            x = self._visit(node.arg2)
            self._render_begin()
            self._set_color(True)
            setpixel(self.renderer, x, y)
            self._render_end()
            self._handle_events(delay=True)
        elif node.op.type == PXLOFF:
            y = self._visit(node.arg1)
            x = self._visit(node.arg2)
            self._render_begin()
            self._set_color(False)
            setpixel(self.renderer, x, y)
            self._render_end()
            self._handle_events(delay=True)
        else:
            raise Exception('Unknown BinaryBuiltin op type: {}'.format(node.op.type))

    def _visit_BinaryFunc(self, node):
        if node.op.type == PXLTEST:
            y = self._visit(node.arg1)
            x = self._visit(node.arg2)
            self._render_begin()
            is_lit = pxltest(self.renderer, x, y)
            self._render_end()
            return 1 if is_lit else 0
        else:
            raise Exception('Unknown BinaryFunc op type: {}'.format(node.op.type))

    def _visit_UnaryBuiltin(self, node):
        if node.op.type == HORIZONTAL:
            y = self._visit(node.arg1)
            self._render_begin()
            self._set_color(True)
            fline(self.renderer, 1, y, 127, y)
            self._render_end()
        elif node.op.type == PROG:
            name = self._visit(node.arg1)
            self._run_prog(name)
        elif node.op.type == STOPICT:
            num = self._visit(node.arg1)
            self._save_pic(num)
        elif node.op.type == RCLPICT:
            num = self._visit(node.arg1)
            self._load_pic(num)
        elif node.op.type == ISZ:
            # NB: this is an incomplete impl!
            self._assign(self._retrieve(node.arg1) + 1, node.arg1)
        elif node.op.type == DSZ:
            # NB: this is an incomplete impl!
            self._assign(self._retrieve(node.arg1) - 1, node.arg1)
        else:
            raise Exception('Unknown UnaryBuiltin op type: {}'.format(node.op.type))

    def _visit_UnaryFunc(self, node):
        if node.op.type == INTG:
            value = self._visit(node.arg1)
            return int(value)
        elif node.op.type == FRAC:
            value = self._visit(node.arg1)
            return value - int(value)
        else:
            raise Exception('Unknown UnaryFunc op type: {}'.format(node.op.type))

    def _visit_NullaryBuiltin(self, node):
        if node.op.type == CLS:
            self._render_begin()
            self._clear_screen()
            self._render_end()
        elif node.op.type == BREAK:
            raise ControlLoopBreakException()
        elif node.op.type == RETURN:
            raise SubroutineReturnException()
        elif node.op.type == STOP:
            raise ProgramStopException()
        else:
            raise Exception('Unknown NullaryBuiltin op type: {}'.format(node.op.type))

    def _visit_NullaryFunc(self, node):
        if node.op.type == GETKEY:
            return self._getkey()
        elif node.op.type == RANDNUM:
            return float(rand_num())
        else:
            raise Exception('Unknown NullaryFunc op type: {}'.format(node.op.type))

    def _visit_Num(self, node):
        return node.value

    def _visit_Var(self, node):
        return self._retrieve(node)

    def _visit_MemoryIndex(self, node):
        return self._retrieve(node)

    def _visit_StringLit(self, node):
        return node.value

    def _visit_Assign(self, node):
        value = self._visit(node.left)
        self._assign(value, node.right)

    def _visit_Initialize(self, node):
        x = self._visit(node.left[0])
        y = self._visit(node.left[1])
        if node.right.op.type == MAT:
            self.mats[node.right.value] = [[0 for j in xrange(y)] for i in xrange(x)]
        else:
            raise Exception('Unknown memory index initialization: {}'.format(node.right.op.type))

    def _visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self._visit(node.left) + self._visit(node.right)
        elif node.op.type == MINUS:
            return self._visit(node.left) - self._visit(node.right)
        elif node.op.type == MUL:
            return self._visit(node.left) * self._visit(node.right)
        elif node.op.type == DIV:
            return self._visit(node.left) / self._visit(node.right)
        elif node.op.type == EQ:
            l = self._visit(node.left)
            r = self._visit(node.right)
            return 1 if l == r else 0
        elif node.op.type == NEQ:
            l = self._visit(node.left)
            r = self._visit(node.right)
            return 1 if l != r else 0
        elif node.op.type == LT:
            l = self._visit(node.left)
            r = self._visit(node.right)
            return 1 if l < r else 0
        elif node.op.type == GT:
            l = self._visit(node.left)
            r = self._visit(node.right)
            return 1 if l > r else 0
        elif node.op.type == LTE:
            l = self._visit(node.left)
            r = self._visit(node.right)
            return 1 if l <= r else 0
        elif node.op.type == GTE:
            l = self._visit(node.left)
            r = self._visit(node.right)
            return 1 if l >= r else 0
        elif node.op.type == AND:
            l = self._visit(node.left)
            r = self._visit(node.right)
            b = bool(l) and bool(r)
            return 1 if b else 0
        elif node.op.type == OR:
            l = self._visit(node.left)
            r = self._visit(node.right)
            b = bool(l) or bool(r)
            return 1 if b else 0
        else:
            raise Exception('Unknown Bin op type: {}'.format(node.op.type))

    def _visit_UnaryOp(self, node):
        if node.op.type == MINUS:
            return -1 * self._visit(node.expr)
        else:
            raise Exception('Unknown Unary op type: {}'.format(node.op.type))

    def _visit_ForTo(self, node):
        currentvalue = self._visit(node.start)
        stepvalue = self._visit(node.step)
        endvalue = self._visit(node.end)

        check_fn = lambda x: x == endvalue

        if currentvalue < endvalue:
            if stepvalue <= 0:
                print 'WRN: ForTo loop is invalid! start=%s step=%s end=%s' % (
                    currentvalue, stepvalue, endvalue)
                check_fn = lambda x: False
            else:
                check_fn = lambda x: x <= endvalue

        elif currentvalue > endvalue:
            if stepvalue >= 0:
                print 'WRN: ForTo loop is invalid! start=%s step=%s end=%s' % (
                    currentvalue, stepvalue, endvalue)
                check_fn = lambda x: False
            else:
                check_fn = lambda x: x >= endvalue

        self._assign(currentvalue, node.var)
        alive = check_fn(currentvalue)
        while alive:
            try:
                self._run_statements(node.children)
            except ControlLoopBreakException:
                break

            newvalue = self._retrieve(node.var) + stepvalue
            alive = check_fn(newvalue)
            if alive:
                self._assign(newvalue, node.var)

    def _visit_IfThen(self, node):
        if self._eval_bool(node.condition):
            self._run_statements(node.if_clause)
        else:
            self._run_statements(node.else_clause)

    def _visit_DoLpWhile(self, node):
        c = True
        while c:
            try:
                self._run_statements(node.children)
            except ControlLoopBreakException:
                break

            c = self._eval_bool(node.condition)

    def _visit_WhileLoop(self, node):
        while self._eval_bool(node.condition):
            try:
                self._run_statements(node.children)
            except ControlLoopBreakException:
                break

    def _visit_Label(self, node):
        pass

    def _visit_Goto(self, node):
        raise GotoException(node)