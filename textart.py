
#-----------------------------------------------------------------------
class TextArt:

    index = 1
    offset = 9999
    IS_ZOOM = False

    def __init__(self, text, file_name = False):
        if file_name:
            with open(text) as file_:
                self.lines = list(file_)
        else:
            self.lines = text.splitlines(keepends=True)
        self.text = ''.join(self.lines)
        self.h = len(self.lines)
        self.w = len(max(self.lines))

    def fill(self, max_y):
        expanded_lines = self.lines * (max_y // self.h + 1)
        expanded_lines[max_y - 1] = expanded_lines[max_y - 1].rstrip('\n')
        return(''.join(expanded_lines[:max_y]))


    def update_text(self, new_text, file_name = False):
        self.__init__(text = new_text, file_name = file_name)

    def is_zoom(self):
        self.IS_ZOOM = True

    def not_zoom(self):
        self.IS_ZOOM = False

#-----------------------------------------------------------------------

strand = TextArt("text_art.txt", file_name = True)
dna = TextArt("┠┨\n")

#-----------------------------------------------------------------------

