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
        curses.init_pair(3*i + 3, curses.COLOR_BLUE, curses.COLOR_BLACK)

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
    """ Representation of a sequence of words/tokens, aimed at helping
    visualisation for processing (e.g tagging) in cli. Each token has a state:
    -- 0: normal: unprocessed so far
    -- 1: selected: undergoing processing
    -- 2: fixed: already processed
    Attr `active` represents a cursor position on the sequence, can be used to
    move around the sequence and update words status.
    """
    def __init__(self, words, words_status=None, active=0):
        self.words = words
        self.words_status = ([0 for _ in self.words] if words_status is None
                             else words_status)
        self.active = active

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

    def activate_closest_nofixed(self, idx):
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

    def unfix(self, *idxs):
        def _process(i_s):
            idx, s = i_s
            if idx in idxs:
                return 1 if s == 2 else s
            return s
        self.words_status = list(map(_process, enumerate(self.words_status)))

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


def update_pad(pad, sentence, color_map, active=False):
    pad.clear()
    for i, word in enumerate(sentence.words):
        color = color_map[sentence.status_name(sentence.words_status[i])
                          + "_active" * (i == sentence.active)
                          + "_waiting" * (not active and i == sentence.active)]
        pad.addstr(word, color)
        pad.addstr(" ")


def refresh_pad(pad, start_line, n_lines, pos_h, width):
    pad.noutrefresh(start_line, 0, pos_h, 0, pos_h + n_lines-1, width)


def main(stdscr, sentences, correspondance):
    stdscr.clear()
    stdscr.noutrefresh()

    max_display_height = 11
    s_idx = 0
    width = 80
    pads_sent = []
    heights = []
    for sentence in sentences:
        heights.append(sentence.char_len // width + 1)
        pads_sent.append(curses.newpad(heights[-1], width))
    display_heights = [min(h, max_display_height) for h in heights]
    win_select = curses.newwin(2, width, sum(display_heights) + 2, 0)
    win_map = curses.newwin(1, width, sum(display_heights) + 3 + len(sentences), 0)
    # todo: replace wins by pads

    color_map = get_color_map()
    cursor = 0  # char idx, for better moving

    while True:
        # draw
        for i, (sentence, pad, display_height) \
                in enumerate(zip(sentences, pads_sent, display_heights)):
            update_pad(pad, sentence, color_map=color_map, active=(s_idx == i))
            pad_height, _ = pad.getmaxyx()
            nrow_active = sentence.char_at_word(sentence.active) // width
            first_row = min(max(nrow_active - display_height // 2, 0),
                            pad_height - display_height)
            pos_h = i * (display_height+1)
            pad.noutrefresh(first_row, 0, pos_h, 0, pos_h + display_height - 1, width)

        win_select.clear()
        win_select.addstr(0, 0, "0: " + " ".join(sentences[0].selection()))
        win_select.addstr(1, 0, "1: " + " ".join(sentences[1].selection()))
        win_select.noutrefresh()

        map_cur = repr(correspondance.current)
        win_map.addstr(0, 0, "..." * (len(map_cur) > width) + map_cur[-(width - 4):])
        win_map.noutrefresh()

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

        curses.doupdate()

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
            sentence = sentences[s_idx]
            cursor = sentence.char_at_word(sentence.active)
        if c in (ord("K"), ord("J")):
            char_idx = sentence.char_at_word(sentence.active)
            s_idx = (s_idx + 1) % len(sentences)
            sentences[s_idx].activate_closest_nofixed(
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
                    sentence.activate_closest_nofixed(sentence.active)
        if c in (curses.KEY_BACKSPACE, ):
            try:
                selections_removed = correspondance.pop()
                for sentence, selection in zip(sentences, selections_removed):
                    sentence.clear_selection()
                    sentence.unfix(*selection)
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
