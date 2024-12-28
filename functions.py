import windows
import vigr
import curses



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

ex_cmds = {"l": little_dna,
           "s": small_dna,
           "m": medium_dna,
           "b": big_dna}
