import curses
import files
import math
import textart

#-----------------------------------------------------------------------


# (diagram not to scale)
# (w_strand has a border, which takes up 2 columns)
#
# <------------WSTRAND_W--------------><--WDNA_RULER_W--><--WDNA_W-->
# │<--------(WSTRAND_W - 2)---------->│
# │<--strand.w--><--WSTRAND_RULER_W-->│


# window widths
WSTRAND_RULER_W = 11
WSTRAND_W = textart.strand.w + WSTRAND_RULER_W + 2 # 2 extra for the border
WDNA_RULER_W = 9 # just 9 for value (max: xx,xxxkbp)
WDNA_W = WDNA_RULER_W + 5 # current largest DNA text art is 5 wide

# window positions (furthest left column)
WSTRAND_X = 0
WSTRAND_RULER_X = textart.strand.w + 1
WDNA_RULER_X = WSTRAND_W + 1
WDNA_X = WDNA_RULER_X + WDNA_RULER_W

#-----------------------------------------------------------------------

def load_dna():

    WDNA_H = curses.LINES - 1 # 1 to line up w/border
    DNA_STRING_H = WDNA_H - 2 # line up w/top + bottom borders
    dna_ruler_min = basepair_format(textart.dna.index)
    dna_ruler_max = basepair_format(textart.dna.index+textart.dna.offset)

    #start window at y = 1 to line up with border
    w_dna = curses.newwin(WDNA_H, WDNA_W, 1, WDNA_X)
    w_dna.addstr(textart.dna.fill(DNA_STRING_H))
    w_dna.noutrefresh()


    #start window at y = 1 to line up with strand border
    w_dna_ruler = curses.newwin(WDNA_H, WDNA_RULER_W, 1, WDNA_RULER_X)
    w_dna_ruler.addstr('{:>9}'.format(dna_ruler_min) + "\n"\
                      +"\n" * (DNA_STRING_H - 3)\
                      +'{:>9}'.format(dna_ruler_max))
    w_dna_ruler.noutrefresh()

#-----------------------------------------------------------------------

def load_strand():

    WSTRAND_H = curses.LINES - 1 # so border isn't cut off by cmd line
    WSTRAND_ID_H = WSTRAND_H - 2 # inner diameter of border



    # fills w_strand with strand TxtArt, but cuts off ends and adds border
    w_strand = curses.newwin(WSTRAND_H, WSTRAND_W, 0, WSTRAND_X)
    w_strand.addstr(textart.strand.fill(WSTRAND_H))
    w_strand.border()



    strand_ruler_max = basepair_format(files.sequence_length)
    # if files.sequence_length >= 10_000_000:
    #     strand_ruler_max = str(round(files.sequence_length / 1_000_000))\
    #               + "mpb"
    # elif files.sequence_length < 10_000:
    #     strand_ruler_max = '{:,}'.format(files.sequence_length) + "bp"
    # else:
    #     strand_ruler_max = '{:,}'.format(round(files.sequence_length / 1_000))\
    #               + "kpb"

    # start at y = 1, x = strand.w + 1 to avoid borders
    w_strand_ruler = curses.newwin(WSTRAND_ID_H, WSTRAND_RULER_W, 1, WSTRAND_RULER_X)
    w_strand_ruler.addstr("┬1bp\n"\
                     + "│\n" * (WSTRAND_ID_H - 2)\
                     + "┴" + strand_ruler_max)



    # >>> HIGHLIGHT CURRENT SELECTION >>>


    #strand.index starts at 0, ends at WSTRAND_ID_H
    textart.strand.index = math.floor((textart.dna.index/files.sequence_length) * WSTRAND_ID_H)

    #strand.offset starts at 0, ends at WSTRAND_ID_H - 1
    #figure out where to stop, and subtract index from that
    dna_endpoint = textart.dna.index + textart.dna.offset
    textart.strand.offset = math.floor((dna_endpoint / files.sequence_length) * WSTRAND_ID_H)\
                    - textart.strand.index
    # the scale_dna and set_dna functions protect dna index/offset from going
    # above the file size, but nothing stops it from setting it to exactly the
    # file size-- which would set strand.offset = WSTRAND_ID_H and cause
    # curses to error due to drawing outside of w_strand_ruler window
    if textart.strand.index + textart.strand.offset == WSTRAND_ID_H:
        textart.strand.offset -= 1

    #w_strand starts outside border, so start at y = 1, x = 1
    w_strand.chgat(1 + textart.strand.index, 1, (WSTRAND_W - 2), curses.A_BLINK)
    for lines in range(1, textart.strand.offset + 1):
        w_strand.chgat(1 + textart.strand.index + lines, 1, (WSTRAND_W - 2), curses.A_BLINK)

    #w_strand_ruler starts inside border, so start at y = 0, x = 0
    w_strand_ruler.chgat(textart.strand.index, 0, WSTRAND_RULER_W, curses.A_REVERSE)
    for lines in range(1, textart.strand.offset + 1):
        w_strand_ruler.chgat(textart.strand.index + lines, 0, WSTRAND_RULER_W, curses.A_REVERSE)


    # <<< HIGHLIGHT CURRENT SELECTION <<<


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


def basepair_format(unformatted :int) -> str:
    if unformatted < 10_000:
        return('{:,}'.format(unformatted) + "bp")
    elif unformatted < 100_000_000:
        return('{:,}'.format(round((unformatted / 1_000)))\
                  + "kpb")
    else:
        return(str(round(unformatted / 1_000_000))\
                  + "mpb")

