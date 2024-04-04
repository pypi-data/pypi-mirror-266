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

from itertools import islice
import logging
import re

import numpy as np

from ..naming import naming
from .annotations import (
    get_xblock_yblocks_elements,
    get_subxblocks_yblocks_elements,
    load_annotations,
)
from ..misc import get_hash, _try_import

logger = logging.getLogger(__name__)
gt = _try_import("graph_tool.all")


def first_element(yb_info_elements):
    return yb_info_elements[0][0] if yb_info_elements else ""


def dblock_terext_graph(
    corpus,
    xbtype,
    doc_level,
    ter_level,
    ext_level,
    *,
    xb_selection=None,
    edges="specific",
):
    xlevel = {"doc": doc_level, "ter": ter_level, "ext": ext_level}[xbtype]
    if edges == "specific":
        annotation_function = get_xblock_yblocks_elements
    elif edges == "common":
        if xlevel == 1:
            raise ValueError(
                f"`edges=common` requires xbtype (here `{xbtype}`) level > 1 (here `{xlevel}`)."
            )
        annotation_function = get_subxblocks_yblocks_elements
    else:
        raise ValueError("`edges` must be one of ['specific', 'common']")

    annotations_ylevel = []
    xb_selection = set(xb_selection)

    if xbtype == "doc":
        if ter_level is not None:
            ter_annotations = load_annotations(
                corpus, annotation_function, "doc", "ter", ter_level
            )
            annotations_ylevel.append((ter_annotations, ter_level))
        if ext_level is not None:
            ext_annotations = load_annotations(
                corpus, annotation_function, "doc", "ext", ext_level
            )
            annotations_ylevel.append((ext_annotations, ext_level))
    else:
        doc_annotations = load_annotations(
            corpus, annotation_function, xbtype, "doc", doc_level
        )
        annotations_ylevel.append((doc_annotations, doc_level))

    g = gt.Graph()
    g.ep["specificity"] = g.new_edge_property("float")
    g.ep["label"] = g.new_edge_property("string")
    vp_label = g.vp["label"] = g.add_edge_list(
        (
            (
                corpus.lblock_to_label[xlevel, xb],
                corpus.lblock_to_label[ylevel, yb],
                yb_info["ent"],
                first_element(yb_info["elements"]),
            )
            for annotations, ylevel in annotations_ylevel
            for xb in annotations[xlevel]
            for yb, yb_info in islice(
                annotations[xlevel][xb]["blocks"].items(), 10
            )  # only 1st 10
            if not xb_selection or xb in xb_selection
        ),
        hashed=True,
        eprops=(g.ep["specificity"], g.ep["label"]),
    )
    vp_labels = {*vp_label}
    for xb in xb_selection:
        xb_label = corpus.lblock_to_label[xlevel, xb]
        if xb_label not in vp_labels:
            vp_label[g.add_vertex()] = xb_label
    vp_type = g.vp["type"] = g.new_vertex_property("string")
    for v in g.vertices():
        vp_type[v] = re.search(r"[DTE]", vp_label[v])[0]

    return g


