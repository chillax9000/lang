import curses
import tempfile
import subprocess


def get_color_map():
    color_base = {
            "normal": curses.COLOR_WHITE,
            "selected": curses.COLOR_GREEN,
            "fixed": curses.COLOR_RED,
    }

    color_map = {}
    for i, (name, color) in enumerate(color_base.items()):
        curses.init_pair(3*i + 1, color, curses.COLOR_BLACK)
        curses.init_pair(3*i + 2, curses.COLOR_BLACK, color)
        curses.init_pair(3*i + 3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        color_map[name] = curses.color_pair(3*i + 1)
        color_map[f"{name}_active"] = curses.color_pair(3*i + 2)
        color_map[f"{name}_active_waiting"] = curses.color_pair(3*i + 3)

    return color_map


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

    @property
    def char_len(self):
        return sum(list(map(lambda w: len(w) + 1, self.words)))

    @staticmethod
    def status_name(i):
        return {
            0: "normal",
            1: "selected",
            2: "fixed",
        }[i]

    def set_status(self, idx, status):
        self.words_status[idx] = status

    def activate_closest_selectable(self, idx):
        if idx >= len(self.words):
            idx = len(self.words) - 1
        if self.words_status[idx] < 2:
            self.activate(idx)
        else:
            idx_next = self.next_nofixed(idx)
            idx_prev = self.prev_nofixed(idx)
            if idx - idx_prev < idx_next - idx:
                self.activate(idx_prev)
            else:
                self.activate(idx_next)

    def activate(self, idx):
        self.active = idx

    def next(self, idx=None):
        idx = self.active if idx is None else idx
        return min(len(self.words), idx + 1)

    def prev(self, idx=None):
        idx = self.active if idx is None else idx
        return max(0, idx - 1)

    def next_nofixed(self, idx=None):
        idx = self.active if idx is None else idx
        i, _ = find_first(self.words_status[idx + 1:],
                          lambda status: status < 2,
                          (-1, None))
        return idx + i + 1

    def prev_nofixed(self, idx=None):
        idx = self.active if idx is None else idx
        idxs = [s for i, s in enumerate(self.words_status) if i < idx]
        i, _ = find_first(idxs[::-1],
                          lambda status: status < 2,
                          (-1, None))
        return idx - i - 1

    def add_to_selection(self, *idxs):
        for idx in idxs:
            if self.words_status[idx] < 2:
                self.words_status[idx] = (self.words_status[idx] + 1) % 2

    def clear_selection(self):
        def _process(s):
            return 0 if s == 1 else s
        self.words_status = list(map(_process, self.words_status))

    def fix_selection(self):
        def _process(s):
            return 2 if s == 1 else s
        self.words_status = list(map(_process, self.words_status))

    def selection(self):
        return [self.words[i] for i, s in enumerate(self.words_status) if s == 1]

    def selection_idxs(self):
        return [i for i, s in enumerate(self.words_status) if s == 1]

    def word_at_char(self, char_idx):
        total = 0
        for i, word in enumerate(self.words):
            total += len(word) + 1
            if total > char_idx:
                return i
        return len(self.words) - 1

    def char_at_word(self, word_idx):
        return sum(list(map(lambda w: len(w) + 1, self.words[:word_idx])))

    def split(self):
        text = " ".join(self.words)
        with tempfile.NamedTemporaryFile() as buffer:
            buffer_path = buffer.name

            with open(buffer_path, "w") as f:
                f.write(text)

            cmd = ["editor", buffer_path]
            subprocess.run(cmd)

            with open(buffer_path, "r") as f:
                text_out = f.read()

        words = text_out.split()
        if self.words != words:
            self.words = words
            self.words_status = [0 for _ in self.words]
            return True
        return False


class Correspondance:
    def __init__(self, corresps):
        self.source = tuple(corresps)
        self._current = list(self.source)

    @property
    def current(self):
        return tuple(self._current)

    def restore(self):
        self._current = list(self.source)

    def clear(self):
        self._current = []

    def pop(self):
        return self._current.pop()

    def add(self, value):
        self._current.append(value)


def draw(win, sentence, color_map, active=False):
    win.clear()
    for i, word in enumerate(sentence.words):
        color = color_map[sentence.status_name(sentence.words_status[i])
                          + "_active" * (i == sentence.active)
                          + "_waiting" * (not active and i == sentence.active)]
        win.addstr(word, color)
        win.addstr(" ")
    win.refresh()


def main(stdscr, sentences, correspondance):
    stdscr.clear()
    stdscr.refresh()

    s_idx = 0
    width = 100
    windows = []
    line = 0
    for sentence in sentences:
        height = sentence.char_len // width + 1
        windows.append(curses.newwin(height, width, line, 0))
        line += height
    win_sel = curses.newwin(2, width, line, 0)

    color_map = get_color_map()
    cursor = 0

    while True:
        # draw
        for i, (sentence, win) in enumerate(zip(sentences,
                                                (windows[0], windows[1]))):
            draw(win, sentence, color_map=color_map, active=(s_idx == i))

        win_sel.clear()
        win_sel.addstr(0, 0, " ".join(sentences[0].selection()) + " | " +
                       " ".join(sentences[1].selection()))
        map_cur = repr(correspondance.current)
        win_sel.addstr(1, 0, map_cur[:width - 4] + "..." * (len(map_cur) > width))
        win_sel.refresh()

        def down(cursor, width, n_chars):
            next_cursor = cursor + width
            if next_cursor < n_chars:
                return next_cursor
            return cursor

        def up(cursor, width):
            next_cursor = cursor - width
            if next_cursor >= 0:
                return next_cursor
            return cursor

        # input
        sentence = sentences[s_idx]
        c = stdscr.getch()

        ## leaving
        if c in (ord("q"), ord("Q")):
            break

        ## moving
        if c in (ord("l"), curses.KEY_RIGHT):
            sentence.activate(sentence.next_nofixed())
            cursor = sentence.char_at_word(sentence.active)
        if c in (ord("h"), curses.KEY_LEFT):
            sentence.activate(sentence.prev_nofixed())
            cursor = sentence.char_at_word(sentence.active)
        if c in (ord("L"), ):
            sentence.activate(sentence.next())
            cursor = sentence.char_at_word(sentence.active)
        if c in (ord("H"), ):
            sentence.activate(sentence.prev())
            cursor = sentence.char_at_word(sentence.active)
        if c in (ord("j"), ):
            cursor = down(cursor, width, sentence.char_len)
            sentence.activate(sentence.word_at_char(cursor))
        if c in (ord("k"), ):
            cursor = up(cursor, width)
            sentence.activate(sentence.word_at_char(cursor))
        if c in (ord("\t"), ):
            s_idx = (s_idx + 1) % len(sentences)
        if c in (ord("K"), ord("J")):
            char_idx = sentence.char_at_word(sentence.active)
            s_idx = (s_idx + 1) % len(sentences)
            sentences[s_idx].activate_closest_selectable(
                sentences[s_idx].word_at_char(char_idx))

        ## selecting
        if c in (ord("s"), ):
            sentence.add_to_selection(sentence.active)
        if c in (ord("c"), ):
            for sentence in sentences:
                sentence.clear_selection()
        if c in (curses.KEY_ENTER, 10, 13):  # \n, \r
            selections = (sentences[0].selection_idxs(),
                          sentences[1].selection_idxs())
            if selections[0] or selections[1]:
                correspondance.add(selections)
                for sentence in sentences:
                    sentence.fix_selection()
                    sentence.activate_closest_selectable(sentence.active)
        if c in (curses.KEY_BACKSPACE, ):
            try:
                selections_removed = correspondance.pop()
                for sentence, selection in zip(sentences, selections_removed):
                    sentence.clear_selection()
                    sentence.add_to_selection(selection)
            except IndexError:
                pass

        ## tokenizing
        if c in (ord("i"), ):
            changed = sentence.split()
            if changed:
                for sentence in sentences:
                    sentence.words_status = [0 for _ in sentence.words]
                correspondance.clear()


def process_manually(tokens0, tokens1, map_):
    sentences = [
        Sentence(tokens0),
        Sentence(tokens1)
    ]
    for corresp in map_:
        for selection, sentence in zip(corresp, sentences):
            sentence.add_to_selection(*selection)
            sentence.fix_selection()
    correspondance = Correspondance(map_)

    curses.wrapper(lambda stdscr: main(stdscr, sentences, correspondance))

    return sentences[0].words, sentences[1].words, correspondance.current


if __name__ == "__main__":
    def tokenize(sent):
        return sent.split()

    inp0 = "Hier , le chat a mangé la souris verte ."
    inp1 = "Yesterday , the cat ate the green mouse ."
    tokens0 = tokenize(inp0)
    tokens1 = tokenize(inp1)

    map_ = (([2, 3], [2, 3]), )

    tokens0, tokens1, new_corresps = \
        tuple(process_manually(tokens0, tokens1, map_))

    print(tokens0)
    print(tokens1)
    print(new_corresps)
