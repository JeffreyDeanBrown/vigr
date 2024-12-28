#!/usr/bin/env python

import curses
import windows

"""
TODO:   -implement a list of keystrokes and :* functions
        -implement filesize, sequence sizing, and scrolling
"""

# initialize curses
stdscr = curses.initscr()
curses.echo()
curses.curs_set(0)


def main(stdscr):

    curses.echo()
    render_screen()

    while True:
        curses.curs_set(0)

        act = stdscr.getch(curses.LINES-1,curses.COLS-5)

        if act == curses.KEY_RESIZE:
            curses.update_lines_cols()
            render_screen()
        if act == ord(":"):
            windows.load_cmd(":")
            curses.curs_set(1)
            curses.echo()
            cmd = stdscr.getstr(curses.LINES-1, 1).decode('utf-8')
            if cmd == 'l':
                windows.dna.update_text(new_text = "║\n")
                windows.load_dna()
            elif cmd == 's':
                windows.dna.update_text(new_text = "││\n")
                windows.load_dna()
            elif cmd == 'm':
                windows.dna.update_text("├┄┤\n")
                windows.load_dna()
            elif cmd == 'b':
                windows.dna.update_text("┣┅┅┅┫\n"\
                                        "┃   ┃\n")
                windows.load_dna()
            elif cmd == chr(curses.KEY_RESIZE):
                curses.update_lines_cols()
                render_screen()
            elif cmd == 'q':
                break


def render_screen():
    stdscr.noutrefresh()
    windows.load_strand()
    windows.load_dna()
    windows.load_cmd(refresh_only = True)


curses.wrapper(main)
