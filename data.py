import json
import os


data_path = os.path.join(os.path.dirname(__file__), "data.json")
with open(data_path) as f:
    SENTENCES = json.load(f)


def get(id_):
    return SENTENCES[id_] if id_ in SENTENCES else None


def get_info(id_):
    return SENTENCES[id_]["info"] if id_ in SENTENCES else None


def get_all():
    for i, d in SENTENCES.items():
        return i, d


def write_map(id_, lang, map_):
    SENTENCES[id_][lang]["map"] = map_


def write_tokens(id_, lang, tokens):
    SENTENCES[id_][lang]["tokens"] = tokens


def get_map(id_, lang):
    return SENTENCES[id_][lang]["map"]


def get_tokens(id_, lang):
    return SENTENCES[id_][lang]["tokens"]


def get_text(id_, lang):
    return SENTENCES[id_][lang]["text"]


def commit():
    with open(data_path, "w") as f:
        json.dump(SENTENCES, f)
