import math

import curses
from curses import wrapper, ascii

import words_lib

TERM_MIN_HEIGHT = 11
TERM_MIN_WIDTH = 31

COLOR_MAIN_BG = 1
COLOR_MAIN_TEXT = 2
COLOR_WND_BG = 3
COLOR_WND_TEXT = 4
COLOR_WND_FRAME_BG = 5
COLOR_WND_FRAME_TEXT = 6
COLOR_FIELD_BG = 7
COLOR_FIELD_TEXT = 8
COLOR_BTN_BG = 9
COLOR_BTN_TEXT = 10
COLOR_BTN_EXIT_BG = 11
COLOR_BTN_EXIT_TEXT = 12

COLOR_PAIR_MAIN = 1
COLOR_PAIR_WND = 2
COLOR_PAIR_WND_FRAME = 3
COLOR_PAIR_FIELD = 4
COLOR_PAIR_BTN = 5
COLOR_PAIR_BTN_EXIT = 6

ACTION_NONE = 0
ACTION_SEARCH_WORDS = 1
ACTION_EXIT = 2

# id, [R, G, B] in 0 .. 1000, fallback_default_color
term_colors = [
    (COLOR_MAIN_BG, [500, 500, 500]), 
    (COLOR_MAIN_TEXT, [0, 0, 0]), 
    (COLOR_WND_BG, [0, 0, 500]), 
    (COLOR_WND_TEXT, [0, 1000, 1000]), 
    (COLOR_WND_FRAME_BG, [0, 0, 500]), 
    (COLOR_WND_FRAME_TEXT, [1000, 1000, 0]), 
    (COLOR_FIELD_BG, [0, 0, 500]), 
    (COLOR_FIELD_TEXT, [0, 1000, 1000]), 
    (COLOR_BTN_BG, [0, 0, 500]), 
    (COLOR_BTN_TEXT, [1000, 1000, 0]), 
    (COLOR_BTN_EXIT_BG, [500, 0, 0]), 
    (COLOR_BTN_EXIT_TEXT, [0, 0, 0]), 
]

# id, [FG_color_id, BG_color_id], [fallback_FG, fallback_BG]
term_color_pairs = [
    (COLOR_PAIR_MAIN, [COLOR_MAIN_TEXT, COLOR_MAIN_BG], 
                      [curses.COLOR_BLACK, curses.COLOR_WHITE]), 
    (COLOR_PAIR_WND, [COLOR_WND_TEXT, COLOR_WND_BG], 
                     [curses.COLOR_CYAN, curses.COLOR_BLUE]), 
    (COLOR_PAIR_WND_FRAME, [COLOR_WND_FRAME_TEXT, COLOR_WND_FRAME_BG], 
                           [curses.COLOR_YELLOW, curses.COLOR_BLUE]), 
    (COLOR_PAIR_FIELD, [COLOR_FIELD_TEXT, COLOR_FIELD_BG], 
                       [curses.COLOR_CYAN, curses.COLOR_BLUE]), 
    (COLOR_PAIR_BTN, [COLOR_BTN_TEXT, COLOR_BTN_BG], 
                     [curses.COLOR_YELLOW, curses.COLOR_BLUE]), 
    (COLOR_PAIR_BTN_EXIT, [COLOR_BTN_EXIT_TEXT, COLOR_BTN_EXIT_BG], 
                          [curses.COLOR_BLACK, curses.COLOR_RED]), 
]

def clamp(x, low, high):
    if (x < low):
        x = low
    elif (x > high):
        x = high
    return x

# addch_last and addstr_last were created
# because ncurses doesn't like writing last char of the window
# but now checking if the char is within window is up to programmer
def addch_last(wnd, *args):
    try:
        wnd.addch(*args)
    except curses.error:
        pass

def addstr_last(wnd, *args):
    try:
        wnd.addstr(*args)
    except curses.error:
        pass

def fill_area(wnd, y0, x0, y1, x1, char, *args):
    wnd_h, wnd_w = wnd.getmaxyx()
    y0 = clamp(y0, 0, wnd_h - 1)
    x0 = clamp(x0, 0, wnd_w - 1)
    y1 = clamp(y1, 0, wnd_h - 1)
    x1 = clamp(x1, 0, wnd_w - 1)
    fill_str = "".join([char for i in range(x1 + 1 - x0)])
    for y in range(y0, y1 + 1):
        if (len(args) > 0):
            addstr_last(wnd, y, x0, fill_str, args[0])
        else:
            addstr_last(wnd, y, x0, fill_str)

# simple "abstract class" for interface objects
class InterfaceObject:
    def __init__(self):
        pass
    def select(self):
        raise NotImplementedError()
    def key_input(self):
        raise NotImplementedError()
    def draw(self):
        raise NotImplementedError()

