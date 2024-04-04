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

from functools import cache

# from itertools import islice
# import re

import logging

# import numpy as np
import pandas as pd

from .. import GraphModels
from ..misc import _try_import
from .util import phi
from .annotations import make_get_annotations

from .network_map import area2radius, first_element

# from ..naming import naming
# from ..misc import get_hash

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

gt = _try_import("graph_tool.all")

# Characteristic edge threshold
Y_KINDS_ENT_FRAC = {"ter": 0.5, "ext": 0.95}

# Network map colors
COLOR_TRANSPARENT = [0, 0, 0, 0]
COLOR_DOMAIN = [1, 0, 0, 0.8]
COLOR_DOMAIN_PURE = [1, 0, 0, 0]
COLOR_TOPIC = [0, 0, 1, 0.8]
COLOR_TOPIC_PURE = [0, 0, 1, 1]
COLOR_EXTENDED = [0, 0.5, 0, 0.8]
COLOR_EXTENDED_PURE = [0, 0.5, 0, 1]
COLOR_BLACK = [0, 0, 0, 0.8]
COLOR_BLACK_PURE = [0, 0, 0, 1]
BLOCK_SIZE = 50 * 2.5
DOC_ELEMENT_SIZE = BLOCK_SIZE / phi**3
ELEMENT_SIZE = BLOCK_SIZE / phi**2
BLOCK_FONT_SIZE = 12 * 2
ELEMENT_FONT_SIZE = 8 * 2.5
EDGE_FONT_SIZE = 10

# BLOCK_PEN_WIDTH = 3
# ELEMENT_PEN_WIDTH = 3/ / phi


def network_map(
    corpus: GraphModels,
    *,
    block_labels=[],
    elements=[],
    characteristic={},
    doc_edges="specific",
    output_file=None,
):
    node_data = get_node_data(corpus, block_labels, elements, characteristic, doc_edges)
    g = get_graph(corpus, node_data, characteristic, doc_edges)
    g = decorate_graph(g)
    draw_graph(g, output_file)
    return g


