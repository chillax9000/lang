import json
import os

data_folder_path = os.path.join(os.path.dirname(__file__), "data")
data_path = os.path.join(data_folder_path, "data.json")
TEXTS = {}

if os.path.exists(data_path):
    with open(data_path) as f:
        TEXTS = json.load(f)


def get(id_):
    return TEXTS[id_] if id_ in TEXTS else None


def get_info(id_):
    return TEXTS[id_]["info"] if id_ in TEXTS else None


def get_all():
    for i, d in TEXTS.items():
        return i, d


def write_map(id_, lang, map_):
    TEXTS[id_][lang]["map"] = map_


def write_tokens(id_, lang, tokens):
    TEXTS[id_][lang]["tokens"] = tokens


def get_map(id_, lang):
    return TEXTS[id_][lang]["map"]


def get_tokens(id_, lang):
    return TEXTS[id_][lang]["tokens"]


def get_text(id_, lang):
    return TEXTS[id_][lang]["text"]


def get_entry(id_):
    return Entry.from_dict(TEXTS[id_])


def write_entry(id_, entry):
    TEXTS[id_] = entry.to_dict()


def commit():
    with open(data_path, "w") as f:
        json.dump(TEXTS, f)


class Text:
    def __init__(self, lang, str_, tokens=None):
        self.lang = lang
        self.str = str_
        self.tokens = tokens if tokens else []

    def set_tokens(self, tokens):
        self.tokens = tokens

    def to_dict(self):
        return {"text": self.str, "tokens": self.tokens}


class Entry:
    def __init__(self, text_src):
        self.lang_src = text_src.lang
        self.text_src = text_src
        self.texts = {text_src.lang: (text_src, None)}

    @property
    def langs(self):
        return tuple(self.texts)

    def add(self, text, map_=()):
        self.texts[text.lang] = (text, map_)

    def get(self, lang):
        return self.texts[lang]

    def get_text(self, lang):
        return self.get(lang)[0]

    def get_map(self, lang):
        return self.get(lang)[1]

    def set(self, lang, text=None, map_=None):
        text_old, map_old = self.texts[lang]
        self.texts[lang] = (text if text is not None else text_old,
                            map_ if map_ is not None else map_old)

    @classmethod
    def from_dict(cls, d):
        lang_src = d["info"]["src"]
        text_src = Text(lang_src, d["src"]["text"], d["src"]["tokens"])
        entry = cls(text_src)
        for lang, d_ in d.items():
            if lang not in ("info", "src"):
                entry.add(Text(lang, d_["text"], d_["tokens"]), d_["map"])
        return entry

    def to_dict(self):
        base = {"info": {"src": self.lang_src},
                "src": self.text_src.to_dict()}
        base.update({lang: {**text.to_dict(), "map": map_}
                     for lang, (text, map_) in self.texts.items() if map_ is not None})
        return base
