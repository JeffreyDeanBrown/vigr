import windows, files
import re


def little_dna():
    windows.dna.update_text(new_text = "║\n")
    windows.load_dna()

def small_dna():
    windows.dna.update_text(new_text = "┠┨\n")
    windows.load_dna()

def medium_dna():
    windows.dna.update_text("├┄┤\n")
    windows.load_dna()

def big_dna():
    windows.dna.update_text("┣┅┅┅┫\n"\
                            "┃   ┃\n")
    windows.load_dna()

def set_dna(offset):
    windows.dna.buffer = offset
    if windows.dna.buffer >= files.sequence_length:
        windows.dna.buffer = files.sequence_length - windows.dna.scale
    if (windows.dna.buffer + windows.dna.scale) > files.sequence_length:
        windows.dna.scale = files.sequence_length - windows.dna.buffer
        scale_dna(None)
    windows.load_dna()

def scale_dna(range_):
    try:
        for x in range_.split(sep = " "):
            if x.isnumeric():
                windows.dna.scale = int(x)
    except:
        pass
    if (windows.dna.buffer + windows.dna.scale) > files.sequence_length:
        windows.dna.buffer = files.sequence_length - windows.dna.scale
    if windows.dna.scale > 1_000_000:
        little_dna()
    elif windows.dna.scale > 1_000:
        small_dna()
    elif windows.dna.scale > 100:
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