def decorate_graph(g: gt.Graph):
    """
    Network map with more flexible node choices:
    - nodes from different levels
    - filter on any node type
    - element (level 0) nodes
    """
    # Vertex properties
    vp_kind = g.vp["kind"]
    vp_level = g.vp["level"]
    vp_volume = g.vp["volume"]
    vp_shape = g.vp["shape"] = g.new_vertex_property("string")
    vp_pen_width = g.vp["pen_width"] = g.new_vertex_property("float")
    vp_color = g.vp["color"] = g.new_vertex_property("vector<float>")
    vp_fill_color = g.vp["fill_color"] = g.new_vertex_property("vector<float>")
    vp_size = g.vp["size"] = g.new_vertex_property("float")
    vp_font_size = g.vp["font_size"] = g.new_vertex_property("float")
    vp_text_color = g.vp["text_color"] = g.new_vertex_property("vector<float>")
    for v in g.vertices():
        if vp_kind[v] not in {"doc", "ter", "ext"}:
            raise ValueError(f"Undefined kind: {vp_kind[v]}")
        vp_pen_width[v] = 1 if vp_level[v] == 0 else 0 if vp_kind[v] == "ter" else 3
        vp_shape[v] = (
            "square"
            if vp_kind[v] == "doc"
            else "circle"
            if vp_kind[v] == "ter"
            else "hexagon"
        )
        if vp_level[v] > 0:
            vp_size[v] = BLOCK_SIZE
            vp_font_size[v] = BLOCK_FONT_SIZE
            if vp_kind[v] == "doc":
                vp_fill_color[v] = [*COLOR_DOMAIN[:-1], COLOR_DOMAIN[-1] * vp_volume[v]]
                vp_color[v] = COLOR_TRANSPARENT
                vp_text_color[v] = COLOR_BLACK_PURE
            elif vp_kind[v] == "ter":
                vp_fill_color[v] = COLOR_TRANSPARENT
                vp_color[v] = COLOR_BLACK
                vp_text_color[v] = COLOR_TOPIC_PURE
            elif vp_kind[v] == "ext":
                vp_fill_color[v] = COLOR_TRANSPARENT
                vp_color[v] = COLOR_EXTENDED
                vp_text_color[v] = COLOR_EXTENDED_PURE
        else:
            vp_font_size[v] = ELEMENT_FONT_SIZE
            vp_fill_color[v] = COLOR_TRANSPARENT
            if vp_kind[v] == "doc":
                vp_size[v] = DOC_ELEMENT_SIZE
                vp_color[v] = COLOR_DOMAIN
                vp_text_color[v] = COLOR_BLACK_PURE
            elif vp_kind[v] == "ter":
                vp_size[v] = ELEMENT_SIZE
                vp_color[v] = COLOR_TRANSPARENT
                vp_text_color[v] = COLOR_TOPIC_PURE
            elif vp_kind[v] == "ext":
                vp_size[v] = ELEMENT_SIZE
                vp_color[v] = COLOR_EXTENDED
                vp_text_color[v] = COLOR_BLACK_PURE  # COLOR_EXTENDED_PURE

    # Edge properties
    ep_specificity = g.ep["specificity"]
    # min_specificity = min(ep_specificity[e] for v in g.edges() if ep_specificity[e] > 0)
    max_specificity = max(
        (ep_specificity[e] for e in g.edges() if ep_specificity[e] > 0), default=0
    )
    ep_pen_width = g.ep["pen_width"] = g.new_edge_property("float")
    ep_sfdp_eweight = g.ep["sfdp_eweight"] = g.new_edge_property("float")
    ep_color = g.ep["color"] = g.new_edge_property("vector<float>")
    ep_text_color = g.ep["text_color"] = g.new_edge_property("vector<float>")
    ep_dash_style = g.ep["dash_style"] = g.new_edge_property("vector<float>")
    ep_end_marker = g.ep["end_marker"] = g.new_edge_property("int")
    ep_start_marker = g.ep["start_marker"] = g.new_edge_property("int")
    for e in g.edges():
        e_target_kind = vp_kind[e.target()]
        e_source_kind = vp_kind[e.source()]
        if e_target_kind == e_source_kind:
            ep_dash_style[e] = [0.2, 0.1, 0.0]
            ep_end_marker[e] = 5
            ep_start_marker[e] = 5
        else:
            ep_end_marker[e] = 1
            ep_start_marker[e] = 0
        if ep_specificity[e] == 0:  # not "doc" -> "ter"
            ep_pen_width[e] = 0.6
            ep_sfdp_eweight[e] = 1
        else:  # "doc" -> "ter"
            ep_pen_width[e] = 10 * ep_specificity[e] / max_specificity
            ep_sfdp_eweight[e] = 0.99 * ep_specificity[e] / max_specificity
        if e_target_kind == "doc":
            if vp_kind[e.source()] == "doc":
                ep_color[e] = COLOR_DOMAIN
            else:
                ep_color[e] = COLOR_BLACK
        elif e_target_kind == "ter":
            ep_color[e] = COLOR_BLACK
            ep_text_color[e] = COLOR_TOPIC_PURE
        elif e_target_kind == "ext":
            ep_color[e] = COLOR_EXTENDED
            ep_text_color[e] = COLOR_EXTENDED_PURE

    g.vp["position"] = gt.sfdp_layout(g, eweight=ep_sfdp_eweight)
    return g


