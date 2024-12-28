import curses

stdscr = curses.initscr()
# curses.noecho()
curses.cbreak() # instantly react to keys
stdscr.refresh()

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
# p_strand = curses.newpad(strand.y, strand.x)
# p_strand.addstr(strand.text)
# p_strand.refresh(0,0,0,0,curses.LINES-1, strand.x)

w_strand = curses.newwin(curses.LINES-2, 30, 0, 0)
w_strand.addstr(strand.fill(curses.LINES-3))
w_strand.border()
w_strand.noutrefresh()

def load_dna(dna):
    w_dna = curses.newwin(curses.LINES-2, 10, 1, 40)
    w_dna.addstr(dna.fill(curses.LINES-4))
    w_dna.noutrefresh()

load_dna(dna)

def load_cmd(input = None):
    w_cmd = curses.newwin(1, curses.COLS-1, curses.LINES-2, 0)
    if input == None:
        w_cmd.addstr(" " * (curses.COLS-2))
    else:
        w_cmd.addstr(input)
    w_cmd.noutrefresh()

load_cmd()

while True:
    curses.doupdate()
    curses.curs_set(0)
    curses.noecho()
    act = stdscr.getkey(curses.LINES-1,0)
    if act == ":":
        load_cmd()
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
