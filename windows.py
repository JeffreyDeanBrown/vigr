import curses

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

    def update_text(self, new_text, file_name = False):
        self.__init__(text = new_text, file_name = file_name)


_strand = TextArt("text_art.txt", file_name = True)
dna = TextArt("├┄┤\n")


def load_dna():
    w_dna = curses.newwin(curses.LINES, 10, 1, 40)
    w_dna.addstr(dna.fill(curses.LINES-3))
    w_dna.noutrefresh()


def load_strand(strand = _strand):
    w_strand = curses.newwin(curses.LINES-1, 30, 0, 0)
    w_strand.addstr(strand.fill(curses.LINES-2))
    w_strand.border()
    w_strand.noutrefresh()


def load_cmd(input = None, refresh_only = False):
    w_cmd = curses.newwin(1, curses.COLS, curses.LINES-1, 0)
    if (input == None) & (not refresh_only):
        w_cmd.addstr(" " * (curses.COLS-1))
    elif refresh_only:
        pass
    else:
        w_cmd.addstr(input)
    w_cmd.noutrefresh()

