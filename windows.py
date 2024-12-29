import curses
import files
import math

#-----------------------------------------------------------------------
class TextArt:

    index = 0
    offset = 1000

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

    WDNA_X = 10
    WDNA_Y = curses.LINES
    DNA_STRING_Y = curses.LINES - 3 # height of  w_strand string

    w_dna = curses.newwin(WDNA_Y, WDNA_X, 1, 40)
    w_dna.addstr(dna.fill(DNA_STRING_Y))
    w_dna.noutrefresh()


    if dna.index >= 10_000_000:
        dna_min = str(round(dna.index / 10_000_000))\
                  + "mpb"
    elif dna.index < 10_000:
        dna_min = '{:,}'.format(dna.index) + "bp"
    else:
        dna_min = '{:,}'.format(round((dna.index / 1_000)))\
                  + "kpb"
    if (dna.index + dna.offset) >= 10_000_000:
        dna_max = str(round((dna.index + dna.offset) / 1_000_000))\
                  + "mpb"
    elif (dna.index + dna.offset) < 10_000:
        dna_max = '{:,}'.format((dna.index + dna.offset)) + "bp"
    else:
        dna_max = '{:,}'.format(round((dna.index + dna.offset) / 1_000))\
                  + "kpb"


    # width 9 for max formatted text of: '99,999kbp'
    DNA_RULER_X = 9

    w_dna_ruler = curses.newwin(WDNA_Y, DNA_RULER_X, 1, 40 - DNA_RULER_X)
    w_dna_ruler.addstr('{:>8}'.format(dna_min) + "\n"\
                      +"       │\n" * (DNA_STRING_Y - 2)\
                      +'{:>8}'.format(dna_max))
    w_dna_ruler.noutrefresh()

#-----------------------------------------------------------------------

def load_strand(strand = _strand):

    WSTRAND_X = 30
    WSTRAND_Y = curses.LINES - 1 # so border isn't cut off by cmd line
    STRAND_STRING_Y = WSTRAND_Y - 1 # for borders


    w_strand = curses.newwin(WSTRAND_Y, WSTRAND_X, 0, 0)
    w_strand.addstr(strand.fill(STRAND_STRING_Y))
    w_strand.border()


    WSTRAND_RULER_Y = WSTRAND_Y - 2 # for borders
    WSTRAND_RULER_X = WSTRAND_X - (2 + strand.x) # borders + strand string

    w_strand_ruler = curses.newwin(WSTRAND_RULER_Y, WSTRAND_RULER_X, 1, strand.x+1)
    w_strand_ruler.addstr("┬0bp\n"\
                     + "│\n" * (WSTRAND_RULER_Y - 2)\
                     + "┴" + '{:,}'.format(files.sequence_length) + "bp")

    strand.index = math.floor((dna.index / files.sequence_length) * STRAND_STRING_Y)
    # FIXME
    # I think index starts at 0, but STRAND_STRING_Y starts at 1
    if strand.index == STRAND_STRING_Y - 1:
        strand.index -= 1 #dont hit that border, now!
    strand.offset = math.floor((dna.offset / files.sequence_length) * STRAND_STRING_Y)
    # FIXME
    # but not for offset I don't think
    if strand.offset == STRAND_STRING_Y:
        strand.offset -= 1

    w_strand.chgat(strand.index+1, 1, (WSTRAND_X - 2), curses.A_BLINK)
    for lines in range(strand.offset):
        w_strand.chgat(strand.index+1+lines, 1, (WSTRAND_X - 2), curses.A_BLINK)

    w_strand_ruler.chgat(strand.index, 0, (WSTRAND_X - 2), curses.A_REVERSE)
    for lines in range(strand.offset):
        w_strand_ruler.chgat(strand.index+lines, 0, (WSTRAND_X - 2), curses.A_REVERSE)

    w_strand.noutrefresh()
    w_strand_ruler.noutrefresh()

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

