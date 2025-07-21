import curses
import files
import math
import textart
from Bio.Seq import Seq
from curses_utils import vigrscr

#-----------------------------------------------------------------------


# (diagram not to scale)
# (w_strand has a border, which takes up 2 columns)
#
# <------------wSTRAND_W--------------><--wDNA_RULER_W--><--wDNA_W--><--MAIN_WINDOW_W-->> (the rest)
# │<--------(wSTRAND_W - 2)---------->│
# │<--strand.w--><--wSTRAND_RULER_W-->│


# window widths
wSTRAND_RULER_W = 11
wSTRAND_W = textart.strand.w + wSTRAND_RULER_W + 2 # 2 extra for the border
wDNA_RULER_W = 9 # just 9 for value (max: xx,xxxkbp)
wDNA_W =  6 # current largest DNA text art is 5 wide


# window positions (furthest left column)
wSTRAND_X = 0
wSTRAND_RULER_X = textart.strand.w + 1
wDNA_RULER_X = wSTRAND_W
wDNA_X = wDNA_RULER_X + wDNA_RULER_W
wMAIN_WINDOW_X = wDNA_X + wDNA_W

FEATURE_SPACING = 10


#-----------------------------------------------------------------------

def load_dna():

    wDNA_H = curses.LINES - 1 # 1 to line up w/border
    global DNA_STRING_H
    DNA_STRING_H = wDNA_H - 2 # line up w/top + bottom borders
    dna_ruler_min = basepair_format(textart.dna.index)
    dna_ruler_max = basepair_format(textart.dna.index+textart.dna.offset)

    #start window at y = 1 to line up with border
    w_dna = curses.newwin(wDNA_H, wDNA_W, 1, wDNA_X)
    w_dna.addstr(textart.dna.fill(DNA_STRING_H))

    #parse nucleotides
    if textart.dna.IS_ZOOM:
        for row in range(DNA_STRING_H):
            nuc = files.file.sequence[textart.dna.index + row - 1]
            cnuc = files.file.sequence.complement()[textart.dna.index + row - 1]
            w_dna.addch(row, 1, nuc)
            w_dna.addch(row, 3, cnuc)


    w_dna.noutrefresh()


    #start window at y = 1 to line up with strand border
    w_dna_ruler = curses.newwin(wDNA_H, wDNA_RULER_W, 1, wDNA_RULER_X)
    w_dna_ruler.addstr(dna_ruler_min.rjust(9) + "\n"\
                      +"\n".rjust(9) * (DNA_STRING_H - 3)\
                      +dna_ruler_max.rjust(9))
    w_dna_ruler.noutrefresh()

#-----------------------------------------------------------------------

def load_strand():

    wSTRAND_H = curses.LINES - 1 # so border isn't cut off by cmd line
    wSTRAND_ID_H = wSTRAND_H - 2 # inner diameter of border


    # fills w_strand with strand TxtArt, but cuts off ends and adds border
    w_strand = curses.newwin(wSTRAND_H, wSTRAND_W, 0, wSTRAND_X)
    w_strand.addstr(textart.strand.fill(wSTRAND_H))
    w_strand.border()

    #labels w_strand with sequence id
    if len(files.file.sequence_name) > wSTRAND_W - 3:
        _seq_label = files.file.sequence_name[:(wSTRAND_W-7)] + "..."
    else:
        _seq_label = files.file.sequence_name
    #label is in the border for the ~*~aesthetics~*~
    w_strand.addstr(0, 1, _seq_label)


    strand_ruler_max = basepair_format(files.file.sequence_length)

    # start at y = 1, x = strand.w + 1 to avoid borders
    w_strand_ruler = curses.newwin(wSTRAND_ID_H, wSTRAND_RULER_W, 1, wSTRAND_RULER_X)
    w_strand_ruler.addstr("┬1bp\n"\
                     + "│\n" * (wSTRAND_ID_H - 2)\
                     + "┴" + strand_ruler_max)


    _scaled = scale_to_vigr(index = textart.dna.index, offset = textart.dna.offset,\
                                         char_scale = wSTRAND_ID_H, int_scale = files.file.sequence_length)

    textart.strand.index = _scaled['scaled_index']
    textart.strand.offset = _scaled['scaled_offset']


    #NOTE TO SELF: list(range(n+1)) returns [0:n]

    # w_strand starts outside border, so start at y = 1, x = 1
    _offset_list = list(range(textart.strand.offset + 1))
    for _offset in  _offset_list:
        w_strand.chgat(1 + textart.strand.index + _offset, 1, (wSTRAND_W - 2), curses.A_BLINK)
    #w_strand_ruler starts inside border, so start at y = 0, x = 0
        w_strand_ruler.chgat(textart.strand.index + _offset, 0, wSTRAND_RULER_W, curses.A_REVERSE)

    w_strand.noutrefresh()
    w_strand_ruler.noutrefresh()