def get_node_data(
    corpus: GraphModels,
    block_labels,
    elements,
    characteristic={},
    doc_edges="specific",
):
    """
    (corpus) a corpus with  some model loaded
    (block_labels) [LxDy, LxTy, LxEy, ...]
    (elements) [doc ids, words, other elements]
    (characteristic) {"kind": None|[level, ...], ...}
        Add nodes for all characteristic kind for given levels
    """
    node_data = pd.DataFrame(
        {
            "kind": pd.Series(dtype="string"),
            "level": pd.Series(dtype="Int8"),
            "id": pd.Series(dtype="string"),
        }
    )

    # Add nodes from given labels and elements
    for block_label in block_labels:
        node_kind, node_level, node_id = corpus.label_to_tlblock[block_label]
        node_data.loc[len(node_data.index)] = [node_kind, node_level, node_id]
    for element in elements:
        node_kind, node_id = element
        node_data.loc[len(node_data.index)] = [node_kind, 0, node_id]

    # Add characteristic blocks for domain nodes as requested
    get_annotations = cache(make_get_annotations(corpus))
    node_kind = "doc"
    for (node_kind, node_level), node_locs in (
        node_data[lambda df: df["kind"].eq("doc") & df["level"].gt(0)]
        .groupby(["kind", "level"])
        .groups.items()
    ):
        for y_kind, y_levels in characteristic.items():
            for y_level in y_levels:
                annotations = get_annotations(
                    node_kind,
                    node_level,
                    y_kind,
                    y_level,
                    doc_edges,
                    ent_frac=Y_KINDS_ENT_FRAC[y_kind],
                )
                for _, node_row in node_data.loc[node_locs, ["id"]].iterrows():
                    for y_id in annotations[node_row["id"]]["blocks"]:
                        node_data.loc[len(node_data.index)] = [y_kind, y_level, y_id]

    return node_data