def network_map(
    corpus,
    xbtype,
    doc_level,
    ter_level=1,
    ext_level=None,
    *,
    xb_selection=None,
    split_on=None,
    split_list=None,
    edges="specific",
):
    """
    (corpus)
    (xbtype)
    (doc_level) display document nodes from this level
    (ter_level) display term nodes from this level
    (ext_level) display chained nodes from this level

    (xb_selection) list of int
        Restrict the network to a list of domains from `doc_level`

    Show a halo on domain nodes for the difference in relative volume
    between those in and out of a set of values such as years:
    (split_on) series of values based on which to split
    (split_list) values from split series to consider positive

    (edges): measure determining edges ("specific" or "common")
    """
    xblocks, xblocks_levels = corpus.get_blocks_levels(xbtype)
    xlevel = {"doc": doc_level, "ter": ter_level, "ext": ext_level}[xbtype]
    arg_xb_selection = xb_selection
    if xb_selection is None:
        xb_selection = xblocks[xlevel]
    xb_selection = np.unique(xb_selection)

    g = dblock_terext_graph(
        corpus,
        xbtype,
        doc_level,
        ter_level,
        ext_level,
        xb_selection=xb_selection,
        edges=edges,
    )
    vp_label = g.vp["label"]

    vp_block = g.new_vertex_property("int")
    for v in g.vertices():
        vp_block[v] = corpus.label_to_tlblock[vp_label[v]][-1]

    vp_type = g.vp["type"]

    g.vp["shape"] = g.new_vertex_property(
        "string",
        [
            "square" if t == "D" else "circle" if t == "T" else "hexagon"
            for t in vp_type
        ],
    )

    g.vp["weight"] = g.new_vertex_property(
        "float",
        (
            3 if vp_type[v] == "D" else 0 if vp_type[v] == "T" else 1
            for v in g.vertices()
        ),
    )
    g.ep["weight"] = gt.prop_to_size(g.ep["specificity"], mi=1)

    # Some data about the corpus to set color and size
    size = (
        corpus.dblocks[doc_level]
        .value_counts()
        .loc[xb_selection if xbtype == "doc" else slice(None)]
        .map(area2radius)
        .pipe(lambda x: x.div(x.max()))
    )
    if split_on is not None:
        period_color_scalar = get_split_fraction_diff_rel(
            corpus, xlevel, xb_selection, split_on, split_list
        )

    vp_size = g.vp["size"] = g.new_vertex_property("float")
    vp_color = g.vp["color"] = g.new_vertex_property("vector<float>")
    vp_fill_color = g.vp["fill_color"] = g.new_vertex_property("vector<float>")
    for v in g.vertices():
        vp_size[v] = 100 if vp_type[v] == "D" else 80
        vp_fill_color[v] = [
            1,
            0,
            0,
            0.8 * size[vp_block[v]] if vp_type[v] == "D" else 0,
        ]
        if vp_type[v] == "D" and split_on is not None:
            color = period_color_scalar[vp_block[v]]
            vp_color[v] = [0, color > 0, color < 0, np.abs(color)]
        elif vp_type[v] == "E":
            vp_color[v] = [0, 0, 0, 1]
        else:
            vp_color[v] = [0, 0, 0, 0]

    g.vp["position"] = gt.sfdp_layout(
        g, eweight=gt.prop_to_size(g.ep["specificity"], mi=0.01, power=1)
    )

    fname_params = [
        ("xbtype", xbtype),
        ("edges", edges),
        ("doc_level", doc_level),
        ("ter_level", ter_level),
        ("ext_level", ext_level),
        (
            "xblocks",
            None
            if arg_xb_selection is None
            else get_hash(tuple(xb_selection.tolist())),
        ),
        ("split_on", getattr(split_on, "name", None)),
        ("split_list", None if split_list is None else get_hash(tuple(split_list))),
    ]
    if sample_hash := corpus.get_sample_hash(doc=True, ter=ter_level, ext=ext_level):
        fname_params = [("sample", sample_hash), *fname_params]

    target_dir = corpus.blocks_adir if ext_level is None else corpus.chained_adir
    fpath_graphml = target_dir / naming.gen("network_map", fname_params, "graphml")
    fpath_pdf = target_dir / naming.gen("network_map", fname_params, "pdf")
    fpath_svg = target_dir / naming.gen("network_map", fname_params, "svg")
    g.save(str(fpath_graphml))
    draw(g, str(fpath_pdf))
    draw(g, str(fpath_svg))

    if False:  # Disable circular layout for now
        gv = circular_layout(g)
        gv.save(
            str(
                target_dir / naming.gen("network_map_circular", fname_params, "graphml")
            )
        )
        draw(
            gv,
            str(target_dir / naming.gen("network_map_circular", fname_params, "pdf")),
        )

    return {"graphml": fpath_graphml, "pdf": fpath_pdf, "svg": fpath_svg}


