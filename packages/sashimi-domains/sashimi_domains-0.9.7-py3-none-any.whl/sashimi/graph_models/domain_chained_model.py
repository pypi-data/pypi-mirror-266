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

import numpy
from itertools import count

from ..naming import naming
from ..misc import _try_import
from .util import contiguous_map_nested_blockstate

logger = logging.getLogger(__name__)
gt = _try_import("graph_tool.all")


def calc_chained_nested_blockstate(
    corpus, bext="max", niter=10, strategy=["anneal", "sweep"]
):
    """
    Calculates a chained nested blockstate for vertices derived from
    values of some property of the documents.
    Only works for NestedBlockState without layers or overlapping.
    (corpus)
    (niter) number of times the optimization procedure is run
    (anneal) use annealing for optimization
    :str: file name of stored state
    """
    name_args = []
    if sample := corpus.get_sample_hash(doc=True, ext=True):
        name_args = [*name_args, ("sample", sample)]

    for irun in count():
        fname = naming.gen(
            "chainedbstate",
            [
                ("prop", corpus.graph_extend["prop"]),
                ("matcher", corpus.graph_extend["matcher"]),
                *name_args,
                ("run", irun),
            ],
            corpus.suffix_nbs,
        )
        try:
            (corpus.blocks_dir / fname).mkdir(exist_ok=False)
            print(f"Reserved name: {fname}\n")
            break
        except OSError:
            pass

    print("Generating initial block state\n")
    pclabel = "type"
    nbstate = gen_nbstate(corpus, pclabel, bext)

    print("Starting minimization from initial state:\n", nbstate)
    nbstate = minimize_nbstate(nbstate, strategy)

    fpath = corpus.blocks_dir / fname / fname
    corpus.store_blockstate(fpath, state=nbstate, pclabel=pclabel)
    print("Saved chained state: {}".format(fname))
    corpus.set_blockstate(str(fname), chained=True)
    return fpath


def gen_nbstate(corpus, pclabel, bext):
    g = gen_doc_graph(corpus)
    extend_graph(corpus, g)
    doc_bs = gen_doc_blocks(corpus)
    nbstate = gen_chained_nested_blockstate(g, doc_bs, pclabel=pclabel, bext=bext)
    return nbstate


def minimize_nbstate(nbstate, strategy):
    ent = nbstate.entropy()
    # WARNING: nbstate copies lose hbfields, do not optimize or get entropy on them
    best_nbstate = nbstate.copy()
    for method in strategy:
        if method == "sweep":
            print("Sweeping...")
            for i in range(1000):  # this should be sufficiently large
                nbstate.multiflip_mcmc_sweep(
                    beta=numpy.inf,
                    niter=10,
                    ls=[*range(len(nbstate.levels) - 1)],
                )
        if method == "anneal":
            print("Annealing...")
            gt.mcmc_anneal(
                nbstate,
                beta_range=(1, 10),
                niter=1000,
                mcmc_equilibrate_args=dict(
                    force_niter=10,
                    mcmc_args=dict(ls=[*range(len(nbstate.levels) - 1)]),
                ),
            )
        if nbstate.entropy() < ent:
            ent = nbstate.entropy()
            best_nbstate = nbstate.copy()
    nbstate = contiguous_map_nested_blockstate(best_nbstate)
    return nbstate


def gen_chained_nested_blockstate(g, bs, pclabel, bext="max"):
    """
    (g) Graph: extended graph
    (bs) Sequence[Sequence]: blockstates of doc graph
    (pclabel) Name of vertex property passed down and frozen at < 2
    (bext) str: "max" or "min": entropy of starting state
    :gt.NestedBlockState
    """
    N_frozen = len([None for v in g.vertices() if g.vp[pclabel][v] < 2])
    if N_frozen != len(bs[0]):
        raise ValueError("Parameters `g` and `bs` don't match")
    N_ext = g.num_vertices() - N_frozen

    state_args = {"pclabel": g.vp[pclabel]}

    # Extend bs to match extended graph
    bs = [[*b] for b in bs]
    for level, b in enumerate(bs):
        if level == len(bs) - 1:
            b.append(0)  # just add a new type
        elif level == len(bs) - 2:
            b.extend([max(b) + 1] * N_ext)  # assign all to new type
        else:
            if bext == "max":
                b.extend(range(max(b) + 1, max(b) + 1 + N_ext))
            elif bext == "min":
                b.extend([max(b) + 1] * N_ext)
            else:
                raise ValueError("Unknown value for `bext`.")
    bs = [numpy.array(b) for b in bs]

    # Setup lfrozen and bfield for the base state
    lfrozen = [g.new_vertex_property("bool")]
    bfield = g.new_vertex_property("vector<double>")
    for v in g.vertices():
        if g.vp[pclabel][v] < 2:
            lfrozen[-1][v] = True
            bfield[v] = freeze_in_block(bs[0][int(v)])
    state_args["bfield"] = bfield

    # Instantiate NestedBlockState and propagate bfield upwards
    ns = gt.NestedBlockState(g, bs, **state_args)
    for s_low, s_cur in zip(ns.levels, ns.levels[1:-1]):
        lfrozen.append(s_cur.g.new_vertex_property("bool"))
        for v in s_low.g.vertices():
            if lfrozen[-2][v]:
                lfrozen[-1][s_low.b[v]] = True
        # fmax = max(s_cur.b[int(v)] for v in s_cur.g.vertices() if lfrozen[-1][v])
        for v in s_cur.g.vertices():
            if lfrozen[-1][v]:
                s_cur.bfield[v] = freeze_in_block(s_cur.b[v])
            #  Already guaranteed by `pclabel` in `state_args`
            # else:
            #     s_cur.bfield[v] = (fmax+1)*[-numpy.inf] + [0]
    #  Already guaranteed by `ls` in `multiflip_mcmc_sweep`
    # for v in ns.levels[-1].g.vertices:
    #    ns.levels[-1].bfield[v] = [0, -numpy.inf]

    # NOTE: `NestedBlockState.copy()` does not copy blockgraph bfields.

    return ns


