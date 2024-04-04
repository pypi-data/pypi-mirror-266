# Sashimi - Study of the organisation and evolution of a corpus
#
# Author(s):
# * Ale Abdo <abdo@member.fsf.org>
#
# License:
# [GNU-GPLv3+](https://www.gnu.org/licenses/gpl-3.0.html)
#
# Project:
# <https://en.wikiversity.org/wiki/The_dynamics_and_social_organization_of
#  _innovation_in_the_field_of_oncology>
#
# Reference repository for this file:
# <https://gitlab.com/solstag/sashimi>
#
# Contributions are welcome, get in touch with the author(s).

from __future__ import annotations
import typing

from heapq import nsmallest as heapq_nsmallest
import html
import random

import pandas
from tqdm import tqdm

from ..naming import naming
from ..ioio import ioio
from ..entropies import make_nested_specificity, make_nested_commonality

if typing.TYPE_CHECKING:
    from ..graph_models import GraphModels


##############################
# xblock yblocks annotations #
##############################


def get_xblock_yblocks(
    corpus: GraphModels, xbtype, xlevel, xb, ybtype, ylevel, num=None, anti=False
):
    """
    Returns
    =======
    [(yblock, yblock_entropy), ...]
    """
    hxb = corpus.level_block_to_hblock(xlevel, xb, xbtype)
    get_counts = make_get_counts(corpus, xbtype, ybtype, ylevel)
    ybcs = get_counts(hxb, anti=anti)
    ybs = ybcs[-1][0] if anti else ybcs[0]
    upybcs = [get_counts(hxb[:i]) for i in reversed(range(1, len(hxb)))]

    nested_specificity = make_nested_specificity(ybcs, upybcs)

    def sortkeyf(x):
        return -x[1]

    return nsmallest(num, ((x, nested_specificity(x)) for x in ybs), key=sortkeyf)


def get_xblock_yblocks_elements(
    corpus: GraphModels,
    xbtype,
    xlevel,
    xb,
    ybtype,
    ylevel,
    num=10,
    ent_frac=0.5,
    anti=False,
):
    """
    Given a domain block, returns a list containing, for each pertinent level 1 topic,
    a list of pertinent terms.

    After ordering topics by pointwise topic-level relative entropy, takes enough topics
    to account for half of the positive part of the topic-level relative entropy between
    the domain and its super domains.

    Then, for each topic, takes all terms whose entropy is larger than half the largest
    term entropy.

    Returns
    =======
    {
        'ent': (covered positive relent, total positive relent),
        'blocks': dict(
            block: dict(
                'ent': block relent,
                'elements': list( (element, element_relent), ... )
            ),
            ...
        ),
        'btypes': (xbtype, ybtype),
        'levels': (xlevel, ylevel),
    }
    """
    yblocks, _ = corpus.get_blocks_levels(ybtype)
    xblock_yblocks = get_xblock_yblocks(
        corpus, xbtype, xlevel, xb, ybtype, ylevel, anti=anti
    )

    get_counts = make_get_counts(corpus, xbtype, ybtype, None)
    hxb = corpus.level_block_to_hblock(xlevel, xb, xbtype)
    ycs = get_counts(hxb, anti=anti)
    upycs = [get_counts(hxb[:i]) for i in reversed(range(1, len(hxb)))]

    yblocks_elements = {}
    for yb, yb_ent in yield_values_fraction(xblock_yblocks, ent_frac):
        yblocks_elements[yb] = {"ent": yb_ent, "elements": []}
    total_ent = sum(v for _, v in xblock_yblocks if v > 0)
    cum_ent = sum(x["ent"] for x in yblocks_elements.values())

    # TODO: we could consider the mutual information with previous terms and
    # skip the term if it's too high.

    nested_specificity = make_nested_specificity(ycs, upycs)

    for yb, ybinfo in yblocks_elements.items():
        elements = yblocks[yblocks[ylevel].eq(yb)].index
        elements = ((x, nested_specificity(x)) for x in elements)
        elements = filter(lambda x: x[1] > 0, elements)
        elements = list(elements)
        ybinfo["ent_el"] = sum(x[1] for x in elements)
        elements = nsmallest(num, elements, key=lambda x: -x[1])
        if not elements:
            continue
        e_list = [elements.pop(0)]
        for el, el_ent in elements:
            if el_ent < e_list[0][1] / 2:
                break
            e_list.append((el, el_ent))
        ybinfo["elements"].extend(e_list)

    return {
        "ent": (cum_ent, float(total_ent)),
        "blocks": yblocks_elements,
        "btypes": (xbtype, ybtype),
        "levels": (xlevel, ylevel),
    }


