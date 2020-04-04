import annotater
import data

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


def tokenize_src(text):
    return text.split()


def tokenize_tgt(text):
    return text.split()


if __name__ == "__main__":
    entry = get_entry()
    text_src = entry.text_src
    text_tgt = entry.get_text(LANG_TARGET)
    tokens_src = text_src.tokens
    tokens_tgt = text_tgt.tokens

    if not tokens_src:
        tokens_src = tokenize_src(text_src.str)
    if not tokens_tgt:
        tokens_tgt = tokenize_tgt(text_tgt.str)
    tokens_src, tokens_tgt, map_ = annotater.process_manually(
        tokens_src, tokens_tgt, entry.get_map(LANG_TARGET)
    )
    entry.text_src.set_tokens(tokens_src)
    entry.get_text(LANG_TARGET).set_tokens(tokens_tgt)
    entry.set(LANG_TARGET, map_=map_)

    if input("Save? [y/N]") in ("y", "Y"):
        data.write_entry(ID, entry)
        data.commit()