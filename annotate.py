import annotater
import data
import tempfile
import subprocess
import argparse

ID = "1"
LANG_TARGET = "en"


def get_entry():
    with open("text_fr.txt") as f:
        text = f.read()
    text_src = data.Text("fr", text)
    entry = data.Entry(text_src)
    with open("text_en.txt") as f:
        entry.add(data.Text("en", f.read()), ())
    return entry


def get_entry():
    return data.get_entry(ID)


def get_id():
    return 2


def tokenize_src(text):
    return text.split()


def tokenize_tgt(text):
    return text.split()


def ask_for_text(text=""):
    with tempfile.NamedTemporaryFile() as buffer:
        buffer_path = buffer.name

        with open(buffer_path, "w") as f:
            f.write(text)

        cmd = ["editor", buffer_path]
        subprocess.run(cmd)

        with open(buffer_path, "r") as f:
            text_out = f.read()

    return text_out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", default=None)
    parser.add_argument("--add", action="store_true")
    args = parser.parse_args()

    if args.id is not None:
        id_ = args.id
        entry = data.get_entry(id_)
        print(f"{entry.lang_src}: {entry.text_src.str}")
        lang_tgt = input("target language: ")
        if args.add and lang_tgt not in entry.langs:
            entry.add(data.Text(lang_tgt, ask_for_text()))
    else:
        id_ = get_id()
        entry = get_entry()
        lang_tgt = LANG_TARGET

    text_src = entry.text_src
    text_tgt = entry.get_text(lang_tgt)
    tokens_src = text_src.tokens
    tokens_tgt = text_tgt.tokens

    if not tokens_src:
        tokens_src = tokenize_src(text_src.str)
    if not tokens_tgt:
        tokens_tgt = tokenize_tgt(text_tgt.str)
    tokens_src, tokens_tgt, map_ = annotater.process_manually(
        tokens_src, tokens_tgt, entry.get_map(lang_tgt)
    )
    entry.text_src.set_tokens(tokens_src)
    entry.get_text(lang_tgt).set_tokens(tokens_tgt)
    entry.set(lang_tgt, map_=map_)

    if input("Save? [y/N]") in ("y", "Y"):
        data.write_entry(id_, entry)
        data.commit()
