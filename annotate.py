import annotater
import data


def tokenize_src(text):
    return text.split()


def tokenize_tgt(text):
    return text.split()


if __name__ == "__main__":
    id_ = "0"
    lang_target = "en"
    entry = data.get_entry(id_)
    text_src = entry.text_src
    text_tgt = entry.get_text(lang_target)
    tokens_src = text_src.tokens
    tokens_tgt = text_tgt.tokens
    if not tokens_src:
        tokens_src = tokenize_src(text_src.str)
    if not tokens_tgt:
        tokens_tgt = tokenize_tgt(text_tgt.str)
    tokens_src, tokens_tgt, map_ = annotater.process_manually(
        tokens_src, tokens_tgt, entry.get_map(lang_target)
    )
    entry.text_src.set_tokens(tokens_src)
    entry.get_text(lang_target).set_tokens(tokens_tgt)
    entry.set(lang_target, map_=map_)

    if input("Save? [y/N]") in ("y", "Y"):
        data.write_entry(id_, entry)
        data.commit()
