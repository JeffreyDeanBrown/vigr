import curses
import files
import math
import textart

#-----------------------------------------------------------------------


# (diagram not to scale)
# (w_strand has a border, which takes up 2 columns)
#
# <------------WSTRAND_W--------------><--WDNA_RULER_W--><--WDNA_W--><--PRESENTATION_W-->> (the rest)
# │<--------(WSTRAND_W - 2)---------->│
# │<--strand.w--><--WSTRAND_RULER_W-->│


# window widths
WSTRAND_RULER_W = 11
WSTRAND_W = textart.strand.w + WSTRAND_RULER_W + 2 # 2 extra for the border
WDNA_RULER_W = 9 # just 9 for value (max: xx,xxxkbp)
WDNA_W =  6 # current largest DNA text art is 5 wide

# window positions (furthest left column)
WSTRAND_X = 0
WSTRAND_RULER_X = textart.strand.w + 1
WDNA_RULER_X = WSTRAND_W
WDNA_X = WDNA_RULER_X + WDNA_RULER_W
WPRESENTATION_X = WDNA_X + WDNA_W

FEATURE_SPACING = 10

# render popup window next during next cycle
render_popup = False
popup_text = ""
popup_label = ""

#-----------------------------------------------------------------------

def load_dna():

    WDNA_H = curses.LINES - 1 # 1 to line up w/border
    global DNA_STRING_H
    DNA_STRING_H = WDNA_H - 2 # line up w/top + bottom borders
    dna_ruler_min = basepair_format(textart.dna.index)
    dna_ruler_max = basepair_format(textart.dna.index+textart.dna.offset)

    #start window at y = 1 to line up with border
    w_dna = curses.newwin(WDNA_H, WDNA_W, 1, WDNA_X)
    w_dna.addstr(textart.dna.fill(DNA_STRING_H))
    w_dna.noutrefresh()


    #start window at y = 1 to line up with strand border
    w_dna_ruler = curses.newwin(WDNA_H, WDNA_RULER_W, 1, WDNA_RULER_X)
    w_dna_ruler.addstr(dna_ruler_min.rjust(9) + "\n"\
                      +"\n".rjust(9) * (DNA_STRING_H - 3)\
                      +dna_ruler_max.rjust(9))
    w_dna_ruler.noutrefresh()

#-----------------------------------------------------------------------

def load_strand():

    WSTRAND_H = curses.LINES - 1 # so border isn't cut off by cmd line
    WSTRAND_ID_H = WSTRAND_H - 2 # inner diameter of border


    # fills w_strand with strand TxtArt, but cuts off ends and adds border
    w_strand = curses.newwin(WSTRAND_H, WSTRAND_W, 0, WSTRAND_X)
    w_strand.addstr(textart.strand.fill(WSTRAND_H))
    w_strand.border()

    #labels w_strand with sequence id
    if len(files.file.sequence_name) > WSTRAND_W - 3:
        _seq_label = files.file.sequence_name[:(WSTRAND_W-7)] + "..."
    else:
        _seq_label = files.file.sequence_name
    #label is in the border for the ~*~aesthetics~*~
    w_strand.addstr(0, 1, _seq_label)


    strand_ruler_max = basepair_format(files.file.sequence_length)

    # start at y = 1, x = strand.w + 1 to avoid borders
    w_strand_ruler = curses.newwin(WSTRAND_ID_H, WSTRAND_RULER_W, 1, WSTRAND_RULER_X)
    w_strand_ruler.addstr("┬1bp\n"\
                     + "│\n" * (WSTRAND_ID_H - 2)\
                     + "┴" + strand_ruler_max)


    _scaled = scale_to_vigr(index = textart.dna.index, offset = textart.dna.offset,\
                                         char_scale = WSTRAND_ID_H, int_scale = files.file.sequence_length)

    textart.strand.index = _scaled['scaled_index']
    textart.strand.offset = _scaled['scaled_offset']


    #NOTE TO SELF: list(range(n+1)) returns [0:n]

    # w_strand starts outside border, so start at y = 1, x = 1
    _offset_list = list(range(textart.strand.offset + 1))
    for _offset in  _offset_list:
        w_strand.chgat(1 + textart.strand.index + _offset, 1, (WSTRAND_W - 2), curses.A_BLINK)
    #w_strand_ruler starts inside border, so start at y = 0, x = 0
        w_strand_ruler.chgat(textart.strand.index + _offset, 0, WSTRAND_RULER_W, curses.A_REVERSE)

    w_strand.noutrefresh()
    w_strand_ruler.noutrefresh()


