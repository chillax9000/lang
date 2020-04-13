import argparse
import pprint
import operator
import re

import data

RE_LANG = re.compile(r"\[([a-z0-9-]*)\]")


def is_lang(s):
    match = RE_LANG.fullmatch(s)
    if match is not None:
        return True, match.group(1)
    return False, None


def read(file_path):
    """parse file formatted like:
        [lang0]
        text0 (multi-line)
        [lang1]
        ...
        into a tuple ((lang0, text0), ...)"""
    with open(file_path) as f:
        lang_texts = []
        lines = []

        try:  # find first language
            islang, lang = is_lang(next(f).strip())
            while not islang:
                islang, lang = is_lang(next(f).strip())
        except StopIteration:
            raise ValueError("Could not parse file: no language detected.")

        for line in f:
            islang, next_lang = is_lang(line.strip())
            if islang:
                if lines:
                    lang_texts.append((lang, "".join(lines)))
                lang = next_lang
                lines.clear()
            else:
                lines.append(line)
        if lines:
            lang_texts.append((lang, "".join(lines)))

    return tuple(lang_texts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--new", action="store_true")
    parser.add_argument("path")
    args = parser.parse_args()

    if args.new:
        try:
            lang_texts = read(args.path)
        except Exception as e:
            print(f"An error occured while reading {args.path}.")
            print(e)
            exit(1)
        lang, txt = lang_texts[0]
        print(f"Found texts for: {'/'.join(map(operator.itemgetter(0), lang_texts))}."
              " Using {lang} as src.")
        text_src = data.Text(lang, txt)
        entry = data.Entry(text_src)
        for lang, txt in lang_texts[1:]:
            entry.add(data.Text(lang, txt))
        new_id = data.add_entry(entry)
        pprint.pprint(entry.to_dict())
        print()
        if input("Save? [y/N]") in ("y", "Y"):
            data.commit()
            print(f"Saved new entry with id {new_id}")
