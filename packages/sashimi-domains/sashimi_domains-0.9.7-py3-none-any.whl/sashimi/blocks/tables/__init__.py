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

import re
import logging
from pathlib import Path

import pandas as pd

from ..util import sorted_hierarchical_block_index
from ..annotations import (
    get_xblock_yblocks_elements,
    get_subxblocks_yblocks_elements,
    get_xblock_xelements,
    make_get_title,
    load_annotations,
)
from .tables_html import (
    html_output,
    html_multi_xblocks_yblocks_table,
    html_domain_documents_table,
    html_xblock_yblocks_table,
)
from .tables_plots import get_time_plot

logger = logging.getLogger(__name__)


def subxblocks_report(
    corpus, xbtype, xlevel, xb, ybtype, ylevel=1, *, outfile=None, plots=False
):
    """
    Produces a table reporting on the topic assemblages for each subxblock
    of `xb`.
    """
    labels = make_labels(corpus.lblock_to_label, get_labels(corpus))
    sub_annotations = load_annotations(
        corpus, get_subxblocks_yblocks_elements, xbtype, ybtype, ylevel
    )
    data = {
        "id": corpus.lblock_to_label[xlevel, xb],
        "common": sub_annotations[xlevel][xb],
    }
    if plots:
        data["plot"] = get_time_plot(corpus, xbtype, xlevel, xb)
    b_table = html_xblock_yblocks_table(data, xbtype, labels)
    sb_table = xblocks_report(
        corpus,
        xbtype,
        get_subxblocks(corpus, xbtype, xlevel, xb),
        ybtype,
        ylevel,
        plots=plots,
    )
    report = [b_table, sb_table]
    if outfile is None:
        return report
    else:
        return html_output(report, outfile)


def xblocks_report(
    corpus, xbtype, xlevel_blocks, ybtype, ylevel=1, *, outfile=None, plots=False
):
    """
    Produces a table reporting on the yblock assemblages for each xblock
    in `xhblocks`.
    """
    labels = make_labels(corpus.lblock_to_label, get_labels(corpus))
    l1_label = f"L1{xbtype[0].upper()}"
    get_title = make_get_title(corpus.col_title, corpus.col_url, corpus.col_time)
    sub_annotations = load_annotations(
        corpus, get_subxblocks_yblocks_elements, xbtype, ybtype, ylevel
    )
    annotations = load_annotations(
        corpus, get_xblock_yblocks_elements, xbtype, ybtype, ylevel
    )
    data = {}
    for xlevel, xb in xlevel_blocks:
        data[xlevel, xb] = {l1_label: {}}
        if xlevel > 1:
            data[xlevel, xb]["id"] = corpus.lblock_to_label[xlevel, xb]
            data[xlevel, xb]["common"] = sub_annotations[xlevel][xb]
            if plots:
                data[xlevel, xb]["plot"] = get_time_plot(corpus, xbtype, xlevel, xb)
        for sxlevel, sxb in get_subxblocks(corpus, xbtype, xlevel, xb, 1):
            sxdata = data[xlevel, xb][l1_label][sxb] = get_xblock_data(
                corpus,
                xbtype,
                sxlevel,
                sxb,
                ybtype,
                annotations[sxlevel][sxb],
                plots=plots,
            )
            if xbtype == "doc":
                sxdata["elements"] = sxdata["examples"].agg(get_title, axis=1)

    report = html_multi_xblocks_yblocks_table(data, xbtype, labels, plots=plots)
    if outfile is None:
        return report
    else:
        return html_output(report, outfile)


def l1domain_full_report(
    corpus,
    dblock,
    ybtype,
    ylevel=1,
    *,
    outfile=None,
    plots=False,
    docs=slice(None),
    code_terms_map=None,
    code_terms_restrict=None,
):
    """
    Produces a table reporting on a single domain's yblock assemblages and documents.
    """
    labels = make_labels(corpus.lblock_to_label, get_labels(corpus))
    get_title = make_get_title(corpus.col_title, corpus.col_url, corpus.col_time)
    annotations = load_annotations(
        corpus, get_xblock_yblocks_elements, "doc", ybtype, ylevel
    )
    data = get_xblock_data(
        corpus,
        "doc",
        1,
        dblock,
        ybtype,
        annotations[1][dblock],
        plots=plots,
    )
    sample = data["examples"].loc[docs]
    if code_terms_map:
        get_code_terms = make_match_code_terms(
            corpus.col_title, corpus.text_sources, code_terms_map
        )
        code_terms = sample.agg(get_code_terms, axis=1)
        if code_terms_restrict:
            sel_code_terms = code_terms.map(code_terms_restrict.intersection)
            sample = sample.loc[sel_code_terms.astype(bool)]
            code_terms = code_terms.reindex_like(sample)
        data["code_terms"] = code_terms
    data["examples"] = sample
    data["abstracts"] = sample[corpus.text_sources]
    if corpus.col_venue:
        data["venues"] = sample[corpus.col_venue]
    data["titles"] = sample.agg(get_title, axis=1)
    report_domain = html_xblock_yblocks_table(data, "doc", labels)
    report_contents = html_domain_documents_table(data, labels, code_terms_map)
    report = [report_domain, report_contents]
    if outfile is None:
        return report
    else:
        return html_output(report, outfile)