def get_xblock_docs(corpus: GraphModels, xbtype, xlevel, xb, order="sample", n=10):
    xdc = corpus.get_xblock_yblocks_counts(xbtype, xlevel, xb, "doc", None)
    xdc = dict((k, v) for k, v in xdc.items() if v)
    docs = corpus.data.index.intersection(xdc).to_list()
    n = len(docs) if n is None else min(n, len(docs))
    if order == "sample":
        return random.sample(docs, n)


###############################
# xblocks yblocks annotations #
###############################


def get_xblocks_yblocks(
    corpus: GraphModels, xbtype, xlevelblocks, ybtype, ylevel, n=None, ent_frac=0.5
):
    yblocks = {}
    for xlevel, xb in xlevelblocks:
        xblock_yblocks = get_xblock_yblocks(corpus, xbtype, xlevel, xb, ybtype, ylevel)
        for k, v in xblock_yblocks:
            yblocks[k] = yblocks.setdefault(k, 0.0) + v
    return list(yield_values_fraction(yblocks.items(), ent_frac))

    # alternative taking ent_frac for each individual topic (less expressive?)
    yblocks = {}
    for xlevel, xb in xlevelblocks:
        xblock_yblocks = get_xblock_yblocks(corpus, xbtype, xlevel, xb, ybtype, ylevel)
        for k, v in yield_values_fraction(xblock_yblocks, ent_frac):
            yblocks[k] = yblocks.setdefault(k, 0.0) + v
    return list(yblocks.items())


def get_yblocks_xblocks(
    corpus: GraphModels, xbtype, xlevel, ybtype, ylevel, ybs, n=None, ent_frac=0.5
):
    ybs = set(ybs)
    xblocks = []

    for xb in tqdm(corpus.get_blocks_levels(xbtype)[0][xlevel].unique()):
        xb_yblocks = get_xblock_yblocks(corpus, xbtype, xlevel, xb, ybtype, ylevel)
        for _, ent_low in yield_values_fraction(xb_yblocks, ent_frac):
            pass
        ent_sum = sum(ent for yb, ent in xb_yblocks if yb in ybs and ent > 0)
        if ent_sum >= ent_low:
            xblocks.append((xb, ent_sum))
    return sorted(xblocks, lambda x: -x[1])


#################################
# subxblock yblocks annotations #
#################################


def get_subxblocks_yblocks(
    corpus: GraphModels, xbtype, xlevel, xb, ybtype, ylevel, num=None, anti=False
):
    get_counts = make_get_counts(corpus, xbtype, ybtype, ylevel)
    hxb = corpus.level_block_to_hblock(xlevel, xb, xbtype)
    yb_counts, _ = get_counts(hxb)
    upx_yb_counts = [get_counts(hxb[:i]) for i in range(1, len(hxb))]

    if xlevel == 1:
        sxlevel = "v"
    else:
        sxlevel = corpus.get_sublevel(xlevel, xbtype)

    xblocks, _ = corpus.get_blocks_levels(xbtype)
    subxblocks = xblocks[xblocks[xlevel].eq(xb)].groupby(sxlevel)
    subx_yb_counts = []
    for subxb, group in subxblocks:
        hsubxb = corpus.level_block_to_hblock(sxlevel, subxb, xbtype)
        subx_yb_counts.append(get_counts(hsubxb))

    keyf = make_nested_commonality(subx_yb_counts, upx_yb_counts)

    yblocks = ((x, keyf(x)) for x in yb_counts)
    yblocks = filter(lambda x: x[1] > 0, yblocks)

    def sortkeyf(x):
        return -x[1]

    return nsmallest(num, yblocks, key=sortkeyf)


