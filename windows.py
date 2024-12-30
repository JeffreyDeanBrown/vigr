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
        expanded_lines[max_y - 1] = expanded_lines[max_y - 1].rstrip('\n')
        return(''.join(expanded_lines[:max_y]))


    def update_text(self, new_text, file_name = False):
        self.__init__(text = new_text, file_name = file_name)


_strand = TextArt("text_art.txt", file_name = True)
dna = TextArt("├┄┤\n")

#-----------------------------------------------------------------------

def load_dna():

    WDNA_X = 10
    WDNA_Y = curses.LINES - 1 # window offset down by 1 to line up w/border
    DNA_STRING_Y = WDNA_Y - 2 # inner diameter of w_string border



    #start window at y = 1 to line up with border
    w_dna = curses.newwin(WDNA_Y, WDNA_X, 1, 40)
    w_dna.addstr(dna.fill(DNA_STRING_Y))
    w_dna.noutrefresh()



    if dna.index >= 10_000_000:
        dna_ruler_min = str(round(dna.index / 10_000_000))\
                  + "mpb"
    elif dna.index < 10_000:
        dna_ruler_min = '{:,}'.format(dna.index) + "bp"
    else:
        dna_ruler_min = '{:,}'.format(round((dna.index / 1_000)))\
                  + "kpb"
    if (dna.index + dna.offset) >= 10_000_000:
        dna_ruler_max = str(round((dna.index + dna.offset) / 1_000_000))\
                  + "mpb"
    elif (dna.index + dna.offset) < 10_000:
        dna_ruler_max = '{:,}'.format((dna.index + dna.offset)) + "bp"
    else:
        dna_ruler_max = '{:,}'.format(round((dna.index + dna.offset) / 1_000))\
                  + "kpb"



    # width 9 for max formatted text of: '99,999kbp'
    DNA_RULER_X = 9
    #start window at y = 1 to line up with strand border
    w_dna_ruler = curses.newwin(WDNA_Y, DNA_RULER_X, 1, 40 - DNA_RULER_X)
    w_dna_ruler.addstr('{:>8}'.format(dna_ruler_min) + "\n"\
                      +"\n" * (DNA_STRING_Y - 2)\
                      +'{:>8}'.format(dna_ruler_max))
    w_dna_ruler.noutrefresh()

#-----------------------------------------------------------------------

def load_strand(strand = _strand):

    WSTRAND_X = 30
    WSTRAND_Y = curses.LINES - 1 # so border isn't cut off by cmd line
    WSTRAND_ID_Y = WSTRAND_Y - 2 # inner diameter of border



    # fills w_strand with strand TxtArt, but cuts off ends and adds border
    w_strand = curses.newwin(WSTRAND_Y, WSTRAND_X, 0, 0)
    w_strand.addstr(strand.fill(WSTRAND_Y))
    w_strand.border()



    WSTRAND_RULER_X = WSTRAND_X - (2 + strand.x) # borders + strand string

    if files.sequence_length >= 10_000_000:
        strand_ruler_max = str(round(files.sequence_length / 1_000_000))\
                  + "mpb"
    elif files.sequence_length < 10_000:
        strand_ruler_max = '{:,}'.format(files.sequence_length) + "bp"
    else:
        strand_ruler_max = '{:,}'.format(round(files.sequence_length / 1_000))\
                  + "kpb"

    # start at y = 1, x = strand.x + 1 to avoid borders
    w_strand_ruler = curses.newwin(WSTRAND_ID_Y, WSTRAND_RULER_X, 1, strand.x+1)
    w_strand_ruler.addstr("┬0bp\n"\
                     + "│\n" * (WSTRAND_ID_Y - 2)\
                     + "┴" + strand_ruler_max)

    #strand.index starts at 0, ends at WSTRAND_ID_Y
    strand.index = math.floor((dna.index/files.sequence_length) * WSTRAND_ID_Y)

    #strand.offset starts at 0, ends at WSTRAND_ID_Y - 1
    #figure out where to stop, and subtract index from that
    dna_endpoint = dna.index + dna.offset
    strand.offset = math.floor((dna_endpoint / files.sequence_length) * WSTRAND_ID_Y)\
                    - strand.index
    # the scale_dna and set_dna functions protect dna index/offset from going
    # above the file size, but nothing stops it from setting it to exactly the
    # file size-- which would set strand.offset = WSTRAND_ID_Y and cause
    # curses to error due to drawing outside of w_strand_ruler window
    if strand.index + strand.offset == WSTRAND_ID_Y:
        strand.offset -= 1



    #w_strand starts outside border, so start at y = 1, x = 1
    w_strand.chgat(1 + strand.index, 1, (WSTRAND_X - 2), curses.A_BLINK)
    for lines in range(1, strand.offset + 1):
        w_strand.chgat(1 + strand.index + lines, 1, (WSTRAND_X - 2), curses.A_BLINK)

    #w_strand_ruler starts inside border, so start at y = 0, x = 0
    w_strand_ruler.chgat(strand.index, 0, WSTRAND_RULER_X, curses.A_REVERSE)
    for lines in range(1, strand.offset + 1):
        w_strand_ruler.chgat(strand.index + lines, 0, WSTRAND_RULER_X, curses.A_REVERSE)



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

