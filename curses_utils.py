import curses


# # initialize curses
# stdscr = curses.initscr()

class vigr_screen:

    stdscr = curses.initscr()

    def get_key(self) -> int:
        _key = self.stdscr.getch(curses.LINES-1, curses.COLS-5)
        return(_key)

    def get_ex(self) -> str:
        _ex = self.stdscr.getstr(curses.LINES-1, 1).decode('utf-8')
        return(_ex)

vigrscr = vigr_screen()