def get_subxblocks_yblocks_elements(
    corpus: GraphModels,
    xbtype,
    xlevel,
    xb,
    ybtype,
    ylevel,
    num=5,
    ent_frac=0.5,
    anti=False,
):
    xblocks, xlevels = corpus.get_blocks_levels(xbtype)
    yblocks, ylevels = corpus.get_blocks_levels(ybtype)

    get_counts = make_get_counts(corpus, xbtype, ybtype, None)
    hxb = corpus.level_block_to_hblock(xlevel, xb, xbtype)
    upx_y_counts = [get_counts(hxb[:i]) for i in range(1, len(hxb))]

    subxblocks_yblocks = get_subxblocks_yblocks(
        corpus, xbtype, xlevel, xb, ybtype, ylevel
    )

    if xlevel == 1:
        return {"ent": (0.0, 0.0), "blocks": {}}
    # sxlevel = 1 # too expensive
    sxlevel = corpus.get_sublevel(xlevel, xbtype)
    subxblocks = xblocks[xblocks[xlevel].eq(xb)].groupby(sxlevel)
    subx_y_counts = []
    for subxb, group in subxblocks:
        hsubxb = corpus.level_block_to_hblock(sxlevel, subxb, xbtype)
        subx_y_counts.append(get_counts(hsubxb))

    yblocks_elements = {}
    for yb, yb_ent in yield_values_fraction(subxblocks_yblocks, ent_frac):
        yblocks_elements[yb] = {"ent": yb_ent, "elements": []}
    total_ent = sum(v for _, v in subxblocks_yblocks if v > 0)
    cum_ent = sum(x["ent"] for x in yblocks_elements.values())

    keyf = make_nested_commonality(subx_y_counts, upx_y_counts)

    for yb, ybinfo in yblocks_elements.items():
        elements = yblocks[yblocks[ylevel].eq(yb)].index
        elements = ((x, keyf(x)) for x in elements)
        elements = filter(lambda x: x[1] > 0, elements)
        elements = list(elements)
        ybinfo["ent_el"] = sum(x[1] for x in elements)
        elements = nsmallest(num, elements, key=lambda x: -x[1])
        if not elements:
            continue
        e_list = [elements.pop(0)]
        for el, el_ent in elements:
            if el_ent < e_list[0][1] / 2:
                break
            e_list.append((el, el_ent))
        ybinfo["elements"].extend(e_list)

    return {
        "ent": (cum_ent, float(total_ent)),
        "blocks": yblocks_elements,
        "btypes": (xbtype, ybtype),
        "levels": (xlevel, ylevel),
    }


######################
# xblock annotations #
######################


