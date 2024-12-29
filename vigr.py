#!/usr/bin/env python

import curses
import windows, commands

"""
TODO:   -make scaling relative to filesize
        -add command history
        -add constants to represent window sizes and stuff
"""

# initialize curses
stdscr = curses.initscr()
curses.echo()
curses.curs_set(0)


def main(stdscr):
    # initial setup
    curses.echo()
    render_screen()

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
    windows.load_strand()
    windows.load_dna()
    windows.load_cmd(refresh_only = True)


curses.wrapper(main)
