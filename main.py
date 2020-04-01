from flask import Flask, escape, request, render_template

app = Flask(__name__)

fr_0 = ["Nous", "allons", "au", "marche", "acheter", "des", "legumes"]
en_0 = ["We", "are", "going", "to", "the", "market", "to", "buy", "vegetables"]
corresps = [(0, 0), (1, [1, 2]), (2, [3, 4]), (3, 5), (4, [6, 7]), ([5, 6], 8)]
for i_group, corresp in enumerate(corresps):
    j_fr, j_en = corresp
    if isinstance(j_fr, list):
        for j in j_fr:
            fr_0[j] = [fr_0[j], i_group]
    else:
        fr_0[j_fr] = [fr_0[j_fr], i_group]
    if isinstance(j_en, list):
        for j in j_en:
            en_0[j] = [en_0[j], i_group]
    else:
        en_0[j_en] = [en_0[j_en], i_group]

text_fr = [fr_0]
text_en = [en_0]

@app.route('/')
def diff():
    return render_template("index.html", text_src=text_fr, text_tgt=text_en)
