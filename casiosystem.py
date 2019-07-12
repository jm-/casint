import time

from common import *
from graphics import setpixel, text, locate, fill


NUM_TEXT_ROWS = 6


class ProgramMenu(object):
    def __init__(self, casio, programs):
        self.casio = casio
        self.programs = programs
        self.selection = 0
        self.offset = 0

    def paint(self):
        # todo: use a new 'program' texture, not the graph texture
        self.casio._render_begin(self.casio.texture_graph)
        self.casio._clear_screen()
        locate(self.casio.renderer, self.casio.font_text, 1, 1, b"Program List")
        # write program names
        i = 0
        while i < NUM_TEXT_ROWS and (i+self.offset) < len(self.programs):
            program = self.programs[i+self.offset]
            if (self.selection-self.offset) == i:
                # print the marker in inverted text
                self.casio._set_color(True)
                fill(self.casio.renderer, 1, i * 8 + 8, 127, i * 8 + 16)
                locate(self.casio.renderer, self.casio.font_text_inverted, 2, i+2, program.name)
            else:
                locate(self.casio.renderer, self.casio.font_text, 2, i+2, program.name)
            i += 1
        self.casio._render_end()
    
    def show(self):
        self.selection = 0
        self.offset = 0

        while True:
            self.paint()
            casio_key = self.casio._getkey()
            if casio_key == 31:
                # enter
                break
            elif casio_key == 28:
                # up
                self.selection -= 1
                if self.selection == -1:
                    self.selection = len(self.programs) - 1
                    self.offset = max(0, len(self.programs) - NUM_TEXT_ROWS)
                elif (self.selection-self.offset) < 0:
                    self.offset -= 1
            elif casio_key == 37:
                # down
                self.selection += 1
                if self.selection == len(self.programs):
                    self.selection = 0
                    self.offset = 0
                elif (self.selection-self.offset) >= NUM_TEXT_ROWS:
                    self.offset += 1
        
        self.casio._render_begin(self.casio.texture_graph)
        self.casio._clear_screen()
        self.casio._render_end()

        return self.selection
