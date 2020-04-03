from flask import Flask, escape, request, render_template
import operator
import collections
import data

app = Flask(__name__)

tokenized_sents_src = [
        ["Aujourd'hui", ",", "il", "fait", "beau", "."],
        ["Nous", "allons", "au", "marche", "acheter", "des", "legumes", "."],
]
tokenized_sents_tgt = [
        ["The", "weather", "is", "nice", "today", "."],
        ["We", "are", "going", "to", "the", "market", "to", "buy", "vegetables", "."],
]
maps = [
        ((0, 4), ([2, 3, 4], [0, 1, 2, 3])),
        ((0, 0), (1, [1, 2]), (2, [3, 4]), (3, 5), (4, [6, 7]), ([5, 6], 8)),
]


def apply_map(sent0, sent1, map_, line_n):
    def listify(t):  # (int, [int], ...) -> ([int], [int], ...)
        def listify_item(x):
            return [x] if isinstance(x, int) else x
        return tuple(map(listify_item, t))

    corresps = tuple(map(listify, map_))

    def tag(sent, sent_n, map_):
        isent_to_tag = collections.defaultdict(lambda: "group-None")
        for igroup, isents in enumerate(map(operator.itemgetter(sent_n), map_)):
            for isent in isents:
                isent_to_tag[isent] = f"group-{line_n}-{igroup}"
        return [[word, isent_to_tag[isent]] for isent, word in enumerate(sent)]

    return tag(sent0, 0, corresps), tag(sent1, 1, corresps)


text_src = []
text_tgt = []
for line, (sent0, sent1, corresps) in enumerate(zip(tokenized_sents_src,
                                                    tokenized_sents_tgt,
                                                    maps)):
    tagged_0, tagged_1 = apply_map(sent0, sent1, corresps, line)
    text_src.append(tagged_0)
    text_tgt.append(tagged_1)


@app.route('/')
def diff():
    return render_template("index.html", text_src=text_src, text_tgt=text_tgt)


@app.route("/<t_id>/<target>")
def text(target=None, t_id=None):
    tokens_src = [data.get_tokens(t_id, "src")]
    tokens_tgt = [data.get_tokens(t_id, target)]
    maps = [data.get_map(t_id, target)]
    text_src = []
    text_tgt = []
    for line, (sent0, sent1, map_) in enumerate(zip(tokens_src,
                                                    tokens_tgt,
                                                    maps)):
        tagged_0, tagged_1 = apply_map(sent0, sent1, map_, line)
        text_src.append(tagged_0)
        text_tgt.append(tagged_1)
    return render_template("index.html", text_src=text_src, text_tgt=text_tgt)
