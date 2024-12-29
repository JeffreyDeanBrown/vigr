import curses
import files

#-----------------------------------------------------------------------

class TextArt:

    buffer = 0
    scale = 1000

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

#-----------------------------------------------------------------------

def load_dna():
    w_dna = curses.newwin(curses.LINES, 10, 1, 40)
    w_dna.addstr(dna.fill(curses.LINES-3))
    w_dna.noutrefresh()

    w_dna_ruler = curses.newwin(curses.LINES, 9, 1, 31)

    if dna.buffer >= 10_000_000:
        dna_min = str(round(dna.buffer / 10_000_000))\
                  + "mpb"
    elif dna.buffer < 10_000:
        dna_min = '{:,}'.format(dna.buffer) + "bp"
    else:
        dna_min = '{:,}'.format(round((dna.buffer / 1_000)))\
                  + "kpb"

    if (dna.buffer + dna.scale) >= 10_000_000:
        dna_max = str(round((dna.buffer + dna.scale) / 1_000_000))\
                  + "mpb"
    elif (dna.buffer + dna.scale) < 10_000:
        dna_max = '{:,}'.format((dna.buffer + dna.scale)) + "bp"
    else:
        dna_max = '{:,}'.format(round((dna.buffer + dna.scale) / 1_000))\
                  + "kpb"

    w_dna_ruler.addstr('{:>8}'.format(dna_min) + "\n"\
                      +"       │\n" * (curses.LINES-5)\
                      +'{:>8}'.format(dna_max))
    w_dna_ruler.noutrefresh()

#-----------------------------------------------------------------------

def load_strand(strand = _strand):
    w_strand = curses.newwin(curses.LINES-1, 30, 0, 0)
    w_strand.addstr(strand.fill(curses.LINES-2))
    w_strand.border()
    w_strand.noutrefresh()

    w_file_size = curses.newwin(curses.LINES-3, 28-strand.x, 1, strand.x+1)
    w_file_size.addstr("┬0bp\n"\
                     + "│\n" * (curses.LINES-5)\
                     + "┴" + '{:,}'.format(files.sequence_length) + "bp")
    w_file_size.noutrefresh()

#-----------------------------------------------------------------------

def load_cmd(input = None, refresh_only = False):
    w_cmd = curses.newwin(1, curses.COLS, curses.LINES-1, 0)
    if (input == None) & (not refresh_only):
        w_cmd.addstr(" " * (curses.COLS-1))
    elif refresh_only:
        pass
    else:
        w_cmd.addstr(input)
    w_cmd.noutrefresh()

