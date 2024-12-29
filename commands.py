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
        scale_dna("")
    windows.load_dna()
    windows.load_strand()

def scale_dna(range_):

    # optional use: scale_dna(0) or scale_dna("") will resize dna chars
    # without changing the offset
    if range_:
        windows.dna.offset = int(range_)

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