class Button(InterfaceObject):
    def __init__(self, wnd, line, col, width, text, style, action_id):
        self._wnd_obj = wnd.derwin(1, width, line, col)
        self._wnd_obj.bkgd(" ", curses.color_pair(style))
        self._width = width
        if (len(text) > width - 2):
            text = text[0 : (width - 2)]
        self._text = text
        self._h_offset = (width - len(text)) / 2
        if (self._h_offset < 0):
            self._h_offset = 0
        else:
            self._h_offset = math.floor(self._h_offset)
        self._action_id = action_id
        self._is_selected = False
    def select(self, val):
        self._is_selected = val
    def key_input(self, key):
        if (((key[0] == chr(curses.ascii.CR)) or (key[0] == chr(curses.ascii.LF)) or 
            (key[0] == " ")) and (self._is_selected)):
            return self._action_id
        else:
            return ACTION_NONE
    def draw(self):
        border = "  "
        if (self._is_selected):
            border = "[]"
        addstr_last(self._wnd_obj, 0, 0, border[0])
        addstr_last(self._wnd_obj, 0, self._width - 1, border[1])
        addstr_last(self._wnd_obj, 0, self._h_offset, self._text)
        self._wnd_obj.refresh()

class InputField(InterfaceObject):
    def __init__(self, wnd, line, col, width, style, is_masked):
        self._wnd_obj = wnd.derwin(1, width, line, col)
        self._wnd_obj.bkgd(" ", curses.color_pair(style))
        self._width = width
        self._is_masked = is_masked
        self._text = ""
        self._is_selected = False
    def select(self, val):
        self._is_selected = val
    def key_input(self, key):
        if (self._is_selected):
            if (key[0] and (key[0].isalpha() or ((self._is_masked) and (key[0] == "*")))):
                self._text = "".join([self._text, key[0].lower()])
            if (key[1] == curses.KEY_BACKSPACE):
                self._text = self._text[0 : -1]
        return ACTION_NONE
    def draw(self):
        text_to_display = self._text
        if (len(text_to_display) > self._width - 1):
            text_to_display = text_to_display[-(self._width - 1):]
        add_char = " "
        if (self._is_selected):
            add_char = "_"
        text_to_display = "".join([text_to_display, add_char])
        fill_area(self._wnd_obj, 0, 0, 0, self._width - 1, " ")
        addstr_last(self._wnd_obj, 0, 0, text_to_display)
        self._wnd_obj.refresh()
    def get_data(self):
        return self._text

class OutputField(InterfaceObject):
    def __init__(self, wnd, line, col, height, width, style_out, style_in):
        self._frame = wnd.derwin(height, width, line, col)
        self._frame.bkgd(" ", curses.color_pair(style_out))
        self._line = line
        self._inner_line = line + 1
        self._col = col
        self._inner_col = col + 1
        self._height = height
        self._inner_height = height - 2
        self._width = width
        self._inner_width = width - 2
        self._style_out = style_out
        self._style_in = style_in
        self._title = ""
        self._is_selected = False
        # sets _line_shift, _word_list, _word_num, _word_len, 
        # _words_per_line, _n_lines, _pad
        self.set_word_list([])
    def select(self, val):
        self._is_selected = val
    def key_input(self, key):
        if (self._n_lines > self._inner_height):
            step = 0
            if (key[1] == curses.KEY_DOWN):
                step = 1
            if (key[1] == curses.KEY_UP):
                step = -1
            self._line_shift += step
            if (self._line_shift < 0):
                self._line_shift = 0
            line_shift_high_lim = self._n_lines - self._inner_height
            if (self._line_shift > line_shift_high_lim):
                self._line_shift = line_shift_high_lim
        return ACTION_NONE
    def draw(self):
        self._frame.border()
        out_title = self._title
        if (len(out_title) > self._inner_width - 2):
            out_title = out_title[0 : (self._inner_width - 2)]
        self._frame.addstr(0, 1, out_title)
        if (self._n_lines > self._inner_height):
            addch_last(self._frame, 0, self._width - 1, curses.ACS_UARROW)
            addch_last(self._frame, self._height - 1, self._width - 1, curses.ACS_DARROW)
        fill_area(self._frame, 1, 1, self._inner_height, self._inner_width, " ")
        self._frame.refresh()
        if (self._n_lines <= 0):
            return
        if (not self._pad):
            self._pad = curses.newpad(self._n_lines, self._inner_width)
        self._pad.bkgd(" ", curses.color_pair(self._style_in))
        for line_idx in range(self._n_lines):
            first_word_idx = line_idx * self._words_per_line
            last_word_idx = first_word_idx + self._words_per_line - 1
            if (last_word_idx >= self._word_num):
                last_word_idx = self._word_num - 1
            cur_str = " ".join(self._word_list[first_word_idx : (last_word_idx + 1)])
            addstr_last(self._pad, line_idx, 0, cur_str)
        self._pad.refresh(self._line_shift, 0, self._inner_line, self._inner_col, 
                          self._inner_line + self._inner_height - 1, 
                          self._inner_col + self._inner_width - 1)
    def set_word_list(self, word_list):
        self._line_shift = 0
        self._word_list = word_list
        self._word_num = len(self._word_list)
        if (self._word_num > 0):
            self._word_len = len(word_list[0])
            self._words_per_line = 1 + math.floor((self._inner_width - self._word_len) / 
                                                  (self._word_len + 1))
            if (self._words_per_line > 0):
                self._n_lines = math.ceil(self._word_num / self._words_per_line)
            else:
                self._n_lines = -1
        else:
            self._word_len = -1
            self._words_per_line = -1
            self._n_lines = -1
        self._pad = None
    def set_title(self, title):
        self._title = title