def l1domains_code_terms_report(
    corpus,
    doc_levels_blocks,
    ybtype,
    ylevel=1,
    *,
    outdir=None,
    plots=False,
    docs=slice(None),
    code_terms_map=None,
):
    if any(dlevel != 1 for dlevel, _ in doc_levels_blocks):
        raise ValueError("`doc_level_blocks` must only contain level 1 domains")
    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True)
    for code_term in code_terms_map:
        code_term_dir = outdir / code_term
        code_term_dir.mkdir(exist_ok=True)
        for dlevel, dblock in doc_levels_blocks:
            outfile = code_term_dir / f"{corpus.lblock_to_label[dlevel, dblock]}.html"
            l1domain_full_report(
                corpus,
                dblock,
                ybtype,
                ylevel,
                outfile=outfile,
                plots=plots,
                docs=docs,
                code_terms_map=code_terms_map,
                code_terms_restrict={code_term},
            )


def get_xblock_data(corpus, xbtype, xlevel, xb, ybtype, annotated, *, plots=False):
    """
    Get the report data for the given domain.
    """
    order = "frequency" if ybtype == "doc" else "time"
    xblocks_elements = get_xblock_xelements(
        corpus, xbtype, xlevel, xb, order, ybtype=ybtype, num=None
    )
    data = {
        "id": corpus.lblock_to_label[xlevel, xb],
        "specific": annotated,
    }
    if xbtype == "doc":
        data["examples"] = corpus.data.loc[xblocks_elements]
    else:
        data["examples"] = corpus.data.loc[xblocks_elements].map(
            lambda x: f"{x[0]} <small>({x[1]})</small>"
        )
    if plots:
        data["plot"] = get_time_plot(corpus, xbtype, xlevel, xb)

    return data


##########
# Coding #
##########


def code_frequency_tables(corpus, domain_labels, code_terms_map, fname_prefix=None):
    if fname_prefix is None:
        fname_prefix = ",".join(domain_labels) + "_×_" + ",".join(code_terms_map)
    match_code_terms = make_match_code_terms(
        corpus.col_title, corpus.text_sources, code_terms_map
    )
    code_coocs, code_frequencies = get_codes_frequencies(
        corpus,
        [corpus.label_to_tlblock[dl][1:] for dl in domain_labels],
        match_code_terms,
    )
    code_frequencies.to_csv(
        corpus.blocks_adir / f"{fname_prefix}-code_domain_frequencies.csv"
    )
    code_coocs.to_csv(corpus.blocks_adir / f"{fname_prefix}-code_colocations.csv")


def get_codes_frequencies(corpus, doc_levels_blocks, match_code_terms):
    col_any, col_size, col_sum = ["#Any", "#Size", "#Sum"]
    domains_codes_count_d = {}
    codes_coocs_count_d = {}
    for dlevel, dblock in doc_levels_blocks:
        dlabel = corpus.lblock_to_label[dlevel, dblock]
        domain = corpus.data.loc[corpus.dblocks[dlevel].eq(dblock)]
        domain_codes = domain.agg(match_code_terms, axis=1)
        codes_coocs_count_d[dlabel] = domain_codes.map(tuple).value_counts()
        codes_coocs_count_d[dlabel][col_any] = domain_codes.astype(bool).sum()
        codes_coocs_count_d[dlabel][col_size] = len(domain_codes)
        domains_codes_count_d[dlabel] = domain_codes.explode().value_counts()
        domains_codes_count_d[dlabel][col_any] = domain_codes.astype(bool).sum()
        domains_codes_count_d[dlabel][col_size] = len(domain_codes)

    codes_coocs_count = pd.concat(codes_coocs_count_d.values())
    codes_coocs_count = codes_coocs_count.groupby(codes_coocs_count.index).sum()
    codes_coocs_count = codes_coocs_count.sort_values(ascending=False)
    codes_coocs_count.name = "Colocations"

    domains_codes_count = pd.DataFrame(domains_codes_count_d, dtype="Int64").fillna(0)
    domains_codes_count[col_sum] = domains_codes_count.sum(axis=1).astype("Int64")
    domains_codes_count = domains_codes_count.sort_values(col_sum, ascending=False)

    return codes_coocs_count, domains_codes_count


####################
# Helper functions #
####################


def get_subxblocks(corpus, xbtype, xlevel, xb, sxlevel=None):
    if sxlevel is None:
        sxlevel = corpus.get_sublevel(xlevel, xbtype)
    xblocks, xlevels = corpus.get_blocks_levels(xbtype)
    xblocks = xblocks[xblocks[xlevel].eq(xb)]
    return [
        corpus.hblock_to_level_block(x, xbtype)
        for x in sorted_hierarchical_block_index(xblocks, xlevels, level=sxlevel)
    ]


def make_labels(lblock_to_label, given_labels):
    def func(level, block):
        lh = lblock_to_label[level, block]
        lb = given_labels.get(lh, None)
        return lh if lb is None else f"{lh}: {lb}"

    return func


def get_labels(corpus, fpath=None):
    if (fpath is not None) and fpath.exists():
        return pd.read_csv(fpath).set_index("Domain")["Label"]
    return pd.Series(dtype=object)


def make_match_code_terms(col_title, text_sources, code_terms_map):
    code_terms_rx = {k: re.compile(rf"(?i)\b{v}\b") for k, v in code_terms_map.items()}
    text_columns = sorted(set([col_title, *text_sources]))

    def match_code_terms(row):
        code_terms = set()
        for key, rex in code_terms_rx.items():
            for text in row[text_columns]:
                if rex.search(text):
                    code_terms.add(key)
        return sorted(code_terms)

    return match_code_terms