def get_xblock_xelements(
    corpus: GraphModels, xbtype, xlevel, xb, order, ybtype=None, num=None, sxblocks=None
):
    xblocks, _ = (
        corpus.get_blocks_levels(xbtype) if sxblocks is None else (sxblocks, None)
    )
    if ybtype:
        xelement_yelements = corpus.get_xelement_yelements(xbtype, ybtype)
    xelements = xblocks[xblocks[xlevel].eq(xb)]
    num = min(num, len(xelements)) if num is not None else len(xelements)
    if order == "time":
        assert xbtype == "doc"
        return corpus.data.loc[xelements.index].sort_values(corpus.col_time).index
    if order == "sample":
        xs = xelements.sample(num).index
        if xbtype == "doc":
            return corpus.data.loc[xs, corpus.col_title].astype(str).to_list()
        if ybtype:

            def keyf(x):
                return -sum(xelement_yelements[x].values())

            return [(x, -keyf(x)) for x in xs]
        else:
            return list(xs)
    if xbtype == "term" and order == "concentration":
        grade, _, _ = corpus.get_graded_vocab_cached(corpus.column, sampled=True)

        def keyf(x):
            return -grade[x]

        return sorted(xelements.index, key=keyf)[:num]
    if order == "frequency":

        def keyf(x):
            return -sum(xelement_yelements[x].values())

        xs = [x for x in nsmallest(num, xelements.index, key=keyf)]
        # xs_freq = [-keyf(x) for x in nsmallest(num, xelements.index, key=keyf)]
        # xs_cumfreq = [sum(xs_freq[: i + 1]) for i in range(len(xs))]
        # total_freq = sum(-keyf(x) for x in xelements.index)
        return [
            # f"{x} <small>({-keyf(x)}, "
            # + f"{xs_freq[i]/total_freq:.0%}/{xs_cumfreq[i]/total_freq:.0%})</small>"
            (x, -keyf(x))
            for i, x in enumerate(xs)
        ]


########
# misc #
########


def make_get_counts(corpus: GraphModels, xbtype, ybtype, ylevel):
    _, xlevels = corpus.get_blocks_levels(xbtype)

    def get_regular_counts(hxb):
        xlevel_, xb_ = corpus.hblock_to_level_block(hxb, xbtype)
        xyc = corpus.get_xblock_yblocks_counts(xbtype, xlevel_, xb_, ybtype, ylevel)
        return xyc, sum(xyc.values())

    def get_anti_counts(hxb):
        xlevel_, xb_ = corpus.hblock_to_level_block(hxb, xbtype)
        counts = []
        for axlevel in [xl for xl in xlevels if xl > xlevel_]:
            xyc = corpus.get_antixblock_yblocks_counts(
                xbtype, xlevel_, xb_, axlevel, ybtype, ylevel
            )
            counts.append((xyc, sum(xyc.values())))
        return counts

    def get_counts(hxb, anti=False):
        if anti:
            return get_anti_counts(hxb)
        return get_regular_counts(hxb)

    return get_counts


def nsmallest(n, iterable, key):
    if n is None:
        return sorted(iterable, key=key)
    else:
        return heapq_nsmallest(n, iterable, key=key)


def yield_values_fraction(keys_values, frac):
    total = sum(v for _, v in keys_values if v > 0)
    cum = 0.0
    for k, v in keys_values:
        cum += v
        yield (k, v)
        if cum > total * frac:
            break


def get_btype_name(btype, plural=False):
    if not plural:
        return "document" if btype == "doc" else "term" if btype == "ter" else "element"
    else:
        return (
            "documents" if btype == "doc" else "terms" if btype == "ter" else "elements"
        )


def format_xblock_yblocks_elements(lblock_to_label, xblock_yblocks_elements):
    formatted = []
    ylevel = xblock_yblocks_elements["levels"][1]
    for yb, yb_info in xblock_yblocks_elements["blocks"].items():
        if formatted:
            formatted.append(" · ")
        formatted.append(lblock_to_label[ylevel, yb])
        formatted.append(": ")
        for el, el_ent in yb_info["elements"]:
            formatted.append(f"{el}")
            formatted.append(", ")
        formatted.pop()

    pow_ent = pow(2, xblock_yblocks_elements["ent"][1])

    return f"{pow_ent:.1f} / " + "".join(formatted)


def prepare_xblock_yblocks_elements(lblock_to_label, xblock_yblocks_elements):
    items = []
    ylevel = xblock_yblocks_elements["levels"][1]
    ybtype = xblock_yblocks_elements["btypes"][1]
    items.append((ybtype, xblock_yblocks_elements["ent"][1]))
    for yb, yb_info in xblock_yblocks_elements["blocks"].items():
        items.append((lblock_to_label[ylevel, yb], yb_info["ent"], None))
        for el, el_ent in yb_info["elements"]:
            items.append((f"{el}", el_ent))
    return items