def main(stdscr):
    stdscr.clear()

    ws = words_lib.WordSearcher()
    ws.load_words('wordlist.txt')

    scr_width = curses.COLS
    scr_height = curses.LINES

    if ((scr_width < TERM_MIN_WIDTH) or (scr_height < TERM_MIN_HEIGHT)):
        curses.endwin()
        print("Terminal size too small!")
        input("Press Enter to exit.")
        return
    
    if (not curses.has_colors()):
        curses.endwin()
        print("Color support required!")
        input("Press Enter to exit.")
        return
    elif ((not curses.can_change_color()) or 
          (curses.COLORS < 16) or (curses.COLOR_PAIRS < 16)):
        for color_pair_def in term_color_pairs:
            curses.init_pair(color_pair_def[0], *color_pair_def[2])
    else:
        for color_def in term_colors:
            curses.init_color(color_def[0], *color_def[1])
        for color_pair_def in term_color_pairs:
            curses.init_pair(color_pair_def[0], *color_pair_def[1])
    
    curses.curs_set(0)

    stdscr.bkgd(" ", curses.color_pair(COLOR_PAIR_MAIN))
    stdscr.addstr(1, 1, "Letters")
    stdscr.addstr(3, 1, "Mask")
    
    letters_in = InputField(stdscr, 1, 16, 12, COLOR_PAIR_FIELD, False)
    mask_in = InputField(stdscr, 3, 16, 12, COLOR_PAIR_FIELD, True)

    words_out = OutputField(stdscr, 5, 1, scr_height - 8, scr_width - 2, 
                            COLOR_PAIR_WND_FRAME, COLOR_PAIR_WND)
    words_out.set_title("Found words (0)")
    
    search_btn = Button(stdscr, scr_height - 2, 1, 14, "Search", 
                        COLOR_PAIR_BTN, ACTION_SEARCH_WORDS)
    exit_btn = Button(stdscr, scr_height - 2, scr_width - 15, 14, "Exit", 
                      COLOR_PAIR_BTN_EXIT, ACTION_EXIT)

    interface_objects = [letters_in, mask_in, words_out, search_btn, exit_btn]
    selectable_objects = [letters_in, mask_in, search_btn, exit_btn]
    sel_idx = 0
    for idx, obj in enumerate(selectable_objects):
        obj.select(idx == sel_idx)
    
    while True:
        for obj in interface_objects:
            obj.draw()
        stdscr.refresh()

        wch = stdscr.get_wch()
        match wch:
            case int(val): # backspace
                ch = (None, val)
            case str(val): # alpha, tab, enter
                ch = (val, None)
            case _:
                ch = (None, None)
        if (ch[0] == chr(curses.ascii.TAB)):
            sel_idx = (sel_idx + 1) % len(selectable_objects)
            for idx, obj in enumerate(selectable_objects):
                obj.select(idx == sel_idx)
        elif (ch[1] == curses.KEY_RESIZE):
            curses.endwin()
            print("Do not resize terminal!")
            input("Press Enter to exit.")
            return
        else:
            cur_action = ACTION_NONE
            for obj in interface_objects:
                new_action = obj.key_input(ch)
                cur_action = max(cur_action, new_action)
            if (cur_action == ACTION_SEARCH_WORDS):
                letters = letters_in.get_data()
                mask = mask_in.get_data()
                res_words = ws.gen_matching_words(letters, mask)
                words_out.set_title("Found words ({0})".format(len(res_words)))
                words_out.set_word_list(res_words)
            if (cur_action == ACTION_EXIT):
                break

wrapper(main)
