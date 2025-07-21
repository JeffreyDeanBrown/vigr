#!/usr/bin/env python

import curses, sys
import windows, commands
from curses_utils import vigrscr

#-----------------------------------------------------------------------
# TODO:
#
#   -parse .gff files which have fasta appended on the end
#   -reformat commands.py to make it easier to see commands
#   -:h[elp] function and $ vigr.py -h[elp]
#   -setup installation script with venv stuff
#
#   PRE-RELEASE CHECKLIST:
#   -reformat like you mean it
#   -make sure ex command names make sense, add shortcuts
#   -add docstring to everything
#   -annotate function types + argument types?
#   -clear out all FIXMEs
#
#   POTENTIAL ADDITIONS:
#   -add major and minor axis lines to strand ruler + labels
#   -also show parent when showing children & label screen w/parent name
#   -implement subroutine for getting messages to user (just center
#       text in a popup)
#
#   WHEN I SOMEHOW GET A LOT OF FREE TIME AND NEED SOMETING TO DO:
#   -selecting features (mouse, arrow keys) and writing that name over others
#   -implement tab autocomplete + ex_command history scrolling
#   -search using / + regex, g/re/p across all sequences in gff
#   -implement browsing or comparing multiple parent/children trees
#
# FIXME:
#   -cutoff features (rarely) extend by 1 line when scrolling
#   -weird flashing glitch when shrinking screen in both x and y too fast
#   -crashes when resized too small too fast (sometimes)
#
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
    curses.curs_set(0) # set cursor to invisible
    render_windows()
    resize_screen()

    #main loop
    while True:
        curses.curs_set(0) # set cursor to invisible
        key = vigrscr.get_key() # wait for user input

        if key == curses.KEY_RESIZE:
            resize_screen()

        if key in commands.vigr_commands:
            commands.check_vigr_commands(key)
        elif key == ord(":"):
            # setup for : command
            windows.load_cmd(":")
            curses.curs_set(1)
            curses.echo()

            #usr input as string
            ex = vigrscr.get_ex()

            if curses.is_term_resized(curses.LINES, curses.COLS):
                resize_screen()
            elif ex == 'q':
                break # thank you have nice day
            else:
                commands.check_ex_commands(ex)

        render_windows() # apply changes
        # The changes are setup and applied starting next loop

#----------------------------------------------------------------------

def resize_screen():
    curses.update_lines_cols()
    commands.scale_dna(0) #updates the scale, will also update features
    render_windows()

#----------------------------------------------------------------------

# load_cmd is always the bottom row, other windows load from
# left to right in the order that they are loaded
def render_windows():
    # check if window is large enough
    if curses.LINES < 8 or curses.COLS < 60:
        return
    vigrscr.stdscr.noutrefresh()
    windows.load_strand()
    windows.load_dna()
    windows.load_main_window()
    windows.load_cmd(refresh_only = True) #keep the command line as is
    curses.doupdate()

#----------------------------------------------------------------------

curses.wrapper(main)
