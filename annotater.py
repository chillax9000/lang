import curses


def get_color_map():
    color_base = {
            "normal": curses.COLOR_WHITE,
            "selected": curses.COLOR_GREEN,
            "fixed": curses.COLOR_RED,
    }

    color_map = {}
    for i, (name, color) in enumerate(color_base.items()):
        curses.init_pair(2*i + 1, color, curses.COLOR_BLACK)
        curses.init_pair(2*i + 2, curses.COLOR_BLACK, color)

        color_map[name] = curses.color_pair(2*i + 1)
        color_map[f"{name}_active"] = curses.color_pair(2*i + 2)

    return color_map


def tokenize(sent):
    return sent.split()


def find_first(xs, cond, fail_return):
    for i, x in enumerate(xs):
        if cond(x):
            return i, x
    return fail_return


class Sentence:
    def __init__(self, words):
        self.words = words
        self.words_status = [0 for _ in self.words]
        self.active = 0

    @staticmethod
    def status_name(i):
        return {
            0: "normal",
            1: "selected",
            2: "fixed",
        }[i]

    def draw(self, win, color_map, active=False):
        win.clear()
        for i, word in enumerate(self.words):
            is_active = active and i == self.active
            color = color_map[self.status_name(self.words_status[i])
                              + "_active" * is_active]
            win.addstr(word, color)
            win.addstr(" ")
        win.refresh()

    def next(self):
        self.active = min(len(self.words), self.active + 1)

    def prev(self):
        self.active = max(0, self.active - 1)

    def next_nofixed(self):
        i, _ = find_first(self.words_status[self.active+1:],
                          lambda status: status < 2,
                          (-1, None))
        self.active += i + 1

    def prev_nofixed(self):
        idxs = [s for i, s in enumerate(self.words_status) if i < self.active]
        i, _ = find_first(idxs[::-1],
                          lambda status: status < 2,
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


def main(stdscr, sentences, corresps):
    stdscr.clear()
    stdscr.refresh()

    s_idx = 0

    win_sent0 = curses.newwin(1, 100, 0, 0)
    win_sent1 = curses.newwin(1, 100, 1, 0)
    win_sel = curses.newwin(2, 100, 3, 0)

    color_map = get_color_map()

    while True:
        # draw
        for i, (sentence, win) in enumerate(zip(sentences,
                                                (win_sent0, win_sent1))):
            sentence.draw(win, color_map=color_map, active=(s_idx == i))

        win_sel.clear()
        win_sel.addstr(0, 0, " ".join(sentences[0].selection()) + " | " +
                       " ".join(sentences[1].selection()))
        win_sel.addstr(1, 0, repr(corresps))
        win_sel.refresh()

        # input
        sentence = sentences[s_idx]
        c = stdscr.getch()

        ## leaving
        if c in (ord("q"), ord("Q")):
            break

        ## moving
        if c in (ord("l"), curses.KEY_RIGHT):
            sentence.next_nofixed()
        if c in (ord("h"), curses.KEY_LEFT):
            sentence.prev_nofixed()
        if c in (ord("L"), ):
            sentence.next()
        if c in (ord("H"), ):
            sentence.prev()
        if c in (ord("k"), ord("j")):
            cur_active = sentence.active
            s_idx = (s_idx + 1) % 2
            sentences[s_idx].active = cur_active

        ## selecting
        if c in (ord("s"), ):
            sentence.add_to_selection(sentence.active)
        if c in (ord("c"), ):
            for sentence in sentences:
                sentence.clear_selection()
        if c in (curses.KEY_ENTER, 10, 13):  # \n, \r
            corresps.append(
                (sentences[0].selection_idxs(), sentences[1].selection_idxs())
            )
            for sentence in sentences:
                sentence.fix_selection()


def tag_manually(sentences, corresps):
    if isinstance(corresps, tuple):
        corresps = list(corresps)
    curses.wrapper(lambda stdscr: main(stdscr, sentences, corresps))
    return corresps


if __name__ == "__main__":
    sent0 = "Le chat mange la souris ."
    sent1 = "The cat eats the mouse ."
    sentences = [
        Sentence(tokenize(sent0)),
        Sentence(tokenize(sent1)),
    ]

    corresps = tag_manually(sentences, [])

    print(corresps)
    _ = input()
