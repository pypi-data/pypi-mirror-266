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
from pathlib import Path
import shutil

import numpy

from ..misc import clearattrs, makep_fromdict, property_getfuncdir
from ..ioio import ioio
from ..corpus import Corpus
from ..scorology import Scorology
from ..blocks import Blocks
from ..misc import _try_import

from . import blockstate_to_dataframes
from .domain_topic_model import create_docter_graph, calc_nested_blockstate
from .domain_chained_model import (
    extend_graph,
    gen_doc_graph,
    calc_chained_nested_blockstate,
)

logger = logging.getLogger(__name__)
gt = _try_import("graph_tool.all")


class GraphModels(Blocks, Scorology, Corpus):
    """
    Build graphs from corpora and find optimal block models.
    """

    def __init__(self, *args, **kwargs):
        """
        Call `super()` to set up the stage then add class specifics.
        """
        super().__init__(*args, **kwargs)

        self.set_graph(self._to_load.pop("graph", None), strict=False)
        self.set_blockstate(self._to_load.pop("blockstate", None))
        self.loaded["chainedbstates"] = self._to_load.pop("chainedbstates", {})
        if graph_extend := self._to_load.pop("graph_extend", None):
            self.set_chain(**graph_extend, strict=False)
        else:
            self.unset_chain()
        self.use_cached_annotations = True
        self.use_sampled_annotations = False
        self.use_cached_cross_counts = True

    suffix_g = ".gt.xz"
    suffix_nbs = ".json.xz"

    graph_name = makep_fromdict("loaded", "graph", True, None, None)
    graph_dir = property_getfuncdir(lambda self: self.data_dir / self.graph_name)
    graph_adir = property_getfuncdir(lambda self: self.data_adir / self.graph_name)
    blocks_name = makep_fromdict("loaded", "blockstate", True, None, None)
    blocks_dir = property_getfuncdir(lambda self: self.graph_dir / self.blocks_name)
    blocks_adir = property_getfuncdir(lambda self: self.graph_adir / self.blocks_name)
    graph_extend = makep_fromdict("loaded", "graph_extend", True, None, None)
    graph_extend_name = property(lambda self: str(tuple(self.graph_extend.values())))
    chained_name = property(
        lambda self: self.loaded["chainedbstates"].get(self.graph_extend_name, None)
    )
    chained_dir = property_getfuncdir(lambda self: self.blocks_dir / self.chained_name)
    chained_adir = property_getfuncdir(
        lambda self: self.blocks_adir / self.chained_name
    )

    def load_domain_topic_model(self, load=True):
        """"""
        self.cache_clear(clear_static=True)
        if not self.column:
            raise ValueError
        if not self.blocks_name or not load:
            create_docter_graph(self)
            self.load_graph()
            calc_nested_blockstate(self)
        self.load_blockstate()
        self.blockstate_to_dataframes()
        if self.get_sample_hash(doc=True):
            self.trim_to_sample()
        self.load_ter_documents()

    def load_domain_chained_model(
        self, load=True, bext="max", strategy=["anneal", "sweep"]
    ):
        """"""
        self.cache_clear(clear_static=True)
        if not (self.graph_extend and (load or self.blocks_name)):
            raise ValueError
        self.load_blockstate()
        self.blockstate_to_dataframes()
        if self.get_sample_hash(doc=True):
            self.trim_to_sample()
        if not self.chained_name or not load:
            calc_chained_nested_blockstate(self, bext=bext, strategy=strategy)
        self.load_blockstate(chained=True, keep_blocks=True)
        self.blockstate_to_dataframes()
        self.load_ter_documents()
        self.load_ext_documents()

    ################################################
    # Graph and blockstate methods (TODO move out) #
    ################################################

    def from_corpus_to_convoc(self):
        """
        Builds a bipartite undirected graph of terms connecting to the contexts
        they appear in.

        TODO: perhaps a directed graph where contexts connect back their
        composing terms?

        Parameters
        ----------
        """
        pass

    def annotate_graph(self, g, vprops=[], eprops=[]):
        """
        Add properties to the vertices and edges of the graph

        Parameters
        ----------
        g: `graph_tool:Graph`
        vprops: `list`
          Columns from `self.data`
        eprops: `list`
          Columns from `self.data`

        Returns
        -------
        g: the graph, with added properties
        """
        document_ids = self.get_document_ids()
        for prop in eprops:
            g.vp[prop] = g.new_vertex_property(self.get_col_type(prop))
        for prop in eprops:
            g.ep[prop] = g.new_edge_property(self.get_col_type(prop))
        for v in g.vertices():
            sel = document_ids == g.vp["name"][v]
            (di,) = document_ids[sel]
            for prop in vprops:
                g.vp[prop][v] = self.data.loc[di, prop]
            for e in v.out_edges():
                for prop in eprops:
                    g.ep[prop][e] = self.data.loc[di, prop]
        return g

    def search_slice(self, slicerange, g=None, overlap=False, layers=True):
        slice_col = self.col_time
        if g is None:
            g = gt.load_graph(str(self.graph_dir / self.graph_name))

        g.ep["sliced"] = g.new_edge_property("int")
        for sval in slicerange:
            name_args = [("slice-" + slice_col, sval)]
            print("Slicing at {}".format(sval))
            for e in g.edges():
                g.ep["sliced"][e] = g.ep[slice_col][e] > sval
            calc_nested_blockstate(
                self,
                name_args=name_args,
                overlap=overlap,
                g=g,
                state_args=dict(ec=g.ep["sliced"], layers=layers),
            )

    ######################
    # I/O and conversion #
    ######################

    # Graph

    def list_graphs(self):
        return [
            str(fpath.name)
            for fpath in self.data_dir.iterdir()
            if ioio.uncompressed_suffix(fpath)
            == ioio.uncompressed_suffix(Path(f"_{self.suffix_g}"))
        ]

    def set_graph(self, name=None, strict=True):
        """
        Set graph to be loaded to `name`. Doesn't load the graph.

        name) `str` or `None` (default)
            Graph to set. If none, keep current graph.
        strict) bool
            Check values are valid.
        """
        if strict:
            if name is not None:
                if not (self.data_dir / name / name).is_file():
                    raise ValueError
        self.loaded["graph"] = name

    def load_graph(self, extend=False):
        """
        Loads a graph previously set by `set_graph` into `self.graph`.
        """
        self.clear_graph()
        graph_path = self.graph_dir / self.graph_name
        self.graph = gt.load_graph(str(graph_path))
        if extend:
            self.clear_extended()
            extend_graph(self)
            print(f"Loaded: {self.graph_name} ({self.graph_extend})\n{self.graph}")
        else:
            print(f"Loaded: {self.graph_name}\n{self.graph}")

    def clear_graph(self):
        clearattrs(self, ["graph"])

    def clear_extended(self):
        clearattrs(
            self,
            ["ext_documents"],
        )

    def unset_chain(self):
        self.loaded["graph_extend"] = None

    def set_chain(self, prop, matcher=None, strict=True):
        """
        (prop) column where to match patterns from matcher
        (matcher) path, absolute or relative to `self.resources_dir`
        """
        if strict:
            if prop not in self.data:
                raise ValueError
            if matcher is not None:
                if not (self.resources_dir / matcher).is_file():
                    raise ValueError
        self.loaded["graph_extend"] = {"prop": prop, "matcher": matcher}

    # Blockstate

    def list_blockstates(self):
        blockstate_list = [
            str(fpath.name)
            for fpath in self.graph_dir.iterdir()
            if fpath.name.startswith("blockstate; ") and fpath.is_dir()
        ]
        return sorted(blockstate_list)

    def list_chainedbstates(self):
        params_string = (
            f"prop={self.graph_extend['prop']}; matcher={self.graph_extend['matcher']};"
        )
        chainedbstates_list = [
            str(fpath.name)
            for fpath in self.blocks_dir.iterdir()
            if fpath.name.startswith("chainedbstate; ")
            and fpath.is_dir()
            and params_string in str(fpath)
        ]
        return sorted(chainedbstates_list)

    def load_blockstate(self, chained=False, keep_blocks=False):
        """
        Loads a previously stored blockstate from a json or pickle file.

        The loaded state is found at `self.state`.

        Parameters
        ==========
        chained: loads from `self.blocks_name` if False else `self.chained_name`.
        """
        self.clear_blockstate(keep_blocks=keep_blocks)
        if chained:
            fpath = self.chained_dir / self.chained_name
        else:
            fpath = self.blocks_dir / self.blocks_name
        if ioio.uncompressed_suffix(fpath) == ".pickle":
            assert chained is False
            self.state = ioio.load(fpath, fmt="pickle")
        else:
            obj = ioio.load(fpath, fmt="json")
            args = obj["args"]
            args["bs"] = list(map(numpy.array, args["bs"]))
            if chained:
                graph = gen_doc_graph(self)
                extend_graph(self, graph, obj["graph"]["extended"])
                # We used to store bs data for terms and they would come first in the list
                args["bs"][0] = args["bs"][0][-graph.num_vertices() :]
            else:
                graph = gt.load_graph(str(self.graph_dir / obj["graph"]["name"]))
            for key, val in obj["vp_args"].items():
                if val is not None:
                    args[key] = graph.vp[val]
            for key, val in obj["ep_args"].items():
                if val is not None:
                    args[key] = graph.ep[val]
            if args.get("ec", None) is not None:
                args["base_type"] = gt.LayeredBlockState
            else:
                args.pop("layers", None)
            state_class = getattr(gt.graph_tool.inference, obj["class"])
            self.state = state_class(graph, **args)
            self.extended = obj["graph"]["extended"]
        print(
            f"Loaded: {self.chained_name if chained else self.blocks_name}\n{self.state}"
        )

    def store_blockstate(self, fpath, state=None, pclabel=None, layers=None, ec=None):
        if state is None:
            state = self.state
        obj = {
            "class": type(state).__name__,
            "graph": {
                "name": self.graph_name,
                "extended": getattr(state.g, "_sashimi_extended", {}),
            },
            "args": {
                "bs": list(map(lambda x: list(map(int, x)), state.get_bs())),
                "layers": layers,
            },
            "vp_args": {
                "pclabel": pclabel,
            },
            "ep_args": {"ec": ec},
            "entropy": state.entropy(),
        }
        ioio.store(obj, fpath, fmt="json")
        print(f"Stored: {fpath}")

    def clear_blockstate(self, keep_blocks=False):
        if not keep_blocks:
            clearattrs(
                self,
                [
                    "dblocks",
                    "tblocks",
                    "eblocks",
                    "_orig_dblocks",
                    "_orig_tblocks",
                    "_orig_eblocks",
                ],
            )
        clearattrs(self, ["state"])

    def delete_blockstate(self, blocks_name):
        if blocks_name.startswith("blockstate; "):
            blocks_dir = self.graph_dir / blocks_name
            blocks_adir = self.graph_adir / blocks_name
        if blocks_name.startswith("chainedbstate; "):
            blocks_dir = self.blocks_dir / blocks_name
            blocks_adir = self.blocks_adir / blocks_name
        if blocks_adir.exists():
            shutil.rmtree(blocks_adir)
        shutil.rmtree(blocks_dir)  # delete data last

    def get_blockstate(self, chained=False):
        if chained:
            return self.loaded["chainedbstates"][self.graph_extend_name]
        else:
            return self.loaded["blockstate"]

    def set_blockstate(self, blockstate_name, chained=False):
        """
        (chained) if True, set chained blockstate for current graph extension
        """
        if chained:
            self.loaded["chainedbstates"][self.graph_extend_name] = blockstate_name
        else:
            self.loaded["blockstate"] = blockstate_name

    def set_best_state(
        self, state_list=None, chained=False, delete_non_best=False, index=0
    ):
        """
        Sets the corpus to load the available state with the lowest entropy.

        (chained) searches chained states for current choice of extend
        (delete_non_best) remove all data related to the higher entropy states
        (index) get state with sorted index `index`

        :dict: contains the names and entropies of the available states
        """
        if state_list is None:
            state_list = (
                self.list_chainedbstates() if chained else self.list_blockstates()
            )
        state_ent = {}
        for state in state_list:
            try:
                self.set_blockstate(state, chained)
                self.load_blockstate(chained=chained)
                state_ent[state] = self.state.entropy()
            except Exception:
                print(f"Invalid state: {state}")
        state_ent = dict(sorted(state_ent.items(), key=lambda x: x[1]))
        chosen_state = [*state_ent][index]
        self.set_blockstate(chosen_state, chained)
        self.clear_blockstate()
        if delete_non_best:
            for state in [state for state in state_list if state != chosen_state]:
                self.delete_blockstate(state)
        return state_ent

    def blockstate_to_dataframes(self, nbstate=None):
        return blockstate_to_dataframes.blockstate_to_dataframes(self, nbstate)