def get_split_fraction_diff_rel(
    corpus, dlevel, dblocks_selection, split_on, split_list
):
    """
    Show a halo on domain nodes for the difference in relative volume
    between those in and out of a set of values such as years:
    (split_on) series of values based on which to split
    (split_list) values from split series to consider positive

    Example:
    get_split_fraction_diff_rel(
        ...,
        split_on=corpus.data[corpus.col_time],
        split_list=set(corpus.data[corpus.col_time][lambda x: x.ge(2002)])
    )
    """
    index = split_on.index.intersection(
        corpus.dblocks.index[corpus.dblocks[dlevel].isin(set(dblocks_selection))]
    )
    split_on = split_on[index]
    split_on.name = "split_on"
    dblocks = corpus.dblocks.loc[index, dlevel]
    dblocks.name = "dblocks"
    grouped_fractions = (
        dblocks.groupby([split_on, dblocks])
        .count()
        .div(split_on.value_counts(), level="split_on")
    )
    split_fractions = grouped_fractions.groupby(
        [grouped_fractions.index.isin(set(split_list), level="split_on"), "dblocks"]
    ).mean()
    diff_fractions = split_fractions[True].sub(split_fractions[False], fill_value=0)
    diff_fractions_norm = diff_fractions / diff_fractions.abs().max()
    return diff_fractions_norm


def area2radius(area):
    """Domain area, currently squares"""
    return np.sqrt(area)  # np.sqrt(area / np.pi)


def circular_layout(g):
    vp_pos = g.vp["position"]
    vp_type = g.vp["type"]
    vp_pin = g.new_vertex_property("bool", (vp_type[v] == "D" for v in g.vertices()))
    center_x = (lambda x: np.mean([x.max(), x.min()]))(vp_pos.get_2d_array([0])[0])
    center_y = (lambda x: np.mean([x.max(), x.min()]))(vp_pos.get_2d_array([1])[0])
    for v in g.vertices():  # Put origin at center
        vp_pos[v] = [vp_pos[v][0] - center_x, vp_pos[v][1] - center_y]
    for v in g.vertices():  # Send degree-1 topics outwards
        if vp_type[v] == "T" and v.in_degree() < 2:
            vn = next(v.in_neighbours())
            if np.linalg.norm(vp_pos[v].a) < np.linalg.norm(vp_pos[vn].a):
                vp_pos[v] = vp_pos[vn].a - (vp_pos[v].a - vp_pos[vn].a)
    max_norm = max(np.linalg.norm(vp_pos[v].a) for v in g.vertices())
    for v in g.vertices():  # Push domains to an outer rim
        if vp_type[v] == "D":
            norm_ratio = np.linalg.norm(vp_pos[v].a) / max_norm
            old_posv = vp_pos[v].a.copy()
            vp_pos[v] = vp_pos[v].a * (1 / norm_ratio) * 2
            for w in v.out_neighbours():
                if w.in_degree() < 2:
                    # print(vp_pos[v].a - old_posv)
                    vp_pos[w] = vp_pos[w].a + (vp_pos[v].a - old_posv)
                    vp_pos[w] = 1.5 * vp_pos[w].a
    # Redo sfdp with frozen domains
    vp_pos = g.vp["position"] = gt.sfdp_layout(g, pos=vp_pos, pin=vp_pin)
    return gt.GraphView(g, vfilt=lambda v: vp_type[v] != "T" or v.in_degree() > 1)


def draw(g, output_file=None):
    vp = {**g.vp}
    ep = {**g.ep}
    if "weight" in vp:
        vp["pen_width"] = vp["weight"]
    if "label" in vp:
        vp["text"] = vp["label"]
    if "weight" in ep:
        ep["pen_width"] = ep["weight"]
    if "label" in g.ep:
        ep["text"] = ep["label"]
    gt.graph_draw(
        g,
        pos=g.vp.get("position", None),
        vprops={"text_position": -2, "text_color": "black", "font_size": 15, **vp},
        eprops={"font_size": 12, "text_color": "blue", "text_parallel": True, **ep},
        output_size=(3 * 1920, 3 * 1080),
        adjust_aspect=False,
        bg_color="white",
        output=output_file,
    )
