import curses

"""
TODO:   -move main loop to function, call with wrapper()
        -add window resize keystroke
        -implement a list of keystrokes and :* functions
        -implement filesize, sequence sizing, and scrolling
        -*organize*
"""

stdscr = curses.initscr()
# curses.noecho()
curses.cbreak() # instantly react to keys


curses.curs_set(0)
class TextArt:
    def __init__(self, text, file_name = False):
        if file_name:
            with open(text) as file_:
                self.lines = list(file_)
        else:
            self.lines = text.splitlines(keepends=True)
        self.text = ''.join(self.lines)
        self.y = len(self.lines)
        self.x = len(max(self.lines))

    def fill(self, max_y):
        expanded_lines = self.lines * (max_y // self.y + 1)
        return(''.join(expanded_lines[:max_y]))


strand = TextArt("text_art.txt", file_name = True)
dna = TextArt("├┄┤\n")


def load_dna(dna):
    w_dna = curses.newwin(curses.LINES, 10, 1, 40)
    w_dna.addstr(dna.fill(curses.LINES-4))
    w_dna.noutrefresh()


def load_strand(strand):
    w_strand = curses.newwin(curses.LINES-2, 30, 0, 0)
    w_strand.addstr(strand.fill(curses.LINES-3))
    w_strand.border()
    w_strand.noutrefresh()


def load_cmd(input = None):
    w_cmd = curses.newwin(1, curses.COLS, curses.LINES, 0)
    buffer_ = " " * (curses.COLS - 1)
    if (input == None):
        w_cmd.addstr(buffer_)
    else:
        buffer_ = input
        load_cmd()
    w_cmd.noutrefresh()


def load_screen():
    stdscr.refresh()
    load_strand(strand)
    load_dna(dna)
    load_cmd()

while True:

    curses.update_lines_cols()
    load_screen()
    curses.curs_set(0)
    curses.noecho()

    act = stdscr.getch(curses.LINES-1,0)
    if act == ord(":"):
        load_cmd(":")
        curses.curs_set(1)
        curses.echo()
        cmd = stdscr.getstr(curses.LINES-2, 1).decode('utf-8')
        if cmd == 'l':
            dna = TextArt("║\n")
            load_dna(dna)
        elif cmd == 's':
            dna = TextArt("││\n")
            load_dna(dna)
        elif cmd == 'm':
            dna = TextArt("├┄┤\n")
            load_dna(dna)
        elif cmd == 'b':
            dna = TextArt("┣┅┅┅┫\n"\
                          "┃   ┃\n")
            load_dna(dna)
        elif cmd == 'q':
            curses.nocbreak()
            stdscr.keypad(False)
            curses.echo()
            curses.endwin()
            break


# cmd_line = curses.newwin(1, curses.COLS-1, curses.LINES-1, 0)

# Terminate curses window
# curses.nocbreak()
# stdscr.keypad(False)
# curses.echo()
# curses.endwin()
