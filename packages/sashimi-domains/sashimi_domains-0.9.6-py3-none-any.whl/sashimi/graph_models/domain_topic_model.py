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

import logging
from itertools import count

import numpy as np
from tqdm import tqdm

from ..naming import naming
from ..misc import _try_import
from .util import contiguous_map_nested_blockstate

logger = logging.getLogger(__name__)
gt = _try_import("graph_tool.all")


def create_docter_graph(corpus, by=None):
    """
    Creates one or more document term graphs, names it, stores it and
    sets as loaded.

    Parameters
    ----------
    by: name of a column from `corpus.data` or an equivalent `pandas:Series`
      If provided, group documents by this column and create multiple graphs

    Returns
    -------
    names: a `list` containing the names of the graphs created
    """
    name_args = [("kind", "docter"), ("column", corpus.column)]
    if sample := corpus.get_sample_hash(doc=True, ter=True):
        name_args.append(("sample", sample))

    if by is not None:
        name_by = (
            by
            if isinstance(by, str)
            else by.name
            if hasattr(by, "name")
            else by.__name__
        )
        if not name_by:
            raise ValueError

    def get_graph_name(name_args, group_name):
        name_args += [] if by is None else [("by", (name_by, group_name))]
        return naming.gen("graph", name_args, corpus.suffix_g)

    graph_names = []
    for group_name, group in (
        [("all", corpus.data)] if by is None else corpus.data.groupby(by)
    ):
        print(f"Generating doc ter graph for {group_name}")
        graph_name = get_graph_name(name_args, group_name)
        fpath = corpus.data_dir / graph_name / graph_name
        load = False
        try:
            fpath.parent.mkdir(exist_ok=False)
        except FileExistsError:
            print("Found existing graph. Will skip creation, test loading.")
            load = True
        if load:
            g = gt.load_graph(str(fpath))
        else:
            doc_tokens = corpus.data[corpus.column].loc[
                corpus.samplify(group.index, corpus.data[corpus.column])
            ]
            try:
                g = gen_docter_graph(doc_tokens, corpus.get_document_ids())
                g.save(str(fpath))
            except Exception:
                fpath.parent.rmdir()  # dir is ours and we failed, so remove it
                raise
        graph_names.append(graph_name)

    if len(graph_names) == 1:
        corpus.set_graph(graph_names[0])
        print("Graph set to: {}".format(graph_names[0]))
    return graph_names


def gen_docter_graph(doc_tokens, doc_ids):
    """
    Builds a bipartite undirected graph of documents connecting to the terms
    they contain.
    """
    vocab = {w for d in doc_tokens for s in d for w in s}
    print("Vocab size: {}".format(len(vocab)))
    vocabindex = dict((w, n) for n, w in enumerate(vocab))

    g = gt.Graph(directed=False)
    g.vp["type"] = g.new_vertex_property("int")  # type = 0: document, 1: term
    g.vp["name"] = g.new_vertex_property("string")
    g.add_vertex(len(vocab) + len(doc_tokens))
    for w, vi in vocabindex.items():
        g.vp["type"][vi] = 1
        g.vp["name"][vi] = w

    def gen_docter_edges():
        document_ids = doc_ids
        for vi, di in enumerate(
            tqdm(doc_tokens.index, desc="Processing docs"), len(vocab)
        ):
            g.vp["type"][vi] = 0
            g.vp["name"][vi] = document_ids[di]
            for s in doc_tokens[di]:
                for w in s:
                    if w in vocab:
                        yield (vi, vocabindex[w])

    g.add_edge_list(gen_docter_edges())
    return g


def calc_nested_blockstate(corpus, name_args=(), state_args={}):
    """
    Calculate and save a nested blockstate for the graph, using
    `graph_tool.inference.minimize.minimize_nested_blockmodel_dl()`.

    Parameters
    ----------
    g: a `graph_tool.Graph` instance
      If not provided, use the current graph.
    name_args: `list` of 2-tuples
      Extra arguments to add to the blockstate filename.
    state_args: `dict`
      Passed downstream. For key "ec", value is passed as `g.ep[value]`.
    """
    state_args = state_args.copy()

    if sample := corpus.get_sample_hash(doc=True, ter=True):
        name_args = [*name_args, ("sample", sample)]

    for irun in count():
        fname = naming.gen(
            "blockstate",
            [*name_args, ("step", "mnbdl"), ("run", irun)],
            corpus.suffix_nbs,
        )
        try:
            (corpus.graph_dir / fname).mkdir(exist_ok=False)
            print(f"Reserving name: {fname}")
            break
        except OSError:
            pass

    g = corpus.graph
    store_blockstate_args = {"fpath": corpus.graph_dir / fname / fname}
    if "ec" in state_args:
        state_args["base_type"] = gt.LayeredBlockState
        store_blockstate_args["ec"] = state_args["ec"]
        state_args["ec"] = g.ep[store_blockstate_args["ec"]]
        if "layers" in state_args:
            store_blockstate_args["layers"] = state_args["layers"]
    if "type" in g.vp:
        assert "pclabel" not in state_args
        store_blockstate_args["pclabel"] = "type"
        state_args["pclabel"] = g.vp[store_blockstate_args["pclabel"]]
        print('Vertex property "type" found, using it as pclabel')

    print("Starting minimization...")
    state = gt.minimize_nested_blockmodel_dl(g, state_args=state_args)
    state = contiguous_map_nested_blockstate(state)

    corpus.store_blockstate(state=state, **store_blockstate_args)
    print("Saved state: {}".format(fname))
    corpus.loaded["blockstate"] = str(fname)
    return fname


def refine_state(state, strategy="sweep"):
    """
    For the "bestest" results go with ["anneal", "sweep"]
    """
    print("Refining state...")
    if isinstance(strategy, str):
        strategy = [strategy]
    for method in strategy:
        if method == "sweep":
            for i in range(1000):
                state.multiflip_mcmc_sweep(beta=np.inf, niter=10)
        if method == "anneal":
            gt.mcmc_anneal(
                state,
                beta_range=(1, 10),
                niter=1000,
                mcmc_equilibrate_args=dict(force_niter=10),
            )
