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

import pandas
from collections import Counter
from tqdm import tqdm

from ..ioio import ioio
from ..naming import naming

"""
Methods to be used with hierarchical_block_map.

'zmethods' should be defined as:

def example(corpus, blocks, level, index)

and should return a pandas.Series of a scalar dtype and indexed by 'index'.
"""


def __init__():
    return


def count(corpus, blocks, level, index):
    count = blocks.groupby(blocks.loc[:, level]).size()
    count = count.reindex(index)
    count = count.where(count.notnull(), 0)
    return count


def density(corpus, blocks, level, index):
    count = blocks.groupby(blocks.loc[:, level]).size()
    count = count.reindex(index)
    count = count.where(count.notnull(), 0)
    dens = count / count.sum()
    return dens


def x_doc_density_gen(btype):
    def x_doc_density(corpus, xblocks, xlevel, index):
        x_documents = getattr(corpus, f"{btype}_documents")
        x_groups = xblocks[xlevel].groupby(xblocks[xlevel])
        count = pandas.Series(index=xblocks[xlevel].unique())
        for n, g in tqdm(x_groups, desc=f"Level {xlevel}"):
            s = set()
            for x in g.index:
                s.update(x_documents[x])
            count.loc[n] = len(corpus.data.index.intersection(s))
        count = count.reindex(index)
        count = count.where(count.notnull(), 0)
        value = count / len(corpus.data)
        return value

    x_doc_density.__name__ = f"{btype}_doc_density"
    return x_doc_density


def x_link_density_gen(btype):
    def x_doc_density(corpus, xblocks, xlevel, index):
        x_documents = getattr(corpus, f"{btype}_documents")
        x_groups = xblocks[xlevel].groupby(xblocks[xlevel])
        count = pandas.Series(0, index=xblocks[xlevel].unique())
        data_index = set(corpus.data.index)
        for n, g in tqdm(x_groups, desc=f"{btype.capitalize()} density level {xlevel}"):
            for x in g.index:
                count.loc[n] += sum(
                    v for k, v in x_documents[x].items() if k in data_index
                )
        count = count.reindex(index)
        count = count.where(count.notnull(), 0)
        docs = corpus.get_doc_terms() if btype == "ter" else corpus.get_doc_exts()
        value = count / docs.transform(len).sum()
        return value

    x_doc_density.__name__ = "{}_doc_density".format(btype)
    return x_doc_density


# Auxiliary methods, used in zmethods or to generate them


def density_pair_gen(idx0, idx1, func):
    def density_pair(corpus, blocks, level, index):
        count0 = blocks.loc[idx0].groupby(blocks[level]).size()
        count0 = count0.reindex(index)
        count0 = count0.where(count0.notnull(), 0)
        dens0 = count0 / count0.sum()
        count1 = blocks.loc[idx1].groupby(blocks[level]).size()
        count1 = count1.reindex(index)
        count1 = count1.where(count1.notnull(), 0)
        dens1 = count1 / count1.sum()
        value = func(dens0, dens1)
        return value.where(value.notnull(), 1)  # 0/0 => 1

    density_pair.__name__ = "density_{}_{}_{}".format(
        func.__name__, idx0.name, idx1.name
    )
    return density_pair


def x_doc_density_pair_gen(idx0, idx1, func, btype):
    def x_doc_density_pair(corpus, xblocks, xlevel, index):
        x_documents = getattr(corpus, f"{btype}_documents")
        x_groups = xblocks[xlevel].groupby(xblocks[xlevel])
        count0 = pandas.Series(index=xblocks[xlevel].unique())
        count1 = pandas.Series(index=xblocks[xlevel].unique())
        index0 = corpus.data.index.intersection(idx0)
        index1 = corpus.data.index.intersection(idx1)
        for n, g in tqdm(x_groups):
            s = set()
            for x in g.index:
                s.update(x_documents[x])
            count0.loc[n] = len(index0.intersection(s))
            count1.loc[n] = len(index1.intersection(s))
        count0 = count0.reindex(index)
        count0 = count0.where(count0.notnull(), 0)
        count1 = count1.reindex(index)
        count1 = count1.where(count1.notnull(), 0)
        value = func(count0 / index0.size, count1 / index1.size)
        return value.where(value.notnull(), 1)

    x_doc_density_pair.__name__ = "{}_doc_density_{}_{}_{}".format(
        btype, func.__name__, idx0.name, idx1.name
    )
    return x_doc_density_pair


