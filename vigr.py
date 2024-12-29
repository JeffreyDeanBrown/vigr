#!/usr/bin/env python

import curses
import windows, commands

"""
TODO:   -implement gg + G + \d*gg searching
        -implement subroutine for getting messages to user
        -add command history
        -layout window positions in WINDOWS comments and convert to constants
        -implement indexing + offset commands based on \d*\Ddb | \d*db format
        -implement keystroke scrolling + page scrolling
        -add major and minor axis lines to strand ruler + labels

FIXME:  -invalid escape sequence SyntaxWarning when :q
      WINDOWS:
        -figure out curses.LINES - 1 reasoning and fix comments
        -also, all the mess with offsets and -1 -2, etc
      COMMANDS:
        -can currently set scale to 0 (implement minimum dna offset)
"""

# initialize curses
stdscr = curses.initscr()
curses.echo()
curses.curs_set(0)


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
