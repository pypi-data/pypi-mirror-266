"""
Routines to turn text into tokens suitable as graph nodes.
"""
from itertools import chain
import re
import logging

import pandas as pd

from ..misc import _try_import

spacy = _try_import("spacy")
compile_infix_regex = _try_import("spacy.util").compile_infix_regex
phrases = _try_import("gensim.models.phrases")

logger = logging.getLogger(__name__)


def process_token_sources(token_sources, to_doc=None):
    to_doc = tokens_to_doc if to_doc is None else to_doc
    return token_sources.applymap(to_doc, na_action="ignore").agg(
        lambda row: [sen for doc in row.dropna() for sen in doc], axis=1
    )


def process_text_sources(text_sources, language=None, ngrams=3, stop_words="language"):
    nlp = get_nlp(language or "en")
    if (stop_words == "language") or (stop_words is True):
        stop_words = nlp.Defaults.stop_words
    elif not stop_words:
        stop_words = {}
    else:
        stop_words = {*stop_words}

    docs = text_to_tokens(text_sources, nlp)

    translate_ngrams = make_translate_ngrams(docs, ngrams=ngrams)
    docs = docs.map(translate_ngrams)

    filter_tokens = make_filter_tokens(stop_words=stop_words)
    docs = docs.map(filter_tokens)

    return docs


def get_nlp(language_code):
    """
    TODO: generalize correction to infixes
    """
    nlp = spacy.blank(language_code)
    nlp.add_pipe("sentencizer")
    if language_code == "en":
        infixes = nlp.Defaults.infixes.copy()
        suffixes = nlp.Defaults.suffixes.copy()
        # do not split on simple hyphen: hot-dog
        old_part = r"(?:-|–|—|--|---|——|~)"
        new_part = old_part.replace(r":-|", r":")
        infixes[-2] = infixes[-2].replace(old_part, new_part)
        # split on relation followed by numeral: value:23 number>3 x/y
        spot = infixes[-1].rindex("[:<>=/](?=[")
        infixes[-1] = infixes[-1][: spot + 11] + "0-9" + infixes[-1][spot + 11 :]
        # split on suffix square bracket numeric citations: cite work[1,13]
        old_part = r"\."
        new_part = r"(?:\[[0-9][0-9,]*\])?" + old_part
        suffixes[-1] = suffixes[-1].replace(old_part, new_part)
        suffixes[-2] = suffixes[-2].replace(old_part, new_part)
        # compile and replace
        nlp.tokenizer.infix_finditer = compile_infix_regex(infixes).finditer
        nlp.tokenizer.suffix_search = compile_infix_regex(suffixes).search
    return nlp


def text_to_tokens(text_sources, nlp):
    """
    Obs: fully NA rows will be empty documents.
    """

    def text_to_doc(text):
        return [[tok.text for tok in sent] for sent in nlp(text).sents]

    def texts_to_doc(texts):
        if isinstance(texts, str):
            return text_to_doc(texts)
        else:
            return chain.from_iterable(text_to_doc(text) for text in texts)

    return (
        text_sources.applymap(texts_to_doc, na_action="ignore")
        .agg(lambda row: [sen for doc in row.dropna() for sen in doc], axis=1)
        .map(lambda doc: [[wor.casefold() for wor in sen] for sen in doc])
    )


def make_translate_ngrams(docs, ngrams=3, threshold=0.9):
    if ngrams not in range(1, 4):
        raise ValueError("`ngrams` must be one of 1, 2, 3")
    if ngrams == 1:
        translate_ngrams = lambda x: x  # noqa
    phrases_args = {"scoring": "npmi", "threshold": threshold}
    if ngrams > 1:
        bigram = phrases.Phraser(
            phrases.Phrases((s for d in docs for s in d), **phrases_args)
        )
        translate_ngrams = lambda doc_or_sen: [*bigram[doc_or_sen]]  # noqa
    if ngrams > 2:
        trigram = phrases.Phraser(
            phrases.Phrases(bigram[(s for d in docs for s in d)], **phrases_args)
        )
        translate_ngrams = lambda doc_or_sen: [*trigram[bigram[doc_or_sen]]]  # noqa
    return translate_ngrams


def make_filter_tokens(stop_words={}):
    rx_alpha = re.compile(r"[^\W\d_]")

    def word_filter(tok):
        return (
            (len(tok) > 1)
            and (tok.casefold() not in stop_words)
            and (rx_alpha.search(tok))
        )

    def filter_tokens(doc):
        return [[tok for tok in sen if word_filter(tok)] for sen in doc]

    return filter_tokens


def get_naive_tokenizer():
    """Do we send this to 'limbo/'?"""
    from itertools import chain

    re_sentence = re.compile(r"[\.!?][\s$]")
    re_term = re.compile(r"[^\w@-]+")
    re_alpha = re.compile(r"[^\W\d_]")

    def to_sentences(doc):
        if isinstance(doc, str):
            return re_sentence.split(doc)
        else:
            return chain.from_iterable(re_sentence.split(doc_) for doc_ in doc)

    def to_tokens(sentence):
        return [
            word
            for inter in sentence.casefold().split()
            for dirty in re_term.split(inter)
            for word in [dirty.strip(".-_")]
            if re_alpha.search(word)
        ]

    def tokenize(doc):
        return [
            tokens
            for sentence in to_sentences(doc)
            for tokens in [to_tokens(sentence)]
            if tokens
        ]

    return tokenize


def strict_na(obj):
    """
    pd.isna() applies element-wise to arrays and lists, but we want `False`.
    """
    is_na = pd.isna(obj)
    return is_na if isinstance(is_na, bool) else False


def flatten_nested_containers(obj, class_or_tuple=(list, tuple), dropna=False):
    if isinstance(obj, class_or_tuple):
        for ob in obj:
            yield from flatten_nested_containers(ob, class_or_tuple, dropna)
    elif not dropna or not strict_na(obj):
        yield obj


def wordsentence(doc, in_class_or_tuple=(list, tuple), out_class=list):
    """
    Convert element to Document[Sentence[Word...]...] form
    """
    if strict_na(doc):
        return doc
    if isinstance(doc, in_class_or_tuple):
        return out_class(
            out_class(flatten_nested_containers(sen, in_class_or_tuple, True))
            for sen in doc
            if not strict_na(sen)
        )
    return out_class([out_class([doc])])


def tokens_to_doc(tokens):
    return [[x] if isinstance(x, str) else [*x] for x in tokens]
