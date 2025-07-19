import files, textart, windows, curses_utils
import re, curses, typing

last_position = 1
last_scale = 1
DEFAULT_SCALE = 10000

def set_dna(index_, memory = True):
    global last_position

    if index_ < 0:
        index_ = 1

    if index_:
        if memory:
            last_position = textart.dna.index
        textart.dna.index = index_

    if textart.dna.index >= files.file.sequence_length:
        textart.dna.index = files.file.sequence_length - textart.dna.offset
    if (textart.dna.index + textart.dna.offset) > files.file.sequence_length:
        textart.dna.offset = files.file.sequence_length - textart.dna.index
        scale_dna(0) # scale string art, but don't change offset



# dna string from windows is curses.LINES - 3

def scale_dna(range_, reset = True):
    #prevent setting a scale of 0 or None
    # optional use: scale_dna(0) will resize dna chars without changing the offset
    if range_:
        if range_ < 0:
            range_ = 1
        textart.dna.offset = range_

    if reset:
        global last_scale
        last_scale = 1

    # FIXME:
    #       -make a "full sequence" subroutine and make this a call to that routine

    if textart.dna.offset >= files.file.sequence_length:
        textart.dna.index = 1
        textart.dna.offset = files.file.sequence_length - 1
    if (textart.dna.index + textart.dna.offset) > files.file.sequence_length:
        textart.dna.index = files.file.sequence_length - textart.dna.offset

    files.file.reset_cols()

    if textart.dna.offset <= (curses.LINES - 3) - 1: # (textart.dna_STRING_H) - 1 for index
        textart.dna.offset = (curses.LINES - 3) - 1
        if files.HAS_FASTA:
            big_dna()
        else:
            medium_dna()
    else:
        small_dna()


def small_dna():
    textart.dna.update_text(new_text = "┠┨\n")
    textart.dna.not_zoom()

def medium_dna():
    textart.dna.update_text("├┄┤\n")
    textart.dna.not_zoom()

def big_dna():
    textart.dna.update_text("┣X X┫\n")
    textart.dna.is_zoom()

def down():
    _increment = round((textart.dna.offset + 1)/windows.DNA_STRING_H)
    _move_to = textart.dna.index + _increment
    if textart.dna.index + textart.dna.offset + _increment > files.file.sequence_length:
        return
    else:
        set_dna(_move_to, memory = False)

def up():
    _increment = round((textart.dna.offset + 1)/windows.DNA_STRING_H)
    _move_to = textart.dna.index - _increment
    set_dna(_move_to, memory = False)

def beggining():
    _key = curses_utils.vigrscr.get_key()
    if _key == ord('g'):
        set_dna(1)

def end():
    set_dna(files.file.sequence_length)

def go_back():
    global last_position
    _buffer, last_position = last_position, textart.dna.index
    set_dna(_buffer)

def scale_toggle():
    global last_scale
    _buffer, last_scale = last_scale, textart.dna.offset
    scale_dna(_buffer, reset = False)

def popup_seqids():
    # format seqids to "[index]:[seqid]..." with max length of 15
    seqs = []
    for name in files.file.seqids:
        n = files.file.seqids.index(name)
        string = str(n)+":"+name
        if len(string) > 20:
            string = string[:17] + '...'
        seqs.append(string)
    #render it into a popup window
    windows.load_popup(_list = seqs,
                       label = "available sequences:")

def switch_sequence(seq_name):
    if seq_name.isdigit():
        if int(seq_name) < len(files.file.seqids):
            files.file.set_sequence(int(seq_name))
    elif seq_name in files.file.seqids:
        files.file.set_sequence(seq_name)

def space_features(space):
    if space.isdigit():
        space = int(space)
        if space > 0:
            windows.FEATURE_SPACING = space
            files.file.reset_cols()

def select_feature_types(selection):
    if selection:
        files.SHOW_ALL_FEATURES = False
        files.select_featuretypes = selection
    else:
        files.SHOW_ALL_FEATURES = True
    files.file.clear_features()

def set_children(parent):
    if parent:
        for feature in files.file.features:
            if feature['name']:
                if feature['name'][0] == parent:
                    parent_id = feature['id']
                    files.named_parent = parent_id
                    files.CHILDREN_ONLY = True
                    files.SHOW_ALL_FEATURES = True
    else:
        files.named_parent = None
        files.CHILDREN_ONLY = False
    files.file.clear_features()

def reset_constraints():
    files.named_parent = None
    files.select_featuretypes = ['gene']
    files.SHOW_ALL_FEATURES = True
    files.CHILDREN_ONLY = False


ex_commands = {'zoom':scale_toggle,
               'seqs': popup_seqids,
               'reset':reset_constraints}

vigr_commands = {ord('j'):down,
                 ord('k'):up,
                 curses.KEY_DOWN:down,
                 curses.KEY_UP:up,
                 ord('g'):beggining,
                 ord('G'):end,
                 15:go_back, # ^O
                 ord('z'):scale_toggle}


def check_ex_commands(cmd): #cmd comes in as a character string

    if cmd in ex_commands:
        run_it = ex_commands[cmd]
        run_it()
    # cmd is an int, or comma delimited int, or on "bp","kbp","mbp" scale
    elif parse_comma_bp(cmd):
        set_dna(parse_comma_bp(cmd))
    # starts with "scale"
    elif re.match("^scale", cmd):
        scale_cmd = cmd.replace("scale", "").replace(' ', '')
        # no value given
        if scale_cmd == '':
            scale_dna(DEFAULT_SCALE)
        else:
            # check if comma delimited, parse "bp","kbp",or "mbp" scales
            scale_dna(parse_comma_bp(scale_cmd))
    elif re.match("^seq ", cmd):
        seq_cmd = cmd.replace("seq ","")
        switch_sequence(seq_cmd)
    elif re.match("^space ", cmd):
        space_cmd = cmd.replace("space ","")
        space_features(space_cmd)
    elif re.match("^type", cmd):
        select_cmd = cmd.replace("type","")
        select_feature_types(select_cmd)
    elif re.match("^children", cmd):
        children_cmd = cmd.replace("children","").replace(" ","")
        set_children(children_cmd)



def parse_comma_bp(input: str)-> typing.Union[int,None]:

    _ncomma = input.replace(",","").replace(" ","")

    if _ncomma.replace("bp","").isdigit():
        return(int(_ncomma.replace("bp","")))

    elif _ncomma.replace("kbp","").isdigit():
        return(int(_ncomma.replace("kbp","")) * 1000)

    elif _ncomma.replace("mbp","").isdigit():
        return(int(_ncomma.replace("mbp","")) * 1000000)



def check_vigr_commands(cmd): #cmd comes in as a character string

    if cmd in vigr_commands:
        run_it = vigr_commands[cmd]
        run_it()
