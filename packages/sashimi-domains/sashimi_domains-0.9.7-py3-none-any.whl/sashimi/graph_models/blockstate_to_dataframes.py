import pandas
from ..blocks.util import sorted_hierarchical_block_index


def blockstate_to_dataframes(corpus, nbstate=None):
    """
    state: the blockstate instance to be turned into dataframes indexed at
    documents and terms
    """
    if nbstate is None:
        nbstate = corpus.state
    g = nbstate.g

    df = pandas.DataFrame(index=[g.vp["name"][v] for v in g.vertices()])
    df["v"] = [int(v) for v in g.vertices()]
    df["type"] = [g.vp["type"][v] for v in g.vertices()]
    # dataframe level is blockstate index + 1
    for level_index in range(len(nbstate.levels) - 1):  # treat top blevel later
        blocks = nbstate.project_level(level_index).get_blocks()
        df[level_index + 1] = [blocks[v] for v in g.vertices()]
    # add top blevel if current top vertices don't correspond to "type"
    if len(df[level_index + 1].unique()) > 2:
        level_index += 1
        blocks = nbstate.project_level(level_index).get_blocks()
        df[level_index + 1] = [blocks[v] for v in g.vertices()]

    # make sure top level matches type then replace its values
    top_level = level_index + 1
    if not df.groupby("type")[top_level].agg(set).map(len).eq(1).all():
        raise ValueError("multiple top level blocks for type!")
    if not df.groupby(top_level)["type"].agg(set).map(len).eq(1).all():
        raise ValueError("multiple types for top level block!")
    df[top_level] = df["type"]

    dblocks = df[df["type"].eq(0)].copy()
    tblocks = df[df["type"].eq(1)].copy()
    eblocks = df[df["type"].gt(1)].copy()
    del df

    if tblocks.empty and not eblocks.empty:
        # chained state: only load eblocks, with index starting after other blocks
        self_dblocks = getattr(corpus, "_orig_dblocks", corpus.dblocks)
        for dblocks_l, tblocks_l, eblocks_l in zip(
            self_dblocks, corpus.tblocks, eblocks
        ):
            assert dblocks_l == tblocks_l == eblocks_l
            eblocks_start_num = (
                max(
                    self_dblocks[dblocks_l].max(),
                    corpus.tblocks[tblocks_l].max(),
                )
                - eblocks[eblocks_l].min()
                + 1
            )
            eblocks[eblocks_l] = eblocks[eblocks_l].map(lambda x: x + eblocks_start_num)
        corpus.eblocks = eblocks
    else:
        # align dblocks with data
        document_ids = corpus.get_document_ids()
        corpus.dblocks = dblocks.reindex(document_ids)
        corpus.dblocks.index = corpus.data.index
        corpus.dblocks.dropna(inplace=True)
        # if sampled, also keep _orig_dblocks aligned with original data
        if len(corpus.dblocks) < len(dblocks):
            odata_document_ids = corpus.get_document_ids(corpus.odata)
            if not document_ids.equals(odata_document_ids):
                corpus._orig_dblocks = dblocks.reindex(odata_document_ids)
                corpus._orig_dblocks.index = corpus.odata.index
                corpus._orig_dblocks.dropna(inplace=True)
        # assign remaining blocks and block_levels
        corpus.tblocks, corpus.eblocks = (tblocks, eblocks)
    remove_redundant_levels(corpus)
    gen_block_label_correspondence(corpus)
    gen_mapindex(corpus)


def remove_redundant_levels(corpus):
    for blocks, levels in corpus.get_blocks_levels().values():
        levels_to_remove = []
        for level, down_level in zip(levels[1:], levels):
            if blocks[level].nunique() == blocks[down_level].nunique():
                levels_to_remove.append(level)
        for level in levels_to_remove:
            del blocks[level]
            levels.remove(level)
        # This is not viable but was helping with something...
        # # Top level may have changed so make sure it matches type
        # blocks[levels[-1]] = blocks["type"]


def gen_block_label_correspondence(corpus):
    # corpus.hblock_to_label = {}
    # corpus.label_to_hblock = {}
    corpus.label_to_tlblock = {}
    corpus.lblock_to_label = {}
    for btype, (blocks, levels) in corpus.get_blocks_levels(orig=True).items():
        for level in reversed(levels):
            for i, hblock in enumerate(
                sorted_hierarchical_block_index(blocks, levels, level)
            ):
                lblock = (level, hblock[-1])
                label = "L{}{}{}".format(level, btype[0].upper(), i)
                # corpus.hblock_to_label[hblock] = label
                # corpus.label_to_hblock[label] = hblock
                corpus.label_to_tlblock[label] = (btype, *lblock)
                corpus.lblock_to_label[(level, hblock[-1])] = label


def gen_mapindex(corpus):
    corpus.label_to_mapindex = {}
    corpus.lblock_to_mapindex = {}
    for btype, (blocks, levels) in corpus.get_blocks_levels().items():
        mapindex = 0
        for level in reversed(levels):
            for i, hblock in enumerate(
                sorted_hierarchical_block_index(blocks, levels, level)
            ):
                lblock = (level, hblock[-1])
                label = corpus.lblock_to_label[lblock]
                corpus.label_to_mapindex[label] = mapindex
                corpus.lblock_to_mapindex[lblock] = mapindex
                mapindex += 1
