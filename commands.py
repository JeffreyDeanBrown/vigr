import files, textart, windows, curses_utils
import re, curses

command_history = []
last_position = 1
last_scale = 1

def set_dna(index_, memory = True):
    global last_position
    if memory:
        last_position = textart.dna.index

    if index_ <= 0:
        index_ = 1
    textart.dna.index = index_
    if textart.dna.index >= files.file.sequence_length:
        textart.dna.index = files.file.sequence_length - textart.dna.offset
    if (textart.dna.index + textart.dna.offset) > files.file.sequence_length:
        textart.dna.offset = files.file.sequence_length - textart.dna.index
        scale_dna(0) # scale string art, but don't change offset



# dna string from windows is curses.LINES - 3

def scale_dna(range_: int, reset = True):
    #prevent setting a scale of 0
    # optional use: scale_dna(0) will resize dna chars without changing the offset
    if range_ == 0:
        pass
    else:
        textart.dna.offset = int(range_)

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
        medium_dna()
    else:
        small_dna()


def small_dna():
    textart.dna.update_text(new_text = "┠┨\n")

def medium_dna():
    textart.dna.update_text("├┄┤\n")

def big_dna():
    textart.dna.update_text("┣┅┅┅┫\n"\
                            "┃   ┃\n")

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

def strand_level():
    global last_scale
    last_scale = textart.dna.offset
    scale_dna(1)

def scale_toggle():
    global last_scale
    _buffer, last_scale = last_scale, textart.dna.offset
    scale_dna(_buffer, reset = False)


ex_commands = {'big':big_dna,
               'zoom':strand_level}

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
    # is an interger, can be delimited with commas
    elif cmd.replace(",","").isdigit():
        set_dna(int(cmd.replace(",","")))
    # is labeled bp, kbp, or mbp
    elif re.match("^\d+.*bp", cmd.replace(",","")):
        if cmd.replace("bp","").replace(",","").isdigit():
            value = int(cmd.replace("bp","").replace(",",""))
            set_dna(value)
        elif cmd.replace("kbp","").isdigit():
            value = int(cmd.replace("kbp","").replace(",","")) * 1000
            set_dna(value)
        elif cmd.replace("mbp","").isdigit():
            value = int(cmd.replace("mbp","").replace(",","")) * 1_000_000
            set_dna(value)
    # repeat, but for scaling offset
    # FIXME
    #      make this DRY
    elif re.match("^scale", cmd):
        scale_cmd = cmd.replace("scale", "").replace(' ', '').replace(",","")
        # no value given
        if scale_cmd == '':
            scale_dna(10000)
        # is an interger, can be delimited with commas
        if scale_cmd.isdigit():
            scale_dna(int(scale_cmd))
        # is labeled bp, kbp, or mbp
        elif re.match(".*bp", scale_cmd):
            if scale_cmd.replace("bp","").isdigit():
                value = int(scale_cmd.replace("bp",""))
                scale_dna(value)
            elif scale_cmd.replace("kbp","").isdigit():
                value = int(scale_cmd.replace("kbp","")) * 1000
                scale_dna(value)
            elif scale_cmd.replace("mbp","").isdigit():
                value = int(scale_cmd.replace("mbp","")) * 1_000_000
                scale_dna(value)


def check_vigr_commands(cmd): #cmd comes in as a character string

    if cmd in vigr_commands:
        run_it = vigr_commands[cmd]
        run_it()
