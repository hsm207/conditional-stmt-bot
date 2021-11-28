import spacy
from spacy.matcher import Matcher
from spacy.tokens import Token

nlp = spacy.load("en_core_web_md")
matcher = Matcher(nlp.vocab)
Token.set_extension("mytext", default=None, force=True)


DOMAIN = ["temperature", "light", "door", "heater", "window", "music"]


def extract_then_part(domain_token, if_token):
    doc = domain_token.doc
    verb_token = domain_token.head

    while verb_token.pos_ != "VERB":
        verb_token = verb_token.head

    if not verb_token.is_sent_start:
        return doc[verb_token.i :]
    else:
        return doc[: if_token.i]


def extract_if_part(verb_token, if_token):
    doc = verb_token.doc

    if if_token.is_sent_start:
        return doc[: verb_token.i]
    else:
        return doc[if_token.i :]


def get_condition_token(doc):
    if_token = [t for t in doc if t.pos_ == "SCONJ"]
    assert len(if_token) == 1, "Only 1 condition per utterance is allowed"
    return if_token[0]


def parse_conditional_statement(doc):
    domain_tokens = [t for t in doc if t.lemma_ in DOMAIN]
    assert (
        len(domain_tokens) == 1
    ), f"Cannot recognize any objects from the utterance: {doc.text}"
    domain_token = domain_tokens[0]

    if_token = get_condition_token(doc)

    if_stmt = extract_if_part(domain_token.head, if_token)
    if_stmt = clean_statement(if_stmt)

    then_stmt = extract_then_part(domain_token, if_token)
    then_stmt = clean_statement(then_stmt)

    return (if_stmt, then_stmt)


def truncate_doc(doc):
    ending_pos = ["VERB", "NOUN", "ADJ", "ADV"]
    root = get_root(doc)

    if doc[-1].head == root and doc[-1].lower_ == "then":
        doc = doc[:-1]

    while doc[-1].pos_ not in ending_pos:
        doc = doc[:-1]

    return doc


def adj_pronoun(doc):
    patterns = [[{"LOWER": "i", "POS": "PRON"}]]

    for token in doc:
        token._.mytext = token.text

    def f(matcher, doc, i, matches):
        match_id, start, end = matches[i]
        doc[start]._.mytext = "you"

        if doc[start + 1].pos_ == "AUX":
            doc[start + 1]._.mytext = "are"

    matcher.add("adj_I_pronoun", patterns, on_match=f)

    matcher(doc)

    return nlp.make_doc(" ".join(token._.mytext for token in doc))


def clean_statement(span):
    doc = span.as_doc()
    doc = truncate_doc(doc)
    doc = adj_pronoun(doc)

    return doc


def get_root(doc):
    root = [token for token in doc if token.head == token]
    return root[0]


def is_conditional_statement(doc):
    root = get_root(doc)
    children = root.children

    return any(token for token in children if token.dep_ == "advcl")


def parse_device_instruction(utterance):
    doc = nlp(utterance)
    if_stmt = None
    then_stmt = None

    if is_conditional_statement(doc):
        if_stmt, then_stmt = parse_conditional_statement(doc)
        if_stmt = str(if_stmt)
        then_stmt = str(then_stmt)

    else:
        then_stmt = str(adj_pronoun(doc))

    return if_stmt, then_stmt
