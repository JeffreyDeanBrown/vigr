#!/usr/bin/env python

import curses, sys
import windows, commands, files

#-----------------------------------------------------------------------

# TODO:

#   FUNCTIONALITY:
#   -implement annotation window with basic functionality
#   -get together a basic mock-up of a gff (just start/stop positions)
#   -implement full gff file + fasta file parsing (sequence selection, etc)
#
#   FEATURES:
#   -implement gg + G + \d*gg searching
#   -add major and minor axis lines to strand ruler + labels
#   -add docstring to everything
#   -implement subroutine for getting messages to user
#   -add command history + scrolling
#   -implement keystroke scrolling + page scrolling
#   -annotate function types + argument types
#   -become a master at [] indexing
#   -implement "minimum mode" where scale stays at 1bp per line (even when resized)
#   -when the scale is small enough, somehow change ruler annotations to smaller scale

# FIXME:

#   COMMANDS.PY:
#   -make comma and bp parsing DRY
#   -cannot set_dna with comma delimited + kbp/mbp labeled (bp works though)

#-----------------------------------------------------------------------

# initialize curses
stdscr = curses.initscr()
curses.echo()
curses.curs_set(0)


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
        # apply last change
        render_screen()
        # wait for user input
        curses.curs_set(0)
        # usr input as decimal value
        key = stdscr.getch(curses.LINES-1,curses.COLS-5)

        if key == curses.KEY_RESIZE:
            resize_vigr()

        elif key in commands.vigr_commands:
            pass

        elif key == ord(":"):
            # setup for : command
            windows.load_cmd(":")
            curses.curs_set(1)
            curses.echo()

            #usr input as string
            ex = stdscr.getstr(curses.LINES-1, 1).decode('utf-8')

            if ex == chr(curses.KEY_RESIZE):
                resize_vigr()

            elif ex == 'q':
                break # thank you have nice day

            else:
                commands.check_ex_commands(ex)


# load_cmd is always the bottom row, other windows load from
# left to right in the order that they are loaded
def render_screen():
    if curses.LINES < 6:
       sys.exit("VIGR ERROR: Window Too Short!\n"\
             "   minimum window height is 6 lines.")
    stdscr.noutrefresh()
    windows.load_strand()
    windows.load_dna()
    windows.load_presentation()
    windows.load_cmd(refresh_only = True)
    curses.doupdate()

def resize_vigr():
    curses.update_lines_cols()
    commands.scale_dna(0) # update dna scale
    render_screen()


curses.wrapper(main)
