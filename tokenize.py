# tokens
SPACE = "<sp>"
NOSPACE = "<nsp>"
NEWLINE = "<nl>"

TOKEN_HUMAN = {
        SPACE: " ",
        NOSPACE: "",
        NEWLINE: "\n",
}

TOKEN_NLP = {
        SPACE: " ",
        NOSPACE: "_",
        NEWLINE: "\n",
}

MANUAL_MAP = {
        " ": SPACE,
        "_": NOSPACE,
        "\n": NEWLINE,
}


def detokenize_human(tokens):
    def process(token):
        return TOKEN_HUMAN[token] if token in TOKEN_HUMAN else token
    return "".join(map(process, tokens))


def detokenize_nlp(tokens):
    def process(token):
        return TOKEN_NLP[token] if token in TOKEN_NLP else token
    return "".join(map(process, tokens))


def clear_tokens(tokens):
    return list(filter(lambda t: t not in TOKEN_HUMAN, tokens))


def tokenize_manually(s):
    tokens = []
    in_word = False
    for i, c in enumerate(s):
        if c in MANUAL_MAP:
            if in_word:
                tokens.append(s[start_word:i])
                in_word = False
            tokens.append(MANUAL_MAP[c])
        else:
            if not in_word:
                in_word = True
                start_word = i
    if in_word:
        tokens.append(s[start_word:])
    return tokens
