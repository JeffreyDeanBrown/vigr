import files, textart, windows
import re, curses



def set_dna(index_):
    if index_ == 0:
        #ERROR: cannot set to zero (when usr error msgs implemented)
        return
    if index_ < 0:
        index_ = 1
    textart.dna.index = index_
    if textart.dna.index >= files.file.sequence_length:
        textart.dna.index = files.file.sequence_length - textart.dna.offset
    if (textart.dna.index + textart.dna.offset) > files.file.sequence_length:
        textart.dna.offset = files.file.sequence_length - textart.dna.index
        scale_dna(0) # scale string art, but don't change offset



# dna string from windows is curses.LINES - 3

def scale_dna(range_: int):
    # WARNING: if you make a new dna text art, make sure windows.WDNA_W
    # can accomodate the width of the text art!

    #prevent setting a scale of 0
    # optional use: scale_dna(0) will resize dna chars without changing the offset
    if range_ == 0:
        pass
    else:
        textart.dna.offset = int(range_)

    # FIXME:
    #       -make a "full sequence" subroutine and make this a call to that routine

    if textart.dna.offset >= files.file.sequence_length:
        textart.dna.index = 1
        textart.dna.offset = files.file.sequence_length - 1
    if (textart.dna.index + textart.dna.offset) > files.file.sequence_length:
        textart.dna.index = files.file.sequence_length - textart.dna.offset

    files.file.reset_cols()

    if textart.dna.offset < (curses.LINES - 3) - 1: # (textart.dna_STRING_H) - 1 for index
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
        set_dna(_move_to)

def up():
    _increment = round((textart.dna.offset + 1)/windows.DNA_STRING_H)
    _move_to = textart.dna.index - _increment
    set_dna(_move_to)

ex_commands = {'big':big_dna}
vigr_commands = {ord('j'):down,
                 ord('k'):up,
                 curses.KEY_DOWN:down,
                 curses.KEY_UP:up}

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
        scale_cmd = cmd.replace("scale ", "").replace(",","")
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
