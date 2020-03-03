import time

from .common import *
from .machine import CasioMachine
from .loader import CasioProgram, CasioPict
from .graphics import locate, fill


NUM_TEXT_ROWS = 6


class CasioSystem(CasioMachine):
    def __init__(self, items):
        super().__init__(items)


    def _paint_menu(self, selection, offset):
        # todo: use a new 'program' texture, not the graph texture
        self._render_begin(self.texture_graph)
        self._clear_screen()
        locate(self.renderer, self.font_text, 1, 1, b"Program List")
        # write program names
        i = 0
        while i < NUM_TEXT_ROWS and (i+offset) < self.items.program_count:
            program = self.items.get_program_by_index(i+offset)
            if (selection-offset) == i:
                # print the marker in inverted text
                self._set_color(True)
                fill(self.renderer, 1, i * 8 + 8, 127, i * 8 + 16)
                locate(self.renderer, self.font_text_inverted, 2, i+2, program.name)
            else:
                locate(self.renderer, self.font_text, 2, i+2, program.name)
            i += 1
        self._render_end()


    def show_menu(self):
        selection = 0
        offset = 0

        while True:
            self._paint_menu(selection, offset)
            casio_key = self._getkey()
            if casio_key == 31:
                # enter
                break
            elif casio_key == 28:
                # up
                selection -= 1
                if selection == -1:
                    selection = self.items.program_count - 1
                    offset = max(0, self.items.program_count - NUM_TEXT_ROWS)
                elif (selection-offset) < 0:
                    offset -= 1
            elif casio_key == 37:
                # down
                selection += 1
                if selection == self.items.program_count:
                    selection = 0
                    offset = 0
                elif (selection-offset) >= NUM_TEXT_ROWS:
                    offset += 1

        self._render_begin(self.texture_graph)
        self._clear_screen()
        self._render_end()

        program = self.items.get_program_by_index(selection)
        return program
