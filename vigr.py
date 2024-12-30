#!/usr/bin/env python

import curses
import windows, commands

#-----------------------------------------------------------------------

"""
TODO:   -implement gg + G + \d*gg searching
        -layout window positions in text file and convert to constants
        -add 9-char value support to strand (same as dna)
        -add temporary file-loading commands
        -add major and minor axis lines to strand ruler + labels
        -add docstring to everything
        -make nucleotide-scale the minimum offset (& max index = filesize - min.offset)
        -implement subroutine for getting messages to user
        -add command history + scrolling
        -implement keystroke scrolling + page scrolling
        -type annotate functions
        -implement gff file + fasta file reading
        -become a master at [] indexing

FIXME:  -invalid escape sequence SyntaxWarning when :q
      WINDOWS:
        -figure out curses.LINES - 1 reasoning and fix comments
        -also, all the mess with offsets and -1 -2, etc
      COMMANDS:
        -make comma and bp parsing DRY
"""

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
    render_screen()

    #main loop
    while True:
        # wait for user input
        curses.curs_set(0)
        # usr input as decimal value
        key = stdscr.getch(curses.LINES-1,curses.COLS-5)

        if key == curses.KEY_RESIZE:
            curses.update_lines_cols()
            render_screen()

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
                curses.update_lines_cols()
                render_screen()

            elif ex == 'q':
                break # thank you have a good one

            else:
                commands.check_ex_commands(ex)



def render_screen():
    stdscr.noutrefresh()
    windows.load_dna()
    windows.load_strand()
    windows.load_cmd(refresh_only = True)


curses.wrapper(main)
