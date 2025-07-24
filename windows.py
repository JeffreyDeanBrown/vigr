import curses
import files
import math
import textart
from Bio.Seq import Seq
from curses_utils import vigrscr


#-----------------------------------------------------------------------



# (diagram not to scale)
#
# <------------HELIX_W--------------><--DNA_RULER_W--><--DNA_W--><--MAIN_WINDOW_W-->> (the rest)
# │<--inside border (HELIX_W - 2)--->│
# │<--helix.w--><---HELIX_RULER_W--->│
# │  █════██     ┬1bp                │             1bp┠┨
# │  █══██       │                   │                ┠┨          │ CDS xxy (theoretical gene)
# │   ██         │                   │                ┠┨          │
# │  █══██       │                   │                ┠┨          │
# │  █════██     │                   │                ┠┨          V Ʌ rRNA yyx (theoretical gene)
# │   ██════█    ┴20kbp              │           15kbp┠┨            │
#
#      ^textart.large_helix      textart.little_ladder^

# window widths are marked with a W (WINDOW_W) and the position of the
# left-most edge is marked with an X (WINDOW_X)

HELIX_RULER_W = 11 # up to xx,xxxkbp (1 space + 9 wide + 1 for the border)
HELIX_W = textart.large_helix.w + HELIX_RULER_W + 2 # 2 extra for the border
DNA_RULER_W = 9 # just 9 for value (max: xx,xxxkbp)
DNA_W =  6 # current largest DNA text art is 5 wide (ex. |C G| )


# window positions (furthest left column)
HELIX_X = 0
HELIX_RULER_X = textart.large_helix.w + 1
DNA_RULER_X = HELIX_W
DNA_X = DNA_RULER_X + DNA_RULER_W
MAIN_WINDOW_X = DNA_X + DNA_W

FEATURE_SPACING = 10


#-----------------------------------------------------------------------

def load_dna():

    DNA_H = curses.LINES - 1 # 1 to line up w/border, starting at y = 1
    global DNA_STRING_H
    DNA_STRING_H = DNA_H - 2 # line up w/top + bottom borders
    dna_ruler_min = basepair_format(textart.little_ladder.index)
    dna_ruler_max = basepair_format(textart.little_ladder.index+textart.little_ladder.offset)

    #start window at y = 1 to line up with border
    w_dna = curses.newwin(DNA_H, DNA_W, 1, DNA_X)
    w_dna.addstr(textart.little_ladder.fill(DNA_STRING_H))

    #parse nucleotides
    if textart.little_ladder.is_zoom:
        for row in range(DNA_STRING_H):
            nuc = files.file.sequence[textart.little_ladder.index + row - 1]
            cnuc = files.file.sequence.complement()[textart.little_ladder.index + row - 1]
            w_dna.addch(row, 1, nuc)
            w_dna.addch(row, 3, cnuc)


    w_dna.noutrefresh()


    #start window at y = 1 to line up with strand border
    w_dna_ruler = curses.newwin(DNA_H, DNA_RULER_W, 1, DNA_RULER_X)
    w_dna_ruler.addstr(dna_ruler_min.rjust(9) + "\n"\
                      +"\n".rjust(9) * (DNA_STRING_H - 3)\
                      +dna_ruler_max.rjust(9))
    w_dna_ruler.noutrefresh()

#-----------------------------------------------------------------------

