
#-----------------------------------------------------------------------
class TextArt:

    index = 1
    offset = 9999
    is_zoom = False

    def __init__(self, text, file_name = False):
        """
        The text string passed to text will be used as the text art,
        unless file_name = True in which case it will open a text file
        with the name passed to text.
        """
        if file_name:
            with open(text) as file_:
                self.lines = list(file_)
        else:
            self.lines = text.splitlines(keepends=True)
        # text art is split into individual lines to determine the
        # height and maximum width of the text art
        self.text = ''.join(self.lines)
        self.h = len(self.lines)
        self.w = len(max(self.lines))

    def fill(self, max_y):
        """
        Repeates the text art over a number of lines, cutting the art
        short when the art does not fit evenly within the number
        of lines.
        Returns a single string delimited by new line characters.
        """
        expanded_lines = self.lines * (max_y // self.h + 1)
        # don't need a new line character on the last line
        expanded_lines[max_y - 1] = expanded_lines[max_y - 1].rstrip('\n')
        return(''.join(expanded_lines[:max_y]))


    def update_text(self, new_text, file_name = False):
        """
        used to change the text art. Useful when zooming in on
        the dna ladder and changing from a skinny ladder to a
        wider ladder. Args are the same as __init__
        """
        self.__init__(text = new_text, file_name = file_name)

#-----------------------------------------------------------------------

large_helix = TextArt("text_art.txt", file_name = True)
little_ladder = TextArt("┠┨\n")

#-----------------------------------------------------------------------

