import windows, files
import re


def little_dna():
    windows.dna.update_text(new_text = "║\n")
    windows.load_dna()
    windows.load_strand()

def small_dna():
    windows.dna.update_text(new_text = "┠┨\n")
    windows.load_dna()
    windows.load_strand()

def medium_dna():
    windows.dna.update_text("├┄┤\n")
    windows.load_dna()
    windows.load_strand()

def big_dna():
    windows.dna.update_text("┣┅┅┅┫\n"\
                            "┃   ┃\n")
    windows.load_dna()
    windows.load_strand()

def set_dna(index_):
    windows.dna.index = index_
    if windows.dna.index >= files.sequence_length:
        windows.dna.index = files.sequence_length - windows.dna.offset
    if (windows.dna.index + windows.dna.offset) > files.sequence_length:
        windows.dna.offset = files.sequence_length - windows.dna.index
        scale_dna(None)
    windows.load_dna()
    windows.load_strand()

def scale_dna(range_):
    try:
        for x in range_.split(sep = " "):
            if x.isnumeric():
                windows.dna.offset = int(x)
    except:
        pass

    # FIXME:
    #       -make a "full sequence" subroutine and make this a call to that routine
    if windows.dna.offset > files.sequence_length:
        windows.dna.index = 0
        windows.dna.offset = files.sequence_length
    if (windows.dna.index + windows.dna.offset) > files.sequence_length:
        windows.dna.index = files.sequence_length - windows.dna.offset

    if windows.dna.offset > 1_000_000:
        little_dna()
    elif windows.dna.offset > 1_000:
        small_dna()
    elif windows.dna.offset > 100:
        medium_dna()
    else:
        big_dna()


ex_commands = {}
vigr_commands = {}

def check_ex_commands(cmd): #cmd comes in as a character string
    if cmd in ex_commands:
        run_it = ex_commands[cmd]
        run_it()
    elif cmd.isdigit():
        set_dna(int(cmd))
    elif re.match("^scale", cmd):
        scale_dna(cmd)