#-----------------------------------------------------------------------

def load_presentation():
    WPRESENTATION_H = curses.LINES - 1
    PRES_STRING_H = DNA_STRING_H
    WPRESENTATION_W = curses.COLS - WPRESENTATION_X

    #FIXME
    files.file.gff_parser(start = textart.dna.index, end = textart.dna.index + textart.dna.offset)

    w_presentation = curses.newwin(WPRESENTATION_H, WPRESENTATION_W, 0, WPRESENTATION_X)

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

        if (_col + WPRESENTATION_X) >= curses.COLS - 2:
            # ERROR: too many cols!
            for row in range(WPRESENTATION_H):
                w_presentation.addstr(row, WPRESENTATION_W-3,'!!', curses.A_ITALIC)
        else:


                                     # ↧  ↥    ▲  𓏚   ⭡ ↓ ↑  Ʌ⯆    ▼↓ ⇂⭣▲
            if len(_offset_list) == 1:
                feature['tiles'] = (_index, _index)
                if _lower_cutoff:
                    if feature['strand'] == '+':
                         w_presentation.addstr(_index, _col, 'V')
                    else:
                         w_presentation.addstr(_index, _col, '╵')
                elif _upper_cutoff:
                    if feature['strand'] == '+':
                         w_presentation.addstr(_index, _col, '╷')
                    else:
                         w_presentation.addstr(_index, _col, 'Ʌ')
                else:
                    if feature['strand'] == '+':
                         w_presentation.addstr(_index, _col, '⭣', curses.A_BOLD)
                    else:
                         w_presentation.addstr(_index, _col, '⭡', curses.A_BOLD)
            else:
                feature['tiles'] = (_index, _index + _offset_list[-1])
                if _lower_cutoff:
                    w_presentation.addstr(_index, _col, '│')
                else:
                    if feature['strand'] == '+':
                         w_presentation.addstr(_index, _col, '╷')
                    else:
                         w_presentation.addstr(_index, _col, 'Ʌ')
                if _upper_cutoff:
                    w_presentation.addstr(_index + _offset_list[-1], _col, '│')
                else:
                    if feature['strand'] == '+':
                        w_presentation.addstr(_index + _offset_list[-1], _col, 'V')
                    else:
                        w_presentation.addstr(_index + _offset_list[-1], _col, '╵')

                _offset_list = _offset_list[1:-1]

                for _offset in _offset_list:
                    w_presentation.addstr(_index + _offset, _col, '│')

    #<<< render feature <<<

    #>>> label feature >>>
    for feature in files.file.features:
        if feature['tiles'] != None: # if this feature exists
            start, end = feature['tiles']
            if feature['name']:
                name = feature['name'][0]
            else:
                name = ''
            product = feature['product']
            label = ' ' + feature['featuretype'] + ': ' + name + " ("\
                    + product + ")"
            can_print = False

            for row in range(start, end+1):
                for char in range(1, len(label)+1):
                    if ((row, feature['col']+char) in _occupied_tiles) or ((feature['col'] + char) >= WPRESENTATION_W):
                        can_print = False
                        break
                    else:
                        can_print = True
                if can_print:
                    w_presentation.addstr(row, feature['col'] + 1, label)
                    break
    #<<< label feature <<<

    w_presentation.noutrefresh()

#-----------------------------------------------------------------------

def load_popup():
    global WPOPUP_H, WPOPUP_W, render_popup, popup_text, popup_label
    global WPOPUP_ROWS, WPOPUP_COLS

    # one for load_cmd, four for a gap
    WPOPUP_H = curses.LINES - 5
    WPOPUP_W = curses.COLS - 4
    WPOPUP_ROWS = WPOPUP_H - 2 - 1 #borders and dont-draw-over
    WPOPUP_COLS = WPOPUP_W - 2 - 1 #ditto


    if render_popup:
        w_popup = curses.newwin(WPOPUP_H, WPOPUP_W, 3, 3)
        w_popup.border()
        w_popup.addstr(0, 3, popup_label)
        w_popup.noutrefresh()
        w_popup_text = curses.newwin(WPOPUP_H-2, WPOPUP_W-2, 4, 4)
        w_popup_text.addstr(popup_text)
        w_popup_text.noutrefresh()
        render_popup = False


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
