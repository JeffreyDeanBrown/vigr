#!/usr/bin/env python

import curses, sys
import windows, commands, textart, files
from curses_utils import vigrscr

#-----------------------------------------------------------------------

# TODO:

#   FUNCTIONALITY:
#   -implement fasta file parsing & display nucleotides
#   -fasta file as argument
#   - :help function
#   - get it to work with eukaryotic seuqences
#   -that's it!
#
#   FEATURES:
#   -add major and minor axis lines to strand ruler + labels
#   -add docstring to everything
#   -implement subroutine for getting messages to user
#   -annotate function types + argument types
#   -search using / + regex, g/re/p across all sequences
#
#   WHEN I SOMEHOW GET A LOT OF FREE TIME AND NEED SOMETING TO DO:
#   -implement tab autocomplete + ex_command history scrolling

# FIXME:

#   COMMANDS.PY:
#   -sometimes ignores when a window is resized
#   -some features are resetting their cols after already being rendered
#   -move feature drawing to a state function

#-----------------------------------------------------------------------

def debug(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    breakpoint()

#-----------------------------------------------------------------------

def main(stdscr):
    # initial setup
    curses.echo()

    #main loop
    while True:
        curses.echo()
        # apply last change
        render_screen()
        # wait for user input
        curses.curs_set(0)
        # usr input as decimal value
        key = vigrscr.get_key()

        if key == curses.KEY_RESIZE:
            resize_vigr()

        elif key in commands.vigr_commands:
            commands.check_vigr_commands(key)

        elif key == ord(":"):
            # setup for : command
            windows.load_cmd(":")
            curses.curs_set(1)
            curses.echo()

            #usr input as string
            ex = vigrscr.get_ex()
            if ex == chr(curses.KEY_RESIZE):
                resize_vigr()

            elif ex == 'q':
                break # thank you have nice day

            else:
                commands.check_ex_commands(ex)



# load_cmd is always the bottom row, other windows load from
# left to right in the order that they are loaded
def render_screen():
    # check if window is large enough
    if curses.LINES < 6:
       sys.exit("VIGR ERROR: Window Too Short!\n"\
             "   minimum window height is 6 lines.")

    # check if default offset of 10,000bp is an OK size
    if files.file.sequence_length < 40000:
        textart.dna.offset = files.file.sequence_length // 4
    else:
        textart.dna.offset = 9999

    vigrscr.stdscr.noutrefresh()
    windows.load_strand()
    windows.load_dna()
    windows.load_presentation()
    windows.load_popup()
    windows.load_cmd(refresh_only = True)
    curses.doupdate()

def resize_vigr():
    curses.update_lines_cols()
    commands.scale_dna(0) # update dna scale
    render_screen()


curses.wrapper(main)