def load_strand():

    HELIX_H = curses.LINES - 1 # so border isn't cut off by cmd line
    HELIX_ID_H = HELIX_H - 2 # inner diameter of border


    # fill w_helix with helix art, add a border
    w_helix = curses.newwin(HELIX_H, HELIX_W, 0, HELIX_X)
    w_helix.addstr(textart.large_helix.fill(HELIX_H))
    w_helix.border()

    #labels w_helix with sequence id
    if len(files.file.sequence_name) > HELIX_W - 3:
        _seq_label = files.file.sequence_name[:(HELIX_W-7)] + "..."
    else:
        _seq_label = files.file.sequence_name
    #label is in the border for the ~*~aesthetics~*~
    w_helix.addstr(0, 1, _seq_label)


    strand_ruler_max = basepair_format(files.file.sequence_length)

    # start at y = 1, x = helix.w + 1 to avoid borders
    w_helix_ruler = curses.newwin(HELIX_ID_H, HELIX_RULER_W, 1, HELIX_RULER_X)
    w_helix_ruler.addstr("┬1bp\n"\
                     + "│\n" * (HELIX_ID_H - 2)\
                     + "┴" + strand_ruler_max)


    _scaled = scale_to_vigr(index = textart.little_ladder.index, offset = textart.little_ladder.offset,\
                                         char_scale = HELIX_ID_H, int_scale = files.file.sequence_length)

    textart.large_helix.index = _scaled['scaled_index']
    textart.large_helix.offset = _scaled['scaled_offset']


    #NOTE TO SELF: list(range(n+1)) returns [0:n]

    # w_helix starts outside border, so start at y = 1, x = 1
    _offset_list = list(range(textart.large_helix.offset + 1))
    for _offset in  _offset_list:
        w_helix.chgat(1 + textart.large_helix.index + _offset, 1, (HELIX_W - 2), curses.A_BLINK)
    #w_helix_ruler starts inside border, so start at y = 0, x = 0
        w_helix_ruler.chgat(textart.large_helix.index + _offset, 0, HELIX_RULER_W, curses.A_REVERSE)

    w_helix.noutrefresh()
    w_helix_ruler.noutrefresh()


#-----------------------------------------------------------------------

def load_main_window():
    global w_main_window

    MAIN_WINDOW_H = curses.LINES - 1
    PRES_STRING_H = DNA_STRING_H
    MAIN_WINDOW_W = curses.COLS - MAIN_WINDOW_X

    files.file.gff_parser(start = textart.little_ladder.index, end = textart.little_ladder.index + textart.little_ladder.offset)

    w_main_window = curses.newwin(MAIN_WINDOW_H, MAIN_WINDOW_W, 0, MAIN_WINDOW_X)
    w_main_window.clear()

    _occupied_tiles = [] # y,x

    #>>> CREATE FEATURE >>>

    for feature in files.file.features:

        _lower_cutoff = False
        _upper_cutoff = False

        #check if start of feature is cutoff
        if feature['start'] < textart.little_ladder.index:
            _start = textart.little_ladder.index
            _lower_cutoff = True
        else:
            _start = feature['start']

        #check if end of feature is cutoff
        if feature['end'] > (textart.little_ladder.index + textart.little_ladder.offset):
            _end = (textart.little_ladder.index + textart.little_ladder.offset)
            _upper_cutoff = True
        else:
            _end = feature['end']

        #returns dict {scaled_index:, scaled_offset}
        _scaled = scale_to_vigr(index = _start - textart.little_ladder.index,\
                                             offset = _end - _start,\
                                             char_scale = PRES_STRING_H,\
                                             int_scale = textart.little_ladder.offset + 1)

        #_index is the starting row
        _index = _scaled['scaled_index'] + 1 #line up with border

        #_offset_list is a list of rows to fill in
        # to reduce jitteriness, features will try to maintain the
        # same length (i.e. offset)
        if _upper_cutoff or _lower_cutoff:
            _offset_list = list(range(_scaled['scaled_offset'] + 1))
        elif not feature['offset_list']:
            feature['offset_list'] = list(range(_scaled['scaled_offset'] + 1))
            _offset_list = feature['offset_list'].copy()
        else:
            _offset_list = feature['offset_list'].copy()

    #<<< CREATE FEATURE <<<

    #>>> COLUMN MANAGEMENT >>>

        #if the feature is assigned a column "col" already:
        #   keep the same column
        if not feature['col']:
            #keep trying cols until you get to an empty one

            #feature['col'] = 0
            for _offset in _offset_list:
                while ((_index + _offset), feature['col']) in _occupied_tiles:
                    feature['col'] += FEATURE_SPACING

        for _offset in _offset_list:
            _occupied_tiles.append(((_index+_offset), feature['col']))

        if (feature['col'] + MAIN_WINDOW_X) >= curses.COLS - 2:
            # ERROR: too many cols!
            for row in range(MAIN_WINDOW_H):
                w_main_window.addstr(row, MAIN_WINDOW_W-3,'!!', curses.A_ITALIC)
            continue #don't print that feature

    # <<< COLUMN MANAGEMENT <<<

    # >>> PRINT FEATURE >>>

        # ↧  ↥   ▲  𓏚   ⭡ ↓ ↑  Ʌ⯆    ▼↓ ⇂⭣▲
        if len(_offset_list) == 1:
            feature['tiles'] = (_index, _index)
            if _lower_cutoff:
                if feature['strand'] == '+':
                     w_main_window.addstr(_index, feature['col'], 'V')
                else:
                     w_main_window.addstr(_index, feature['col'], '╵')
            elif _upper_cutoff:
                if feature['strand'] == '+':
                     w_main_window.addstr(_index, feature['col'], '╷')
                else:
                     w_main_window.addstr(_index, feature['col'], 'Ʌ')
            else:
                if feature['strand'] == '+':
                     w_main_window.addstr(_index, feature['col'], '⭣', curses.A_BOLD)
                else:
                     w_main_window.addstr(_index, feature['col'], '⭡', curses.A_BOLD)
        else:
            feature['tiles'] = (_index, _index + _offset_list[-1])
            if _lower_cutoff:
                w_main_window.addstr(_index, feature['col'], '│')
            else:
                if feature['strand'] == '+':
                     w_main_window.addstr(_index, feature['col'], '╷')
                else:
                     w_main_window.addstr(_index, feature['col'], 'Ʌ')
            if _upper_cutoff:
                w_main_window.addstr(_index + _offset_list[-1], feature['col'], '│')
            else:
                if feature['strand'] == '+':
                    w_main_window.addstr(_index + _offset_list[-1], feature['col'], 'V')
                else:
                    w_main_window.addstr(_index + _offset_list[-1], feature['col'], '╵')

            _offset_list = _offset_list[1:-1]

            for _offset in _offset_list:
                w_main_window.addstr(_index + _offset, feature['col'], '│')

    #<<< PRINT FEATURE <<<

    #>>> label feature >>>

    for feature in files.file.features:
        if feature['tiles'] == None:
            continue # that feature was not printed
        start, end = feature['tiles']
        if feature['name']:
            name = feature['name'][0]
        else:
            name = ''
        if feature['product']:
            product = "(" + feature['product'][0] + ")"
        else:
            product = ''
        label = ' ' + feature['featuretype'] + ': ' + name + product
        can_print = False

        for row in range(start, end+1):
            for char in range(1, len(label)+1):
                if ((row, feature['col']+char) in _occupied_tiles) or ((feature['col'] + char) >= MAIN_WINDOW_W):
                    can_print = False
                    break
                else:
                    can_print = True
            if can_print:
                w_main_window.addstr(row, feature['col'] + 1, label)
                break

    #<<< label feature <<<

    w_main_window.noutrefresh()

