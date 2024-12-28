#!/usr/bin/env python

import curses
import windows, functions

"""
TODO:   -implement a list of keystrokes and :* functions
        -implement filesize, sequence sizing, and scrolling
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
        act = stdscr.getch(curses.LINES-1,curses.COLS-5)

        if act == curses.KEY_RESIZE:
            curses.update_lines_cols()
            render_screen()

        if act == ord(":"):
            # setup for : command
            windows.load_cmd(":")
            curses.curs_set(1)
            curses.echo()
            cmd = stdscr.getstr(curses.LINES-1, 1).decode('utf-8')
            if cmd in functions.ex_cmds:
                run_it = functions.ex_cmds[cmd]
                run_it()

            elif cmd == chr(curses.KEY_RESIZE):
                curses.update_lines_cols()
                render_screen()

            elif cmd == 'q':
                break # thank you and have a good one


def render_screen():
    stdscr.noutrefresh()
    windows.load_strand()
    windows.load_dna()
    windows.load_cmd(refresh_only = True)


curses.wrapper(main)
