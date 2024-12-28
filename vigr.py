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
                dna = windows.TextArt("║\n")
                windows.load_dna(dna)
            elif cmd == 's':
                dna = windows.TextArt("││\n")
                windows.load_dna(dna)
            elif cmd == 'm':
                dna = windows.TextArt("├┄┤\n")
                windows.load_dna(dna)
            elif cmd == 'b':
                dna = windows.TextArt("┣┅┅┅┫\n"\
                              "┃   ┃\n")
                windows.load_dna(dna)
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