def make_get_title(key_title, key_url=None, key_time=None):
    """
    `get_title(row)` used e.g. in `corpus.data.agg(get_title, axis=1)`.
    """

    def get_title(row):
        """
        Returns an enriched title for a row of data.
        """
        # pandas bug: .agg(get_title) → if access row[_] → result df not series
        if row.empty:
            return None

        title = html.escape(str(row[key_title]))
        if key_time:
            if pandas.notna(row[key_time]):
                time = html.escape(str(row[key_time]))
                if time:
                    title += f" ({time})"
        if key_url:
            urls = row[key_url]
            if not isinstance(urls, (pandas.Series, list, tuple)):
                urls = [urls]
            urls = [str(x) for x in urls if x]
            if urls:
                title += " "
            for url in urls:
                title += f'<a target="_blank" href="{html.escape(str(url))}">🗎</a>'
        return title

    return get_title


#########
# cache #
#########


def load_annotations(
    corpus: GraphModels,
    annotation_function,
    xbtype,
    ybtype,
    ylevel=1,
    num=5,
    ent_frac=0.5,
):
    btypes = {"xbtype": xbtype, "ybtype": ybtype}
    use_cache = corpus.use_cached_annotations
    sample_hash = corpus.get_sample_hash(
        **{x: x in btypes.values() for x in ["doc", "ter", "ext"]}
    )
    fdir = corpus.chained_dir if "ext" in btypes.values() else corpus.blocks_dir
    use_sample = corpus.use_sampled_annotations or f"sample={sample_hash};" in fdir.stem
    if use_cache:
        fname_params = (
            *btypes.items(),
            ("ylevel", ylevel),
            ("num", num),
            ("ent_frac", ent_frac),
        )
        if use_sample and sample_hash:
            fname_params = [("sample", sample_hash), *fname_params]
        fpath = (
            fdir
            / "cache"
            / naming.gen(
                annotation_function.__name__,
                fname_params,
                ".pickle.xz",
            )
        )
        if fpath.exists():
            print(
                f"Loading cached "
                f"{'sampled ' if (use_sample and sample_hash) else ''}"
                f"annotations: {fpath}"
            )
            return ioio.load(fpath)

    if not use_sample and sample_hash:
        raise ValueError("No cached unsampled annotations found!")
    annotations = {}
    xblocks, xlevels = corpus.get_blocks_levels(xbtype)
    for xlevel in tqdm(xlevels):
        annotations[xlevel] = {}
        for xb in tqdm(xblocks[xlevel].unique()):
            annotations[xlevel][xb] = annotation_function(
                corpus, xbtype, xlevel, xb, ybtype, ylevel, num, ent_frac
            )

    if use_cache:
        ioio.store(annotations, fpath)

    return annotations


def make_get_annotations(corpus: GraphModels):
    """
    By using this function one can cache results in-place like
    `annotations = cache(make_get_annotations(corpus))`
    """

    def get_annotations(xbtype, xlevel, ybtype, ylevel, edges, **kwargs):
        """
        Usage:
        ```
        annotations = get_annotations("doc", 2, "ter", 1, "specific")
        annotations[xb]["blocks"][yb]["elements"]` -> [(element, relent), ...]
        ```
        """
        if edges == "specific":
            annotation_function = get_xblock_yblocks_elements
        elif edges == "common" and xlevel > 1:
            annotation_function = get_subxblocks_yblocks_elements
        elif edges == "common" and xlevel == 1:
            raise ValueError('`edges="common"` requires xlevel > 1')
        else:
            raise ValueError("`edges` must be one of ['specific', 'common']")
        annotations = load_annotations(
            corpus, annotation_function, xbtype, ybtype, ylevel, **kwargs
        )[xlevel]
        return annotations

    return get_annotations