def extend_graph(corpus, g=None, extend=None):
    """
    Adds nodes from another dimension (data column) to the graph.
    Used to calculate a chained blockstate.

    (g) graph to be extended if not corpus.graph
    (extend) prop and matcher, if not corpus.graph_extend
    """
    g = corpus.graph if g is None else g
    extend = corpus.graph_extend if extend is None else extend
    match_keys, get_matches = corpus.make_matcher(extend)
    name2vindex = dict((g.vp["name"][v], v) for v in g.vertices())
    vtype = max(2, max(g.vp["type"]) + 1)
    edge_list = []
    document_ids = corpus.get_document_ids()
    for extvname in match_keys:
        v = g.add_vertex()
        g.vp["type"][v] = vtype
        g.vp["name"][v] = extvname
        matches = get_matches(extvname)
        for docidx in matches:
            doc_vindex = name2vindex[document_ids[docidx]]
            edge_list.append((doc_vindex, v))
    # FIXME graph tool >2.46 will take vertices again
    # g.add_edge_list(edge_list)
    g.add_edge_list((int(x) for x in row) for row in edge_list)
    g._sashimi_extended = extend.copy()


def gen_doc_blocks(corpus):
    """
    Returns the corpus' state's blocks restricted to current documents.
    """
    bs = [numpy.array(b) for b in corpus.state.get_bs()]
    document_ids = {*corpus.get_document_ids()}
    bs[0] = numpy.array(
        [
            corpus.state.levels[0].b[v]
            for v in corpus.state.g.vertices()
            if corpus.state.g.vp["type"][v] == 0
            and corpus.state.g.vp["name"][v] in document_ids
        ]
    )
    bs = contiguous_map_nested_blockstate(bs, True)
    if len(b := bs[-1]) > 1:
        if (b_max := max(b)) > 0:
            bs.append(numpy.array([0] * (b_max + 1)))
        bs.append(numpy.array([0]))
    return bs


def gen_doc_graph(corpus):
    docs = corpus.data.index
    document_ids = corpus.get_document_ids()
    g = gt.Graph(directed=False)
    g.vp["type"] = g.new_vertex_property("int")  # 0: document
    g.vp["name"] = g.new_vertex_property("string")
    g.add_vertex(len(docs))
    for vi, idx in enumerate(docs):
        g.vp["type"][vi] = 0
        g.vp["name"][vi] = document_ids[idx]

    return g


def freeze_in_block(block):
    """
    Returns the bfield value to freeza a vertex at block.
    Meaning with probability 1 at `block` and zero elsewhere (as log probabilities).
    (block) int: the index of a block
    :list(float)
    """
    return block * [-numpy.inf] + [0, -numpy.inf]


def gen_docext_graph(corpus):
    """Unused for now"""
    print(f"Generating doc ext graph for {corpus.graph_extend['prop']}")
    match_keys, get_matches = corpus.make_matcher()

    docs = corpus.data.index
    document_ids = corpus.get_document_ids()
    g = gt.Graph(directed=False)
    g.vp["type"] = g.new_vertex_property("int")  # 0: document, 2:ext
    g.vp["name"] = g.new_vertex_property("string")
    g.add_vertex(len(docs))
    name2vindex = {}
    for vi, idx in enumerate(docs):
        g.vp["type"][vi] = 0
        g.vp["name"][vi] = document_ids[idx]
        name2vindex[g.vp["name"][vi]] = vi
    edge_list = []
    for extvname in match_keys:
        v = g.add_vertex()
        g.vp["type"][v] = 2
        g.vp["name"][v] = extvname
        matches = get_matches(extvname)
        for docidx in matches:
            doc_vindex = name2vindex[document_ids[docidx]]
            edge_list.append((doc_vindex, v))
    g.add_edge_list(edge_list)

    return g