#-----------------------------------------------------------------------


def load_popup(text = "", label = "", _list = None):

    # popup window widths
    wPOPUP_H = curses.LINES - 5 # 1 for load_cmd, 4 for a gap
    wPOPUP_W = curses.COLS - 4
    wPOPUP_ROWS = wPOPUP_H - 2 - 1 #borders and dont-draw-over
    wPOPUP_COLS = wPOPUP_W - 2 - 1 #ditto
    if wPOPUP_H < 3: return
    if wPOPUP_W < 5: return

    #>>> sorting and organizing a list >>>i

    if _list: # a list needs to be sorted by columns and reorganized

        text_cols = wPOPUP_COLS
        text_rows = wPOPUP_ROWS + 1 #something to do with indexing

        # split list into columns which matches the height of w_popup
        _list_by_col = [] # a matrix of seq split into cols
        # i.e. [1,2,3,4,5,6,7,8] becomes [[1,2,3],[4,5,6],[7,8]]
        # for: 1   4   7
        #      2   5   8
        #      3   6
        for x in range(0, len(_list), text_rows):
            #_column_values will list everything in each column, starting at
            # column containing seq[0:text_rows] then seq[text_rows:text_rows*2]
            # etc (remember: indexing using [] works as borders surrounding
            #      values!)
            _column_values = _list[x:x+text_rows]
            if len(_column_values) < text_rows: # we are on a short col (last col)
                empty_rows = text_rows - len(_column_values)
                i = 0
                while i < empty_rows:
                    _column_values.append(" ")
                    i += 1
            _list_by_col.append(_column_values)

        # index through the columns by row, appending to a "row" matrix
        _list_by_row = []
        i = 0
        while i < len(_list_by_col[0]): # only run through longest column
            string = ""
            for col in _list_by_col:
                string = string + col[i] + " "
            if len(string) > text_cols:
                string = string[:text_cols-5] + "...!!"
            _list_by_row.append(string)
            i += 1

        if len(_list_by_row) > text_rows:
            _list_by_row = _list_by_row[:text_rows]
            _list_by_row[text_rows] = "Terminal too small!"
        text = "\n".join(_list_by_row) # all together now

    #<<< sorting and organizing a list <<<

    #render the popup border and write the label
    w_popup = curses.newwin(wPOPUP_H, wPOPUP_W, 3, 3)
    w_popup.border()
    w_popup.addstr(0, 3, label)
    w_popup.noutrefresh()
    #render the popup (main message) on top of the border
    w_popup_text = curses.newwin(wPOPUP_H-2, wPOPUP_W-2, 4, 4)
    w_popup_text.addstr(text)
    w_popup_text.noutrefresh()

    #keep the popup window active until the next keypress
    curses.curs_set(0) # set cursor to invisible
    vigrscr.get_key() # wait for user input
    #after the user presses a key, the entire screen is re-rendered
    #and the main loop resets