def x_link_density_pair_gen(idx0, idx1, func, btype):
    def x_doc_density_pair(corpus, xblocks, xlevel, index):
        x_documents = getattr(corpus, f"{btype}_documents")
        x_groups = xblocks[xlevel].groupby(xblocks[xlevel])
        count0 = pandas.Series(index=xblocks[xlevel].unique())
        count1 = pandas.Series(index=xblocks[xlevel].unique())
        index0 = set(corpus.data.index.intersection(idx0))
        index1 = set(corpus.data.index.intersection(idx1))
        for n, g in tqdm(x_groups):
            for x in g.index:
                count0.loc[n] = sum(v for k, v in x_documents[x].items() if k in index0)
                count1.loc[n] = sum(v for k, v in x_documents[x].items() if k in index1)
        count0 = count0.reindex(index)
        count0 = count0.where(count0.notnull(), 0)
        count1 = count1.reindex(index)
        count1 = count1.where(count1.notnull(), 0)
        docs = corpus.get_doc_terms() if btype == "ter" else corpus.get_doc_exts()
        value = func(
            count0 / docs.loc[docs.index.intersection(idx0)].transform(len).sum(),
            count1 / docs.loc[docs.index.intersection(idx1)].transform(len).sum(),
        )
        return value.where(value.notnull(), 1)

    x_doc_density_pair.__name__ = "{}_doc_density_{}_{}_{}".format(
        btype, func.__name__, idx0.name, idx1.name
    )
    return x_doc_density_pair


def get_cross_counts(corpus, ybtype, ltype):
    """
    Pairs every domain from every level with every cross block from every
    level (topics or extended blocks) and counts the number of links or documents
    connected to each cross block.

    (corpus)
    (ybtype): str
        The block type to cross. Either 'ter' or 'ext'.
    (ltype) str
        Either 'link' or 'doc'. Whether to count links or documents.

    Result
    ------
    A pandas.Series with MultiIndex:
    (domain level, domain, cross level, cross block)
    """
    use_cache = corpus.use_cached_cross_counts
    dblocks = corpus.dblocks
    yblocks, yblocks_levels = corpus.get_blocks_levels(ybtype)
    y_documents = corpus.get_xelement_yelements(ybtype, "doc")
    fname_params = [("ybtype", ybtype), ("ltype", ltype)]
    if sample_hash := corpus.get_sample_hash(
        **{x: x in {"doc", ybtype} for x in ["doc", "ter", "ext"]}
    ):
        fname_params = [("sample", sample_hash), *fname_params]
    if ybtype == "ter":
        fdir = corpus.blocks_dir
    elif ybtype == "ext":
        fdir = corpus.chained_dir
    fpath = (
        fdir / "cache" / naming.gen("cross_counts", fname_params, corpus.suffix_data)
    )

    if use_cache:
        try:
            values = ioio.load(fpath)
            if isinstance(values, dict):
                values = pandas.Series(
                    index=pandas.MultiIndex.from_tuples(values["index"]),
                    data=(x for x in values["data"]),
                )
            print("Loaded cached cross counts")
            return values
        except FileNotFoundError:
            pass

    keys, vals = [], []
    for ylevel in tqdm(yblocks_levels, desc="Cross level"):
        y_groups = yblocks[ylevel].groupby(yblocks[ylevel])
        for yb, yg in tqdm(y_groups, desc=f"  {ybtype.capitalize()} block"):
            yb_docs = Counter() if ltype == "link" else set()
            for ye in yg.index:
                yb_docs.update(y_documents[ye])
            for level in tqdm(corpus.dblocks_levels, desc="    Doc level"):
                doc_groups = dblocks[level].groupby(dblocks[level])
                for b, g in doc_groups:
                    keys.append((level, b, ylevel, yb))
                    if ltype == "link":
                        g_index = set(g.index)
                        vals.append(sum(v for k, v in yb_docs.items() if k in g_index))
                    else:  # ltype == 'doc'
                        vals.append(len(g.index.intersection(yb_docs)))

    values = pandas.Series(vals, index=pandas.MultiIndex.from_tuples(keys))

    if use_cache:
        print("Storing cross counts")
        ioio.store_pandas(values, fpath)
    return values


def p_diff(a, b):
    return a - b


def p_rel(a, b):
    return a / b