#-----------------------------------------------------------------------

def load_main_window():
    global w_main_window

    wMAIN_WINDOW_H = curses.LINES - 1
    PRES_STRING_H = DNA_STRING_H
    wMAIN_WINDOW_W = curses.COLS - wMAIN_WINDOW_X

    files.file.gff_parser(start = textart.dna.index, end = textart.dna.index + textart.dna.offset)

    w_main_window = curses.newwin(wMAIN_WINDOW_H, wMAIN_WINDOW_W, 0, wMAIN_WINDOW_X)
    w_main_window.clear()

    _occupied_tiles = [] # y,x

    #>>> Render feature >>>
    for feature in files.file.features:

        _lower_cutoff = False
        _upper_cutoff = False

        if feature['start'] < textart.dna.index:
            _start = textart.dna.index
            _lower_cutoff = True
        else:
            _start = feature['start']

        if feature['end'] > (textart.dna.index + textart.dna.offset):
            _end = (textart.dna.index + textart.dna.offset)
            _upper_cutoff = True
        else:
            _end = feature['end']

        _scaled = scale_to_vigr(index = _start - textart.dna.index,\
                                             offset = _end - _start,\
                                             char_scale = PRES_STRING_H,\
                                             int_scale = textart.dna.offset + 1)

        _index = _scaled['scaled_index'] + 1 #line up with border
        _offset_list = list(range(_scaled['scaled_offset'] + 1))

        if feature['col']:
            _col = feature['col']
        else:
            _col = 0
            for _offset in _offset_list:
                while ((_index + _offset), _col) in _occupied_tiles:
                    _col += FEATURE_SPACING
            feature['col'] = _col

        for _offset in _offset_list:
            _occupied_tiles.append(((_index+_offset), _col))

        if (_col + wMAIN_WINDOW_X) >= curses.COLS - 2:
            # ERROR: too many cols!
            for row in range(wMAIN_WINDOW_H):
                w_main_window.addstr(row, wMAIN_WINDOW_W-3,'!!', curses.A_ITALIC)
        else:
                                     # ↧  ↥    ▲  𓏚   ⭡ ↓ ↑  Ʌ⯆    ▼↓ ⇂⭣▲
            if _offset_list:
                if len(_offset_list) == 1:
                    feature['tiles'] = (_index, _index)
                    if _lower_cutoff:
                        if feature['strand'] == '+':
                             w_main_window.addstr(_index, _col, 'V')
                        else:
                             w_main_window.addstr(_index, _col, '╵')
                    elif _upper_cutoff:
                        if feature['strand'] == '+':
                             w_main_window.addstr(_index, _col, '╷')
                        else:
                             w_main_window.addstr(_index, _col, 'Ʌ')
                    else:
                        if feature['strand'] == '+':
                             w_main_window.addstr(_index, _col, '⭣', curses.A_BOLD)
                        else:
                             w_main_window.addstr(_index, _col, '⭡', curses.A_BOLD)
                else:
                    feature['tiles'] = (_index, _index + _offset_list[-1])
                    if _lower_cutoff:
                        w_main_window.addstr(_index, _col, '│')
                    else:
                        if feature['strand'] == '+':
                             w_main_window.addstr(_index, _col, '╷')
                        else:
                             w_main_window.addstr(_index, _col, 'Ʌ')
                    if _upper_cutoff:
                        w_main_window.addstr(_index + _offset_list[-1], _col, '│')
                    else:
                        if feature['strand'] == '+':
                            w_main_window.addstr(_index + _offset_list[-1], _col, 'V')
                        else:
                            w_main_window.addstr(_index + _offset_list[-1], _col, '╵')

                    _offset_list = _offset_list[1:-1]

                    for _offset in _offset_list:
                        w_main_window.addstr(_index + _offset, _col, '│')

    #<<< render feature <<<

    #>>> label feature >>>
    for feature in files.file.features:
        if feature['tiles'] != None: # if this feature exists
            if feature['col'] != None:
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
                        if ((row, feature['col']+char) in _occupied_tiles) or ((feature['col'] + char) >= wMAIN_WINDOW_W):
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

def load_cmd(input = None, refresh_only = False):
    w_cmd = curses.newwin(1, curses.COLS, curses.LINES-1, 0)
    if refresh_only: # keep the cmd line as it is
        pass
    elif input: # append the input to the end of the cmd line
        w_cmd.addstr(input)
    else: # no input, clear the command line
        w_cmd.addstr(" " * (curses.COLS-1))
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
