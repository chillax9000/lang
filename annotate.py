import annotater
import data


def tokenize(text):
    return text.split()


if __name__ == "__main__":
    id_ = "0"
    lang_target = "en"
    tokens_src = data.get_tokens(id_, "src")
    if not tokens_src:
        tokens_src = tokenize(data.get_text(id_, "src"))
    tokens_tgt = data.get_tokens(id_, lang_target)
    if not tokens_tgt:
        tokens_tgt = tokenize(data.get_text(id_, lang_target))
    map_ = data.get_map(id_, lang_target)
    tokens_src, tokens_tgt, map_ = \
        annotater.process_manually(tokens_src, tokens_tgt, map_)
    data.write_tokens(id_, "src", tokens_src)
    data.write_tokens(id_, lang_target, tokens_tgt)
    data.write_map(id_, lang_target, map_)

    if input("Save? [y/N]") in ("y", "Y"):
        data.commit()
