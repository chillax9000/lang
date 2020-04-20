from flask import Flask, render_template
import operator
import collections
from data import DAO

app = Flask(__name__)


def apply_map(sent0, sent1, map_, line_n):
    def tag(sent, sent_n, map_):
        isent_to_tag = collections.defaultdict(lambda: "group-None")
        for igroup, isents in enumerate(map(operator.itemgetter(sent_n), map_)):
            for isent in isents:
                isent_to_tag[isent] = f"group-{line_n}-{igroup}"
        return [[word, isent_to_tag[isent]] for isent, word in enumerate(sent)]

    return tag(sent0, 0, map_), tag(sent1, 1, map_)


@app.route('/')
def diff():
    return "Hello"


@app.route("/<t_id>")
def text(t_id=None):
    entry = DAO.get_entry(t_id)
    if entry is None:
        return f"entry of id {t_id} not found", 404
    max_size = 80
    text_str = entry.text_src.str
    preview = text_str[:max_size] + "..." * (len(text_str) >= max_size)
    s = f"{entry.lang_src}: {preview}<br>"
    def li(lang): return f"<li><a href='/{t_id}/{lang}'>{lang}</a></li>"
    l = "<ul>" + "".join(map(li, entry.target_langs)) + "</ul>"
    return s + l


@app.route("/api/<t_id>")
def api_json(t_id=None):
    return DAO.get_entry(t_id).to_dict()


@app.route("/<t_id>/<target>")
def compare_line(target=None, t_id=None):
    entry = DAO.get_entry(t_id)
    tokens_src = [entry.text_src.tokens]
    tokens_tgt = [entry.get_text(target).tokens]
    maps = [entry.get_map(target)]
    text_src = []
    text_tgt = []
    for line, (sent0, sent1, map_) in enumerate(zip(tokens_src,
                                                    tokens_tgt,
                                                    maps)):
        tagged_0, tagged_1 = apply_map(sent0, sent1, map_, line)
        text_src.append(tagged_0)
        text_tgt.append(tagged_1)
    return render_template("index.html", text_src=text_src, text_tgt=text_tgt)


@app.route("/<t_id>/<target>/sided")
def compare_side(target=None, t_id=None):
    entry = DAO.get_entry(t_id)
    tokens_src = [entry.text_src.tokens]
    tokens_tgt = [entry.get_text(target).tokens]
    maps = [entry.get_map(target)]
    text_src = []
    text_tgt = []
    for line, (sent0, sent1, map_) in enumerate(zip(tokens_src,
                                                    tokens_tgt,
                                                    maps)):
        tagged_0, tagged_1 = apply_map(sent0, sent1, map_, line)
        text_src.append(tagged_0)
        text_tgt.append(tagged_1)
    return render_template("sided.html", text_src=text_src, text_tgt=text_tgt)
