import annotater
import data
import tempfile
import subprocess
import argparse


def get_entry(args, dao):
    if args.id is not None:
        try:
            entry = dao.get_entry(args.id)
        except data.EntryNotFoundError:
            print(f"entry {args.id} not found")
            exit(0)
        print(f"{entry.lang_src}: {entry.text_src.str}")
        choices_str = "/".join(filter(lambda l: l != entry.lang_src, entry.langs))
        lang_tgt = input(f"target language (existing: {choices_str}):")
        if lang_tgt not in entry.langs:
            if args.add:
                entry.add(data.Text(lang_tgt, ask_for_text()))
            else:
                print(f"target language {lang_tgt} not found for entry "
                      "{args.id}. to add a new target, use the --add flag.")
            exit(0)

        def save(entry):
            dao.write_entry(args.id, entry)
    elif args.new:
        lang_src = input("source language: ")
        entry = data.Entry(data.Text(lang_src, ask_for_text()))
        lang_tgt = input("target language: ")
        entry.add(data.Text(lang_tgt, ask_for_text()))

        def save(entry):
            dao.add_entry(entry)
    else:
        print("Nothing to be done")
        exit(0)

    return entry, lang_tgt, save


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
    parser.add_argument("--new", action="store_true")
    args = parser.parse_args()

    entry, lang_tgt, save = get_entry(args, data.DAO)

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
    text_src.set_tokens(tokens_src)
    entry.get_text(lang_tgt).set_tokens(tokens_tgt)
    entry.set(lang_tgt, map_=map_)

    if input("Save? [y/N]") in ("y", "Y"):
        save(entry)