def get_graph(
    corpus: GraphModels,
    node_data: pd.DataFrame = None,
    characteristic={},
    doc_edges="specific",
) -> gt.Graph:
    """
    Translate nodes, i.e. row elements of the data, into vertices of a graph,
    connecting them with appropriate edges.

    Edges are introduced automatically, connecting nodes by:
    - closest parent to block or element (any level)
    - domain to characteristic blocks of other kinds (levels > 0)
    - document to elements of other kinds (level = 0)

    Links involving nodes not in `node_data` are excluded, so all
    desired nodes must be declared there.

    (node_data: DataFrame[kind, level, id])
    (doc_edges) How links from superdomains to other kinds are added:
        `specific`: characteristic to the domain as a whole
        `common`: characteristic to each of its subdomains

    :g: The graph of node relationships

    """
    node_data.drop_duplicates(inplace=True)
    node_data["vertex"] = pd.Series(dtype=object)
    g = gt.Graph()
    g.vp["kind"] = g.new_vertex_property("string")
    g.vp["level"] = g.new_vertex_property("int")
    g.vp["label"] = g.new_vertex_property("string")
    g.vp["volume"] = g.new_vertex_property("float")
    g.ep["label"] = g.new_edge_property("string")
    g.ep["specificity"] = g.new_edge_property("float")

    # Add vertices from node_data
    for idx, node_row in node_data.iterrows():
        node_vertex = node_data.loc[idx, "vertex"] = g.add_vertex()
        g.vp["kind"][node_vertex] = str(node_row["kind"])
        g.vp["level"][node_vertex] = str(node_row["level"])
        if node_row["level"] > 0:
            g.vp["label"][node_vertex] = corpus.lblock_to_label[
                (node_row["level"], node_row["id"])
            ]
        elif node_row["kind"] == "doc":
            g.vp["label"][
                node_vertex
            ] = ""  # TODO corpus.data.loc[node_row["id"], corpus.col_id]
        else:
            g.vp["label"][node_vertex] = node_row["id"]

    # Add volume information for domain nodes
    for level, group in node_data[
        lambda df: df["kind"].eq("doc") & df["level"].gt(0)
    ].groupby("level"):
        volume = (
            corpus.dblocks[level]
            .value_counts()
            .map(area2radius)
            .pipe(lambda x: x.div(x.max()))
        )
        for _, node_row in group.iterrows():
            g.vp["volume"][node_row["vertex"]] = volume[node_row["id"]]

    # Add edges
    get_annotations = cache(make_get_annotations(corpus))
    for _, node_row in node_data.iterrows():
        node_kind = node_row["kind"]
        node_level = node_row["level"]
        node_id = node_row["id"]
        node_vertex = node_row["vertex"]

        # Hierarchical link from closest block parent to domain or document
        for _, parent in get_parents(node_row, corpus).sort_values("level").iterrows():
            parent = node_data.loc[lambda df: df[parent.index].eq(parent).all(axis=1)]
            if not parent.empty:
                assert len(parent) == 1
                parent_vertex = parent.iloc[0]["vertex"]
                edge = g.add_edge(parent_vertex, node_vertex)
                break

        # Add characteristic links from domains to blocks of other kinds
        # Group by kind+level bc of how load_annotations work
        if node_kind == "doc" and node_level > 0:
            for (y_kind, y_level), y_locs in (
                node_data[lambda df: ~df["kind"].eq("doc") & df["level"].gt(0)]
                .groupby(["kind", "level"])
                .groups.items()
            ):
                if not (y_kind in characteristic and y_level in characteristic[y_kind]):
                    continue
                annotations = get_annotations(
                    node_kind,
                    node_level,
                    y_kind,
                    y_level,
                    doc_edges,
                    ent_frac=Y_KINDS_ENT_FRAC[y_kind],
                )[node_id]["blocks"]
                for _, y_row in node_data.loc[y_locs, ["id", "vertex"]].iterrows():
                    if y_row["id"] in annotations.keys():
                        edge = g.add_edge(node_vertex, y_row["vertex"])
                        g.ep["specificity"][edge] = annotations[y_row["id"]]["ent"]
                        g.ep["label"][edge] = first_element(
                            annotations[y_row["id"]]["elements"]
                        )

        # Add link from documents to elements of other kinds
        if node_kind != "doc" and node_level == 0:
            if node_kind == "ter":
                doc_ids = corpus.data[
                    lambda df: df[corpus.column].map(
                        lambda d: any(w == node_id for s in d for w in s)
                    )
                ].index
            else:
                match_keys, get_matches = corpus.make_matcher()
                doc_ids = get_matches(node_id)
            doc = node_data.loc[
                lambda df: df[["kind", "level"]].eq(["doc", 0]).all(axis=1)
            ].loc[lambda df: df["id"].isin(doc_ids)]
            for _, doc_row in doc.iterrows():
                g.add_edge(doc_row["vertex"], node_vertex)

    return g


def get_parents(node_row: pd.Series, corpus: GraphModels):
    blocks, levels = corpus.get_blocks_levels(node_row["kind"], orig=True)
    if blocks.empty:
        logger.debug(f'No blocks found for kind {node_row["kind"]}')
        return pd.DataFrame(columns=["level"])
    node_level = node_row["level"]
    node_id = node_row["id"]
    blocks, levels = blocks.reset_index(names=0), [0] + levels
    block_row = blocks.loc[lambda df: df[node_level].eq(node_id)].iloc[0]
    parents_row: pd.Series = block_row[levels[levels.index(node_level) + 1 :]]
    parents = parents_row.reset_index(name="id").rename({"index": "level"}, axis=1)
    parents.insert(0, "kind", node_row["kind"])
    return parents


def draw_graph(g, output_file=None):
    vp = {**g.vp}
    ep = {**g.ep}
    pos = vp.pop("position", None)
    if "label" in vp:
        vp["text"] = vp.pop("label")
    if "label" in ep:
        ep["text"] = ep.pop("label")
    gt.graph_draw(
        g,
        pos=pos,
        vprops={"text_position": -2, "text_color": "black", **vp},
        eprops={"font_size": EDGE_FONT_SIZE, "text_parallel": True, **ep},
        output_size=(3 * 1920, 3 * 1080),
        adjust_aspect=False,
        bg_color="white",
        output=output_file,
    )
