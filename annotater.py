import curses


sent0 = "Le chat mange la souris ."
sent1 = "The cat eats the mouse ."


def tokenize(sent):
    return sent.split()


class Sentence:
    def __init__(self, words):
        self.words = words
        self.selected = 0

    def draw(self, win):
        win.clear()
        for word in self.words:
            win.addstr(word)
            win.addstr(" ")
        win.refresh()


def main(stdscr):
    stdscr.clear()
    stdscr.refresh()

    sentence = Sentence(tokenize(sent0))
    win = curses.newwin(1, 100, 0, 0)

    while True:
        sentence.draw(win)

        c = stdscr.getch()
        if c in (ord("q"), ord("Q")):
            break


curses.wrapper(main)
