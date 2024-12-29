import windows
import re


def little_dna():
    windows.dna.update_text(new_text = "║\n")
    windows.load_dna()

def small_dna():
    windows.dna.update_text(new_text = "││\n")
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
    windows.load_dna()

def scale_dna(range_):
    for x in range_.split(sep = " "):
        if x.isnumeric():
            windows.dna.scale = int(x)
    if windows.dna.scale > 1_000_000_000:
        little_dna()
    elif windows.dna.scale > 1_000_000:
        small_dna()
    elif windows.dna.scale > 1_000:
        medium_dna()
    else:
        big_dna()

ex_commands = {}


def check_ex_commands(cmd): #cmd comes in as a character string
    if cmd in ex_commands:
        run_it = ex_commands[cmd]
        run_it()
    elif cmd.isdigit():
        set_dna(int(cmd))
    elif re.match("^scale", cmd):
        scale_dna(cmd)


vigr_commands = {}
