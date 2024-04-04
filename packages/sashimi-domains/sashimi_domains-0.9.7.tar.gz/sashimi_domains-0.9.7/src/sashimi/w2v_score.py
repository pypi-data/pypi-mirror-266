# Originally LGPL licensed code from gensim
# See https://github.com/RaRe-Technologies/gensim

from numpy import (
    exp,
    log,
    dot,
    zeros,
    outer,
    random,
    dtype,
    float32 as REAL,
    double,
    uint32,
    seterr,
    array,
    uint8,
    vstack,
    fromstring,
    sqrt,
    newaxis,
    ndarray,
    empty,
    sum as np_sum,
    prod,
    ones,
    ascontiguousarray,
    vstack,
    logaddexp,
)

from copy import deepcopy


def score_sentence_cbow(model, sentence, alpha, work=None, neu1=None):
    """
    Obtain likelihood score for a single sentence in a fitted CBOW representaion.
    The sentence is a list of Vocab objects (or None, where the corresponding
    word is not in the vocabulary. Called internally from `Word2Vec.score()`.
    This is the non-optimized, Python version. If you have cython installed, gensim
    will use the optimized version from word2vec_inner instead.
    """
    log_prob_sentence = 0.0
    if model.negative:
        raise RuntimeError("scoring is only available for HS=True")

    word_vocabs = [model.wv.vocab[w] for w in sentence if w in model.wv.vocab]
    for pos, word in enumerate(word_vocabs):
        if word is None:
            continue  # OOV word in the input sentence => skip

        start = max(0, pos - model.window)
        window_pos = enumerate(word_vocabs[start : (pos + model.window + 1)], start)
        word2_indices = [
            word2.index
            for pos2, word2 in window_pos
            if (word2 is not None and pos2 != pos)
        ]
        l1 = np_sum(model.wv.syn0[word2_indices], axis=0)  # 1 x layer1_size
        if word2_indices and model.cbow_mean:
            l1 /= len(word2_indices)
        log_prob_sentence += score_cbow_pair(model, word, word2_indices, l1)

    return log_prob_sentence


def score_cbow_pair(model, word, word2_indices, l1):
    l2a = model.syn1[word.point]  # 2d matrix, codelen x layer1_size
    sgn = (-1.0) ** word.code  # ch function, 0-> 1, 1 -> -1
    lprob = -logaddexp(0, -sgn * dot(l1, l2a.T))
    return sum(lprob)


def score_words_cbow(model, sentence):
    if model.negative:
        raise RuntimeError("scoring is only available for HS=True")

    log_prob_words = [None] * len(sentence)
    index = [i for i, w in enumerate(sentence) if w in model.wv.vocab]
    word_vocabs = [model.wv.vocab[sentence[i]] for i in index]

    for pos, (word, idx) in enumerate(zip(word_vocabs, index)):
        if word is None:
            continue  # OOV word in the input sentence => skip

        start = max(0, pos - model.window)
        window_pos = enumerate(word_vocabs[start : (pos + model.window + 1)], start)
        word2_indices = [
            word2.index
            for pos2, word2 in window_pos
            if (word2 is not None and pos2 != pos)
        ]
        l1 = np_sum(model.wv.syn0[word2_indices], axis=0)  # 1 x layer1_size
        if word2_indices and model.cbow_mean:
            l1 /= len(word2_indices)
        log_prob_words[idx] = score_cbow_pair(model, word, word2_indices, l1)

    return log_prob_words


def score_sentence_sg(model, sentence, work=None):
    """
    Obtain likelihood score for a single sentence in a fitted skip-gram representaion.
    The sentence is a list of Vocab objects (or None, when the corresponding
    word is not in the vocabulary). Called internally from `Word2Vec.score()`.
    This is the non-optimized, Python version. If you have cython installed, gensim
    will use the optimized version from word2vec_inner instead.
    """

    log_prob_sentence = 0.0
    if model.negative:
        raise RuntimeError("scoring is only available for HS=True")

    word_vocabs = [model.wv.vocab[w] for w in sentence if w in model.wv.vocab]
    for pos, word in enumerate(word_vocabs):
        if word is None:
            continue  # OOV word in the input sentence => skip

        # now go over all words from the window, predicting each one in turn
        start = max(0, pos - model.window)
        for pos2, word2 in enumerate(
            word_vocabs[start : pos + model.window + 1], start
        ):
            # don't train on OOV words and on the `word` itself
            if word2 is not None and pos2 != pos:
                log_prob_sentence += score_sg_pair(model, word, word2)

    return log_prob_sentence


def score_sg_pair(model, word, word2):
    l1 = model.wv.syn0[word2.index]
    l2a = deepcopy(model.syn1[word.point])  # 2d matrix, codelen x layer1_size
    sgn = (-1.0) ** word.code  # ch function, 0-> 1, 1 -> -1
    lprob = -logaddexp(0, -sgn * dot(l1, l2a.T))
    return sum(lprob)


def score_words_sg(model, sentence):
    if model.negative:
        raise RuntimeError("scoring is only available for HS=True")

    log_prob_words = [None] * len(sentence)
    index = [i for i, w in enumerate(sentence) if w in model.wv.vocab]
    word_vocabs = [model.wv.vocab[sentence[i]] for i in index]

    for pos, (word, idx) in enumerate(zip(word_vocabs, index)):
        log_prob_words[idx] = 0.0
        if word is None:
            continue  # OOV word in the input sentence => skip

        start = max(0, pos - model.window)
        for pos2, word2 in enumerate(
            word_vocabs[start : pos + model.window + 1], start
        ):
            # don't train on OOV words and on the `word` itself
            if word2 is not None and pos2 != pos:
                log_prob_words[idx] += score_sg_pair(model, word, word2)
            # TODO shoul divide a word's contribution by respective word2s size?
    return log_prob_words


def score_words(model, sentence):
    if not model.hs:
        raise RuntimeError(
            "We have currently only implemented score \
                for the hierarchical softmax scheme, so you need to have \
                run word2vec with hs=1 and negative=0 for this to work."
        )
    if model.sg:
        return score_words_sg(model, sentence)
    else:
        return score_words_cbow(model, sentence)


def score_sentence(model, sentence):
    if not model.hs:
        raise RuntimeError(
            "We have currently only implemented score \
                for the hierarchical softmax scheme, so you need to have \
                run word2vec with hs=1 and negative=0 for this to work."
        )
    if model.sg:
        return score_sentence_sg(model, sentence)
    else:
        return score_sentence_cbow(model, sentence, None)


def score_word_pair(model, w1, w2):
    if model.hs:
        word = model.wv.vocab[w1]
        word2 = model.wv.vocab[w2]
        l1 = model.wv.syn0[word2.index]
        #        l2a = deepcopy(model.syn1[word.point])  # 2d matrix, codelen x layer1_size
        l2a = model.syn1[word.point]  # 2d matrix, codelen x layer1_size
        sgn = (-1.0) ** word.code  # ch function, 0-> 1, 1 -> -1
        lprob = -logaddexp(0, -sgn * dot(l1, l2a.T))
        return sum(lprob)
    else:
        word = model.wv.vocab[w1]
        word2 = model.wv.vocab[w2]
        l1 = model.wv.syn0[word2.index]
        l2 = model.syn1neg[word.index]
        lprob = -logaddexp(0, -dot(l1, l2))
        return lprob
