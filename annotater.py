import curses
import collections

Colors = collections.namedtuple("Color", ["normal", "selected", "active",
                                "corresponding"])


def get_colors():
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    return Colors(
            normal=curses.color_pair(0),
            selected=curses.color_pair(1),
            active=curses.color_pair(2),
            corresponding=curses.color_pair(3),
    )


sent0 = "Le chat mange la souris ."
sent1 = "The cat eats the mouse ."


def tokenize(sent):
    return sent.split()


def find_first(xs, cond, fail_return):
    for i, x in enumerate(xs):
        if cond(x):
            return i, x
    return fail_return


class Sentence:
    def __init__(self, words, colors):
        self.words = words
        self.words_status = [0 for _ in self.words]  # 0: normal, 1: currently selected, 2: already corresponding
        self.active = 0
        self.colors = colors
        self.status_color = {
                0: self.colors.normal,
                1: self.colors.selected,
                2: self.colors.corresponding
        }

    def draw(self, win, active=False):
        win.clear()
        for i, word in enumerate(self.words):
            color = self.status_color[self.words_status[i]]
            if active and i == self.active:
                color = self.colors.active
            win.addstr(word, color)
            win.addstr(" ")
        win.refresh()

    def next(self):
        self.active = min(len(self.words), self.active + 1)

    def prev(self):
        self.active = max(0, self.active - 1)

    def next_nosel(self):
        i, _ = find_first(self.words_status[self.active+1:],
                          lambda status: status == 0,
                          (-1, None))
        self.active += i + 1

    def prev_nosel(self):
        idxs = [s for i, s in enumerate(self.words_status) if i < self.active]
        i, _ = find_first(idxs[::-1],
                          lambda status: status == 0,
                          (-1, None))
        self.active -= i + 1

    def add_to_selection(self, *idxs):
        for idx in idxs:
            if self.words_status[idx] < 2:
                self.words_status[idx] = (self.words_status[idx] + 1) % 2

    def clear_selection(self):
        def clear(s):
            return 0 if s == 1 else s
        self.words_status = list(map(clear, self.words_status))

    def fix_selection(self):
        def fix(s):
            return 2 if s == 1 else s
        self.words_status = list(map(fix, self.words_status))

    def selection(self):
        return [self.words[i] for i, s in enumerate(self.words_status) if s == 1]

    def selection_idxs(self):
        return [i for i, s in enumerate(self.words_status) if s == 1]


def main(stdscr):
    stdscr.clear()
    stdscr.refresh()

    sentences = [
        Sentence(tokenize(sent0), get_colors()),
        Sentence(tokenize(sent1), get_colors()),
    ]
    s_idx = 0

    win_sent0 = curses.newwin(1, 100, 0, 0)
    win_sent1 = curses.newwin(1, 100, 1, 0)
    win_sel = curses.newwin(2, 100, 3, 0)

    corresps = []

    while True:
        # draw
        for i, (sentence, win) in enumerate(zip(sentences,
                                                (win_sent0, win_sent1))):
            sentence.draw(win, active=(s_idx == i))

        win_sel.clear()
        win_sel.addstr(0, 0, " ".join(sentences[0].selection()) + " | " +
                       " ".join(sentences[1].selection()))
        win_sel.addstr(1, 0, repr(corresps))
        win_sel.refresh()

        # input
        sentence = sentences[s_idx]
        c = stdscr.getch()
        if c in (ord("q"), ord("Q")):
            break
        if c in (ord("l"), curses.KEY_RIGHT):
            sentence.next_nosel()
        if c in (ord("h"), curses.KEY_LEFT):
            sentence.prev_nosel()
        if c in (ord("L"), ):
            sentence.next()
        if c in (ord("H"), ):
            sentence.prev()
        if c in (ord("s"), ):
            sentence.add_to_selection(sentence.active)
        if c in (ord("c"), ):
            for sentence in sentences:
                sentence.clear_selection()
        if c in (ord("k"), ord("j")):
            s_idx = (s_idx + 1) % 2
        if c in (curses.KEY_ENTER, 10, 13):  # \n, \r
            corresps.append(
                (sentences[0].selection_idxs(), sentences[1].selection_idxs())
            )
            for sentence in sentences:
                sentence.fix_selection()


if __name__ == "__main__":
    curses.wrapper(main)
