#!/usr/bin/env python

import curses, sys
import windows, commands
from curses_utils import vigrscr

#-----------------------------------------------------------------------

# TODO:

#   -reformat commands.py to make it easier to see commands
#   -:h[elp] function and $ vigr.py -h[elp]
#   -setup installation script with venv stuff
#   -use the term "contig" instead of seqs when choosing contigs
#   -type removal
#   -auto spacing, finding biggest label space, name cutoff
#   -selecting features (mouse, arrow keys) and writing that name over others
#   -setup a way to warn the user when the window is too small to list
#    all of the seqs in :seqs (soon to be contigs in :contigs)
#    as currently it just crashes when the window is too small
#
#   PRE-RELEASE CHECKLIST:
#   -reformat like you mean it
#   -make sure ex command names make sense, add shortcuts
#   -add docstring to everything
#   -annotate function types + argument types
#   - :select all & children none
#   -clear out all FIXMEs
#
#   POTENTIAL ADDITIONS:
#   -also show parent when showing children & label screen w/parent name
#   -add major and minor axis lines to strand ruler + labels
#   -implement subroutine for getting messages to user
#   -parse .gff files which have fasta appended on the end
#
#   WHEN I SOMEHOW GET A LOT OF FREE TIME AND NEED SOMETING TO DO:
#   -implement tab autocomplete + ex_command history scrolling
#   -search using / + regex, g/re/p across all sequences in gff
#   -implement browsing or comparing multiple parent/children trees

# FIXME:

#   COMMANDS.PY:
#   -ignores resize key if waiting for an ex command
#   -some features are resetting their cols after already being rendered

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
    render_screen()

    #main loop
    while True:
        curses.curs_set(0) # set cursor to invisible
        key = vigrscr.get_key() # wait for user input

        if key in commands.vigr_commands:
            commands.check_vigr_commands(key)
        elif key == ord(":"):
            # setup for : command
            windows.load_cmd(":")
            curses.curs_set(1)
            curses.echo()

            #usr input as string
            ex = vigrscr.get_ex()

            if ex == 'q':
                break # thank you have nice day
            else:
                commands.check_ex_commands(ex)
        render_screen() # apply changes
        # The changes are setup and applied starting next loop

#----------------------------------------------------------------------

# load_cmd is always the bottom row, other windows load from
# left to right in the order that they are loaded
def render_screen():
    #update to current terminal size
    curses.update_lines_cols()
    commands.scale_dna(0) # update dna scale

    # check if window is large enough
    if curses.LINES < 6:
       sys.exit("VIGR ERROR: Window Too Short!\n"\
             "   minimum window height is 6 lines.")
    vigrscr.stdscr.noutrefresh()

    # load the windows
    windows.load_strand()
    windows.load_dna()
    windows.load_main_window()
    windows.load_cmd(refresh_only = True) #keep the command line as is
    curses.doupdate()


curses.wrapper(main)