#-----------------------------------------------------------------------


def load_notepad(text = "", label = ""):

    # popup window widths
    wNOTEPAD_H = curses.LINES - 5 # 1 for load_cmd, 4 for a gap
    wNOTEPAD_W = curses.COLS - 4
    wNOTEPAD_ROWS = wNOTEPAD_H - 2 - 1 #borders and dont-draw-over
    wNOTEPAD_COLS = wNOTEPAD_W - 2 - 1 #ditto
    if wNOTEPAD_H < 3: return
    if wNOTEPAD_W < 5: return

    text_rows = wNOTEPAD_ROWS
    text_cols = wNOTEPAD_COLS

    pad_height = text.count('\n') + 1
    pad_width = 90

    #render the notepad border and write the label
    w_notepad = curses.newwin(wNOTEPAD_H, wNOTEPAD_W, 3, 3)
    w_notepad.border()
    w_notepad.addstr(0, 3, label)
    w_notepad.noutrefresh()
    #render the notepad (main message) on top of the border
    w_notepad_text = curses.newpad(pad_height, pad_width)
    w_notepad_text.addstr(text)

    # scrolling function for the notepad
    pad_pos = 0
    while True:
        w_notepad_text.noutrefresh(pad_pos, 0, 4, 4, text_rows + 4, text_cols)
        key = vigrscr.get_key()

        if key in [curses.KEY_UP, ord('k')]:
            if pad_pos > 0:
                pad_pos -= 1
        elif key in [curses.KEY_DOWN, ord('j')]:
            if pad_pos < pad_height - text_rows:
                pad_pos += 1
        else:
            break


#-----------------------------------------------------------------------


def load_cmd(input = None, refresh_only = False):
    w_cmd = curses.newwin(1, curses.COLS, curses.LINES-1, 0)
    if refresh_only: # keep the cmd line as it is
        pass
    elif input: # append the input to the end of the cmd line
        w_cmd.addstr(input)
    else: # no input, clear the command line
        w_cmd.addstr(" " * (curses.COLS-1))
    w_cmd.noutrefresh()

#-----------------------------------------------------------------------

def basepair_format(unformatted :int) -> str:
    if unformatted < 10_000:
        return('{:,}'.format(unformatted) + "bp")
    elif unformatted < 100_000_000:
        return('{:,}'.format(round((unformatted / 1_000)))\
                  + "kpb")
    else:
        return(str(round(unformatted / 1_000_000))\
                  + "mpb")

#-----------------------------------------------------------------------

def scale_to_vigr(index, offset, char_scale, int_scale) -> dict:
    '''
    returns dict {scaled_index:, scaled_offset} scaled down to chars in char_scale.
    '''
    if index < 0:
        index = 0
    _endpoint = index + offset
    scaled_index = math.floor((index / int_scale) * char_scale)

    scaled_offset = math.floor((_endpoint / int_scale) * char_scale)\
                    - scaled_index

    # make sure when at the end of char_scale, you don't add a new char
    # otherwise you will go over your chars limit
    if scaled_index + scaled_offset == char_scale:
        scaled_offset -= 1

    return({'scaled_index':scaled_index, 'scaled_offset':scaled_offset})
