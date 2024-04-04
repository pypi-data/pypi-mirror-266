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

from pathlib import Path

import colorcet
import numpy as np
import pandas
from tqdm import tqdm

# bokeh
from bokeh import (
    plotting as bkp,
    models as bkm,
    layouts as bkl,
    events as bke,
    io as bio,
)
from bokeh.models.callbacks import CustomJS
from bokeh.transform import transform
from bokeh.models.transforms import CustomJSTransform
from bokeh.models.formatters import DatetimeTickFormatter

from ..naming import naming
from . import zmethods
from .util import (
    sorted_hierarchical_block_index,
    try_time_index,
    is_time_type,
    make_normalization_factor,
    btype_to_name,
    phi,
)
from .annotations import (
    load_annotations,
    get_xblock_xelements,
    get_xblock_docs,
    get_xblock_yblocks_elements,
    get_subxblocks_yblocks_elements,
    get_btype_name,
    prepare_xblock_yblocks_elements,
    make_get_title,
)
from .link_maps import link_maps


def composite_hierarchical_block_map(
    corpus,
    btype,
    zmethod=None,
    norm=None,
    scale="linear",
    bheight="hierarchical",
    link_p_func=None,
    page_title=None,
    disable_features={},
):
    """
    Colormap to display multimodal aggregates at different levels.
    Elements are documents and terms, but also journals, authors, institutions, years.
    Colors can represent volume within or connections between different agregates.

    Colors reflect the z axis, which is calculated from 'zmethod', a member of the
    abstract Zmethod class. See the documentation for that class for more information
    and to define your own functions.

    You may pass a list of two or more btypes, in this case multiple
    colormaps will be displayed using the options given. Options that
    are also lists will then be applied to the corresponing map.
    """

    def as_list(arg):
        return arg if isinstance(arg, list) else [arg] * len(btype)

    # From lists to one parameter dict per hierarchical_block_map
    btype = [btype] if isinstance(btype, str) else btype
    maps_args = [
        {
            "zmethod": zmethods.count if (x := as_list(zmethod)[i]) is None else x,
            "norm": as_list(norm)[i],
            "scale": as_list(scale)[i],
            "bheight": as_list(bheight)[i],
            "annotate": as_list("annotations" not in disable_features)[i],
            "other_btype": next(o_btype for o_btype in btype if o_btype != i_btype),
        }
        for i, i_btype in enumerate(btype)
    ]
    zname = [map_args["zmethod"].__name__ for map_args in maps_args]

    if page_title is None:
        page_title = f'{"|".join(corpus.loaded["data"])}: {len(corpus.data)} documents'

    name_args = "norm", "scale", "bheight"
    fname_params = [
        (key, [maps_args[i][key] for i in range(len(btype))]) for key in name_args
    ]
    if sample_hash := corpus.get_sample_hash(**{x: True for x in btype}):
        fname_params = [("sample", sample_hash), *fname_params]
    fname = naming.gen(
        f"domain_map_{btype}_{zname}",
        fname_params,
        "html",
    )

    # Object shared by all maps
    document_data = bkm.ColumnDataSource(
        {
            "title": corpus.data.reset_index().agg(
                make_get_title(corpus.col_title, corpus.col_url, corpus.col_time),
                axis=1,
            )
        }
    )
    for map_args in maps_args:
        map_args["document_data"] = document_data

    # Produce the hierarchical_block_map for each individual set of parameters
    corpus.cache_clear()
    figs, cbars, nav_buttons, infos = zip(
        *(
            get_hierarchical_block_map(corpus, btype[i], **maps_args[i])
            for i in range(len(btype))
        )
    )

    # Lay out the Bokeh document and save it to disk
    map_layouts = []
    info_layouts = []
    for i, (i_btype, i_fig, i_bar, i_nav_buttons, i_info) in enumerate(
        zip(btype, figs, cbars, nav_buttons, infos)
    ):
        map_row = bkl.row(
            i_fig,
            bkl.column(i_nav_buttons, i_bar, sizing_mode="stretch_height"),
            sizing_mode="stretch_both",
        )
        map_layouts.append(map_row)
        info_column = []
        if i_btype == "doc" and "doc_histogram" not in disable_features:
            print("Building doc histogram")
            try:
                info_column.append(
                    get_doc_histogram(get_doc_histogram_data(corpus), i_fig),
                )
            except Exception as e:
                print(f"Failed to build doc histogram: {repr(e)}")
        if i_btype == "doc" and "multi_histogram" not in disable_features:
            print("Building multi histogram")
            try:
                info_column.append(
                    get_multi_histogram(
                        get_multi_histogram_data(
                            corpus,
                            maps_args[i]["other_btype"],
                        ),
                        i_fig,
                    ),
                )
            except Exception as e:
                print(f"Failed to build term histogram: {repr(e)}")
        info_column.append(bkm.ScrollBox(child=i_info, sizing_mode="stretch_both"))
        info_vbox_rows = {1: ["100%"], 2: ["20%", "80%"], 3: ["19%", "21%", "60%"]}[
            len(info_column)
        ]
        info_vbox = bkm.VBox(
            children=info_column, rows=info_vbox_rows, sizing_mode="stretch_both"
        )
        info_layouts.append(info_vbox)

    help_div = bkm.Div(
        text=(Path(__file__).with_name("hierarchical_block_map_help.html").read_text()),
        sizing_mode="stretch_both",
    )

    selection_mode = bkm.Select(
        value="single",
        options=["single", "multi AND", "multi OR"],
        align="center",
    )
    if "search" not in disable_features:
        doc_fig = figs[btype.index("doc")] if "doc" in btype else None
        print("Building the search box")
        search_widget = get_search_widget(
            corpus, i_btype, i_fig, doc_fig, selection_mode
        )
    else:
        search_widget = bkl.Spacer()
    search_row = bkm.HBox(
        children=[
            bkl.Spacer(),
            search_widget,
            bkl.Spacer(),
        ],
        cols=["25%", "50%", "25%"],
        sizing_mode="stretch_width",
    )

    if len(btype) in (1, 2) and "link_maps" not in disable_features:
        # link figures
        if btype in (["doc", "ter"], ["doc", "ext"]):
            map_d = ["doc", figs[0], corpus.dblocks, corpus.dblocks_levels]
            if btype[1] == "ter":
                map_x = ["ter", figs[1], corpus.tblocks, corpus.tblocks_levels]
                values_x = zmethods.get_cross_counts(corpus, "ter", "link")
            if btype[1] == "ext":
                map_x = ["ext", figs[1], corpus.eblocks, corpus.eblocks_levels]
                values_x = zmethods.get_cross_counts(corpus, "ext", "link")
            for map_s, map_t in ([map_d, map_x], [map_x, map_d]):
                link_maps(
                    corpus,
                    *map_s,
                    *map_t,
                    values=values_x,
                    selection_mode=selection_mode,
                    pfunc=link_p_func,
                )
    figlabels = {"doc": "Domain", "ter": "Topic", "ext": "Chained"}
    if len(btype) in (1, 2):
        # two column single row layout
        mapinfo_row = [
            bkm.Tabs(
                sizing_mode="stretch_both",
                tabs=[
                    bkm.TabPanel(
                        child=map_layouts[i],
                        title="{} map".format(figlabels[btype[i]]),
                    ),
                    bkm.TabPanel(
                        child=info_layouts[j],
                        title="{} info".format(figlabels[btype[j]]),
                    ),
                    bkm.TabPanel(
                        child=bkm.ScrollBox(child=help_div, sizing_mode="stretch_both"),
                        title="Help",
                    ),
                ],
            )
            for i, j in (([0, 1], [1, 0]) if len(btype) == 2 else ([0, 0],))
        ]
        layout_col = [
            search_row,
            mapinfo_row,
        ]
    else:
        # multicolumn two rows layout
        map_row = [
            bkm.TabPanel(child=i_figcol, title="{} map".format(figlabels[i_btype]))
            for i_btype, i_figcol in zip(btype, map_layouts)
        ]
        info_row = [
            bkm.TabPanel(child=i_info, title="{} info".format(figlabels[i_btype]))
            for i_btype, i_info in zip(btype, info_layouts)
        ]
        layout_col = [search_row, map_row, info_row, help_div]

    fdir = corpus.chained_adir if "ext" in btype else corpus.blocks_adir
    bokehjs = dict(mode="inline")
    bkp.output_file(fdir / fname, title=page_title, **bokehjs)

    return bkp.save(bkl.layout(layout_col, sizing_mode="stretch_both"))


def get_hierarchical_block_map(
    corpus,
    btype,
    zmethod,
    norm=None,
    scale="linear",
    bheight="hierarchical",
    annotate=True,
    document_data=None,
    other_btype=None,
):
    """
    This method returns a bokeh.figure and other objects to be further processed.
    """
    blocks, levels = corpus.get_blocks_levels(btype)
    lscape = get_block_level_landscape(corpus, btype, zmethod)

    source = dict(
        (k, [])
        for k in (
            "label",  # block label to display
            "level",  # the block's level
            "x",  # horizontal position of center
            "y",  # vertical position of center
            "height",  # heigth of block
            "z",  # colorscale position of block
            "o_z",  # original colorscale position of block
            "value",  # value to be scaled/normalized into z
            "o_value",  # original value to be scaled/normalized into z
            "doc_terms",  # if 'doc': a list of terms
            "doc_exts",  # if 'doc': a list of elements
            "xb_elements",  # if not 'doc': elements and their occurrences
            "documents",  # list of integers representing document for block
            "count",  # number of elements in block
        )
    )
    b2h = {(): 1}  # maps hblock to height, used when bheight=="hierarchical"
    color_p = get_color_params(btype)

    # Load document annotations
    if annotate:
        doc_annotations = get_doc_annotations(corpus) if btype == "doc" else None

    for level in tqdm(
        reversed(levels), total=len(levels), desc=f"{btype.capitalize()} level"
    ):
        # level total height
        if bheight == "procount":
            h_sum = len(blocks[level])
        elif bheight == "proval":
            h_sum = lscape[level].sum()
        else:
            h_sum = 1
        h_cum = 0

        # level nomalization factor
        lscape_scaled = lscape[level].apply(np.log) if scale == "log" else lscape[level]
        znorm = make_normalization_factor(norm)(lscape_scaled)

        hxbindex = sorted_hierarchical_block_index(blocks, levels, level)
        for hxb in tqdm(hxbindex, desc=f" L{level}{btype[0].upper()} blocks"):
            xb = hxb[-1]
            count = (blocks[level] == xb).sum()
            val = lscape[level].loc[xb]
            if np.isnan(val):  # happens in some 0/0 cases so put 1
                val = 1
            zval = (
                np.log(val) / znorm if scale == "log" else val / znorm
            )  # scale and normalize val

            # block height
            if bheight == "procount":
                h_block = count / h_sum
            elif bheight == "proval":
                h_block = val / h_sum
            elif bheight == "hierarchical":
                num_same_parent = (
                    1
                    if len(hxb) == 1
                    else blocks.loc[
                        blocks[levels[levels.index(level) + 1]].eq(hxb[-2]), level
                    ]
                    .unique()
                    .size
                )
                h_block = b2h[hxb[:-1]] / num_same_parent
                b2h[hxb] = h_block

            # data for this block
            source["level"].append(level)
            source["x"].append(levels.index(level) + 1)
            source["y"].append(h_cum + h_block / 2)
            source["height"].append(h_block)
            source["label"].append(f"{corpus.lblock_to_label[level, xb]}")
            source["count"].append(count)
            source["value"].append(val)
            source["z"].append(zval)
            h_cum += h_block

            # add block annotations
            if annotate:
                annotate_block(
                    corpus, btype, level, xb, source, blocks, doc_annotations
                )

    fig, colorbar, labels = get_hbm_figure_and_colorbar(btype, source, color_p)
    info_box = get_info_box(
        btype,
        fig,
        document_data,
        other_btype,
        annotate,
        hasattr(corpus, "ext_documents"),
    )
    nav_buttons = get_hbm_nav_buttons(fig, btype, labels)
    hbm_add_wheel_zoom(btype, fig, labels)
    hbm_add_pan_tool(fig, labels)
    fig.add_tools(bkm.TapTool(behavior="select"))

    return fig, colorbar, nav_buttons, info_box


def get_doc_annotations(corpus):
    annotations = {}
    if hasattr(corpus, "ter_documents"):
        annotations["ter"] = {
            "specific": load_annotations(
                corpus, get_xblock_yblocks_elements, "doc", "ter"
            ),
            "common": load_annotations(
                corpus, get_subxblocks_yblocks_elements, "doc", "ter"
            ),
        }
    if hasattr(corpus, "ext_documents"):
        annotations["ext"] = {
            "specific": load_annotations(
                corpus, get_xblock_yblocks_elements, "doc", "ext"
            ),
            "common": load_annotations(
                corpus, get_subxblocks_yblocks_elements, "doc", "ext"
            ),
        }
    return annotations


def get_hbm_transforms(source, fig):
    transforms = {}

    # trivial
    transforms["format_number"] = CustomJSTransform(  # field: value
        v_func="""
        return xs.map(value => value.toPrecision(2) + " ")
        """
    )

    # positioning
    transforms["x_block_right"] = CustomJSTransform(  # field: x
        v_func="""
        return xs.map(x => x - 0.46)
        """
    )
    transforms["x_block_left"] = CustomJSTransform(  # field: x
        v_func="""
        return xs.map(x => x + 0.46)
        """
    )
    transforms["y_block_bottom"] = CustomJSTransform(  # field: y
        args=dict(source=source, fig=fig),
        v_func="""
        const h = source.data["height"]
        const delta = fig.y_range.end - fig.y_range.start
        const pixels_in_line = fig.frame_height / 41
        const lines_in_frame = fig.frame_height / pixels_in_line
        const lines_per_height = lines_in_frame / delta
        return xs.map(function (y, i) {
            if ((y - h[i] / 2 < fig.y_range.start)
                && (y + h[i] / 2 > fig.y_range.start + 1 / lines_per_height)) {
                return fig.y_range.start + 0.005 * delta
            }
            return y - h[i] / 2 + 0.005 * delta
        })
        """,
    )
    transforms["y_block_top"] = CustomJSTransform(  # field: y
        args=dict(source=source, fig=fig),
        v_func="""
        const h = source.data["height"]
        const delta = fig.y_range.end - fig.y_range.start
        return xs.map(function (y, i) {
            if ((y + h[i] / 2 > fig.y_range.end) && (y - h[i] / 2 < fig.y_range.end)) {
                return fig.y_range.end - 0.005 * delta
            }
            return y + h[i] / 2 - 0.005 * delta
        })
        """,
    )

    # sizes and colors
    transforms["font_size_height_threshold"] = CustomJSTransform(  # field: height
        args=dict(fig=fig),
        v_func="""
        const delta = fig.y_range.end - fig.y_range.start
        return xs.map(height => fig.frame_height * height / delta > 13 ? "1em" : "0em")
        """,
    )
    transforms["contents_font_size"] = CustomJSTransform(  # field: height
        args=dict(fig=fig),
        v_func="""
        const delta = fig.y_range.end - fig.y_range.start
        return xs.map(height => fig.frame_height * height / delta > 30 ? "1em" : "0em")
        """,
    )
    transforms["line_width"] = CustomJSTransform(  # field: height
        args=dict(fig=fig),
        v_func="""
        return xs.map(height => (fig.frame_height * height > 39) ? 1 : 0.001)
        """,
    )
    transforms["map_text_color"] = CustomJSTransform(  # field: z
        v_func="""
        return xs.map(z => (isFinite(z) || z > 0) ? "black" : "grey")
        """,
    )

    # contents
    transforms["label_text"] = CustomJSTransform(  # field: label
        # TODO: no longer needed since removal of hxb from label
        v_func="""
        return xs.map(label => label)
        """
    )
    transforms["count_text"] = CustomJSTransform(  # field: count
        v_func="""
        return xs.map(count => count + " ")
        """,
    )
    process_items_js = """ // args: xs, source, fig
        const h = source.data["height"]
        const y = source.data["y"]
        const delta = fig.y_range.end - fig.y_range.start
        const pixels_in_line = fig.frame_height / 41
        const lines_in_frame = fig.frame_height / pixels_in_line
        const lines_per_height = lines_in_frame / delta
        const height_taken = 1 / lines_per_height + 2 * 0.005 * delta
//        const a = (fig.frame_height * 30 / 650) / delta
//        const b = (fig.frame_height * 30 / 650) * (1 / 30)
        function process_items (items, i) {
            const height_in_frame = Math.max(
               0,
               Math.min(y[i] + h[i] / 2, fig.y_range.end)
               - Math.max(y[i] - h[i] / 2, fig.y_range.start)
            )
            const num_elements = (
                height_in_frame
                ? Math.max(
                    0, Math.round((height_in_frame - height_taken) * lines_per_height))
                : 0
            )
            const sel = (
                items.slice(0, num_elements).map(
                    ([x0, ...x_rest], i) =>
                    x_rest.length > 1 ? (x0[0] == "L" ? "　" + x0 : x0)
                    : (x0.length > 17 ? x0.slice(0, 17) + "…" : x0)
                )
            )
            if (sel.length < items.length) {
                sel[sel.length - 1] = "︙"
            }
            return sel.join("\\n")
    }
    """
    transforms["short_contents_nondoc_text"] = CustomJSTransform(  # field: xb_elements
        args=dict(source=source, fig=fig),
        v_func=process_items_js
        + """
        return xs.map(process_items)
        """,
    )
    transforms["short_contents_doc_text"] = CustomJSTransform(  # field: doc_terms
        args=dict(source=source, fig=fig),
        v_func=process_items_js
        + """
        function preprocess_items (_items, i) {
            const items = [..._items]
            const [btype, ent] = items[0]
            const level_is_1 = source.data["level"][i] == 1
            const title = `${level_is_1 ? "≏" : "⋂"} ${Math.pow(2, ent).toPrecision(2)}`
            if (items.length > 1) {
                items.shift()
                items[0] = [`${title}　⁄　${items[0][0]}`, ...items[0].slice(1)]
            } else {
                items[0] = [`${title}`, ...items[0].slice(1)]
            }
            return items
        }
        let res = xs.map(preprocess_items)
        if (source.data.hasOwnProperty("doc_exts")) {
            const pre = source.data["doc_exts"].map(preprocess_items)
            res = res.map((x, i) => x.concat(pre[i]))
        }
        return res.map(process_items)
        """,
    )
    return transforms


def get_hbm_figure_and_colorbar(btype, source_data, color_p):
    fig = bkp.figure(
        toolbar_location=None,
        tools="",
        sizing_mode="stretch_width",
        frame_height=900,  # TODO: stretch vertically
        min_border_right=0,
        x_range=(max(source_data["x"]) + 0.5, min(source_data["x"]) - 0.5),
        y_range=bkm.Range1d(0, 1, bounds="auto", max_interval=1),
        x_axis_label="level",
        y_axis_label=(get_btype_name(btype) + " blocks").strip(),
    )
    fig.grid.visible = False
    fig.xaxis[0].ticker.desired_num_ticks = len(set(source_data["x"]))
    fig.xaxis[0].major_label_overrides = dict(
        zip(source_data["x"], (str(x) for x in source_data["level"]))
    )
    fig.xaxis.minor_tick_line_color = None
    fig.yaxis.major_label_text_font_size = "0px"
    fig.yaxis.major_tick_line_color = None
    fig.yaxis.minor_tick_line_color = None

    # Used in link_maps()
    source_data["o_z"] = source_data["z"].copy()
    source_data["o_value"] = source_data["value"].copy()

    # remove unused columns and instantiate datasource
    for key in [k for k in source_data if not len(source_data[k])]:
        source_data.pop(key)
    source = bkm.ColumnDataSource(data=source_data, name="{}_map_data".format(btype))

    transforms = get_hbm_transforms(source, fig)

    # plot the glyphs
    fig.rect(
        "x",
        "y",
        width=1,
        height="height",
        source=source,
        line_width={"field": "height", "transform": transforms["line_width"]},
        line_color=color_p["line_color"],
        fill_color={"field": "z", "transform": color_p["cmap"]},
        selection_line_width=4.0,
        selection_line_color=color_p["selection_line_color"],
        nonselection_alpha=1.0,
    )
    fig.add_layout(
        label_block := bkm.LabelSet(
            text=transform("label", transforms["label_text"]),
            x=transform("x", transforms["x_block_right"]),
            y=transform("y", transforms["y_block_bottom"]),
            text_baseline="bottom",
            text_align="right",
            text_font_size=transform(
                "height", transforms["font_size_height_threshold"]
            ),
            text_color=transform("z", transforms["map_text_color"]),
            source=source,
            level="annotation",
        )
    )
    fig.add_layout(
        label_value := bkm.LabelSet(
            text=transform("value", transforms["format_number"]),
            x=transform("x", transforms["x_block_left"]),
            y=transform("y", transforms["y_block_bottom"]),
            text_baseline="bottom",
            text_align="left",
            text_font_size=transform(
                "height", transforms["font_size_height_threshold"]
            ),
            text_color=transform("z", transforms["map_text_color"]),
            source=source,
            level="annotation",
        )
    )
    fig.add_layout(
        label_count := bkm.LabelSet(
            text=transform("count", transforms["count_text"]),
            x="x",
            y=transform("y", transforms["y_block_bottom"]),
            text_baseline="bottom",
            text_align="center",
            text_font_size=transform(
                "height", transforms["font_size_height_threshold"]
            ),
            text_color=transform("z", transforms["map_text_color"]),
            source=source,
            level="annotation",
        )
    )
    if btype == "doc":
        fig.add_layout(
            label_contents := bkm.LabelSet(
                text=transform("doc_terms", transforms["short_contents_doc_text"]),
                x=transform("x", transforms["x_block_left"]),
                y=transform("y", transforms["y_block_top"]),
                text_baseline="top",
                text_align="left",
                text_font_size=transform("height", transforms["contents_font_size"]),
                text_color=transform("z", transforms["map_text_color"]),
                # x_offset=5,
                # y_offset=5,
                source=source,
                level="annotation",
            )
        )
    if btype != "doc":
        fig.add_layout(
            label_contents := bkm.LabelSet(
                text=transform("xb_elements", transforms["short_contents_nondoc_text"]),
                x=transform("x", transforms["x_block_left"]),
                y=transform("y", transforms["y_block_top"]),
                text_baseline="top",
                text_align="left",
                text_font_size=transform("height", transforms["contents_font_size"]),
                text_color=transform("z", transforms["map_text_color"]),
                # x_offset=5,
                # y_offset=5,
                source=source,
                level="annotation",
            )
        )

    # colorbar as an independent figure
    colorbar = bkp.figure(
        toolbar_location=None,
        tools="",
        sizing_mode="stretch_height",
        outline_line_color=None,
        min_border_left=0,
        margin=(0, 0, 30, 0),
        width=66,
    )
    cbar = bkm.ColorBar(color_mapper=color_p["cmap"])
    cbar.major_label_text_font_size = "0em"
    colorbar.add_layout(cbar, "right")

    # Pass this on to ensure transforms get updated when zooming
    labels = {
        "block": label_block,
        "value": label_value,
        "count": label_count,
        "contents": label_contents,
    }
    return fig, colorbar, labels


def get_block_level_landscape(corpus, btype, zmethod, zby=None, zrel=None, zargs={}):
    """
    Applies zmethod over all blocks for each level.

    Parameters
    ----------
    btype: string
        What kind of block to apply to (doc, ter, ext)
    zmethod: function
        The function which returns the series of values for a level.
    zrel: 2-tuple of named pandas indexes
        Calculate values for the first index relative to the second.
    zby: object to groupby
        Splits blocks into subgroups and evaluate consecutive pairs.
    zargs: dict
        Extra arguments passed to `zmethod`.

    Returns
    -------
    lscape: dict of pandas.DataFrames
        for each level, the series of values over its blocks.
    """
    blocks, levels = corpus.get_blocks_levels(btype)

    lscape = dict()

    if zrel is not None:
        for level in levels:
            lidx = blocks[level].unique()
            lscape[level] = zmethod(zrel[0], zrel[1], **zargs)(
                corpus, blocks, level, lidx
            )
        return lscape

    elif zby is not None:
        idxs = []
        for gname, g in corpus.data.groupby(zby):
            g.index.name = gname
            idxs.append(g.index)
        for level in levels:
            lscape[level] = pandas.DataFrame(index=blocks[level].unique())
            for idx0, idx1 in zip(idxs[1:], idxs):
                lscape[level][(idx0.name, idx1.name)] = zmethod(idx0, idx1, **zargs)(
                    corpus, blocks, level, lscape[level].index
                )
        return lscape

    else:
        for level in levels:
            lidx = blocks[level].unique()
            lscape[level] = zmethod(corpus, blocks, level, lidx)
        return lscape


def annotate_block(corpus, xbtype, xlevel, xb, source, sblocks, doc_annotations):
    # reset index to match bokeh datasource index
    data = corpus.data.reset_index()
    if xbtype == "doc":
        # doc_terms and doc_exts
        kind = "specific" if xlevel == 1 else "common"
        source["doc_terms"].append(
            prepare_xblock_yblocks_elements(
                corpus.lblock_to_label, doc_annotations["ter"][kind][xlevel][xb]
            )
        )
        if hasattr(corpus, "ext_documents"):
            source["doc_exts"].append(
                prepare_xblock_yblocks_elements(
                    corpus.lblock_to_label, doc_annotations["ext"][kind][xlevel][xb]
                )
            )
        documents = data.loc[sblocks[xlevel].eq(xb).values].index.to_series()
        num_documents = len(documents) if xlevel == 1 else min(len(documents), 23)
        documents = documents.sample(num_documents)
    else:  # xb_elements
        num_elements = None if xlevel == 1 else 23
        xb_elements = get_xblock_xelements(
            corpus, xbtype, xlevel, xb, "frequency", "doc", num_elements, sblocks
        )
        source["xb_elements"].append(xb_elements)
        documents = data.loc[
            corpus.data.index.isin(get_xblock_docs(corpus, xbtype, xlevel, xb, n=23))
        ].index.to_series()
    if corpus.col_time:
        documents = documents.sort_index(key=data[corpus.col_time].get, kind="stable")
    source["documents"].append(documents)


def get_color_params(btype):
    palette_color = (
        colorcet.b_diverging_bwr_40_95_c42[128:]
        if btype == "doc"
        else list(reversed(colorcet.b_diverging_bwr_40_95_c42[:128]))
        if btype == "ter"
        else list(reversed(colorcet.b_diverging_gwr_55_95_c38[:128]))
        if btype == "ext"
        else None
    )
    palette = colorcet.dimgray[124:-4] + palette_color
    selection_line_color = {
        "doc": "slateblue",
        "ter": "firebrick",
        "ext": "firebrick",
    }[btype]
    cmap_low, cmap_high = -1, 1
    cmap = bkm.LinearColorMapper(
        palette,
        low=cmap_low,
        high=cmap_high,
        high_color="violet",
        low_color="black",
    )
    line_color = "black" if "#ffffff" in palette else "white"

    return dict(
        cmap=cmap,
        line_color=line_color,
        selection_line_color=selection_line_color,
    )


def get_info_box(
    btype, fig, document_data, other_btype, annotate, has_chained_elements
):
    source = fig.select_one("{}_map_data".format(btype))

    # HTML templates
    # Label and numbers
    head_html = f"""
    <div style="display: flex; justify-content: space-between">
        <div><span style="color:#3333dd">block:</span> {{label}}</div>
        <div><span style="color:#3333dd">{btype_to_name(btype, plural=True)}:</span>
             {{count}}</div>
        <div><span style="color:#3333dd">map value:</span> {{value}}</div>
        <!-- <div><span style="color:#3333dd">color:</span> {{z}}</div> -->
    </div>
    """
    # Terms and other
    info_term_html = """<div>"""
    if btype == "doc":
        doc_ybtypes = ["""<div>{doc_terms}</div>"""]
        if has_chained_elements:
            doc_ybtypes.extend(["""<br />""", """<div>{doc_exts}</div>"""])
        if other_btype == "ext":
            doc_ybtypes = reversed(doc_ybtypes)
        info_term_html += """\n""".join(doc_ybtypes)
    else:
        element_label = get_btype_name(btype, True)
        info_term_html += f"""
            <div style="color:#3333dd">{{top}} {element_label} (occurrences):</div>
            <div>{{xb_elements}}</div>
        """
    info_term_html += "</div>"
    # Titles
    title_html = """
    <div>
        <span style="color:#3333dd">{sample} titles:</span><br />{titles}
    </div>
    """

    if not annotate:
        info_term_html = title_html = ""
    info_box_wrap = """{}<br />{}<br />{}"""
    info_box_html = info_box_wrap.format(head_html, info_term_html, title_html)
    info_box = bkm.Div(
        text="<br />I suggest you try clicking on a block. 😉",
        sizing_mode="stretch_both",
        styles={"font-size": "1.3em"},
        stylesheets=[bkm.InlineStyleSheet(css=".bk-clearfix {width: 100%};")],
    )
    info_box_cb = CustomJS(
        args=dict(
            btype=btype,
            source=source,
            info_box=info_box,
            info_box_html=info_box_html,
            document_data=document_data,
            colors=colorcet.glasbey_dark[1:],
            other_btype=other_btype,
        ),
        code=r"""
    const texts = []
    for (const index of source.selected.indices) {
        const level_is_1 = source.data["level"][index] == 1
        const info_box_text = info_box_html.replace(
            /{[\A-z ]*}/g,
            function(key) {
                key = key.slice(1, -1)
                if (key == "sample") {
                    return ((btype == "doc") && level_is_1) ? "All" : "Sample"
                }
                if (key == "top") {
                    return level_is_1 ? "All" : "Top"
                }
                if (key == "titles") {
                    const val = source.data["documents"][index]
                    const documents_title = document_data.data["title"]
                    return [...val].map(x => documents_title[x]).join("<br/><br/>")
                } else if (['value', 'z'].includes(key)) {
                    const val = source.data[key][index]
                    const y = String(val).match(/-?\d+\.\d{4}/)
                    if (y) { return y[0] }
                } else if (key == "xb_elements") {
                    const val = source.data[key][index]
                    return (
                        val.map(x => x[0] + " <small>(" + x[1] + ")</small>")
                        .join(", ") + "."
                    )
                } else if (["doc_terms", "doc_exts"].includes(key)) {
                    let val = [...source.data[key][index]]
                    let label_n = 0
                    val = val.map(v =>
                        v.length == 3 && label_n < 5
                          && key.slice(4, 7) == other_btype
                        ? [`<span style="color: ${colors[label_n++]}; `
                          + `font-weight: bold">${v[0]}</span>`, v[1], v[2]]
                        : v)
                    const [btype, ent] = val.shift()
                    const btype_name = (btype == "ter") ? "terms" : "elements"
                    let title = (level_is_1 ? "≏ Specific " : "⋂ Common ") + btype_name
                    title = `<span style="color:#3333dd">${title}</span>
                             <small>(${Math.pow(2, ent).toPrecision(2)})</small> `
                    return val.reduce(
                        (a, v) => (
                            (v.length == 3) ? `${a.slice(0, -1)}<br />${v[0]}:` : `${a} ${v[0]},`
                        ),
                        title,
                    ).slice(0, -1)
                }
                return source.data[key][index]
            }
        )
        texts.push(info_box_text)
    }
    if (texts.length){
        info_box.text = texts.join("<hr>")
    }
    else {
        info_box.text = "<br />I suggest you try clicking on a block. 😉"
    }
        """,
    )
    source.selected.js_on_change("change:indices", info_box_cb)
    source.js_on_change("change:data", info_box_cb)

    return info_box


def hbm_add_hover_tool(btype, fig, annotate, has_chained_elements):
    """
    Unused as we now display the same information on top of the blocks
    """

    head_html = """<span style="color:#3333dd">block:</span> {label}"""

    tooltip_num_html = """
        <span style="color:#3333dd">value:</span> @value{{0,0.0[00]}}
        <span style="color:#3333dd">color:</span> @z{{0,0.0[00]}}
        <span style="color:#3333dd">count:</span> @count"""
    if btype == "doc":
        tooltip_term_html = """{doc_terms}"""
        if has_chained_elements:
            tooltip_term_html += """<br />{doc_exts}"""
    else:
        element_label = get_btype_name(btype, True)
        tooltip_term_html = f"""
            <span style="color:#3333dd">{element_label} (occurrences):</span>
            <div style="max-height:10em; overflow:hidden;">
            {{xb_elements}}</div>"""
    if not annotate:
        tooltip_term_html = ""
    tooltip_wrap = """<div style="max-width: 450px; padding: 5px; font-size: 1.3em">
        <div>{}<br />{}<br />{}</div></div>"""
    tooltip_sub = dict(
        label="@label",
        doc_terms="@doc_terms{safe}",
        doc_exts="@doc_exts{safe}",
        xb_elements="@xb_elements{safe}",
    )
    tooltip_html = tooltip_wrap.format(
        head_html, tooltip_num_html, tooltip_term_html
    ).format(**tooltip_sub)
    fig.add_tools(
        bkm.HoverTool(
            point_policy="follow_mouse",
            tooltips=tooltip_html,
            attachment="horizontal",
            formatters={
                "@xb_elements": bkm.CustomJSHover(
                    code="""return String(value.map(x => x[0]).join(", "))"""
                )
            },
        )
    )


def hbm_add_wheel_zoom(btype, fig, labels):
    source = fig.select_one("{}_map_data".format(btype))

    wheelzoom_tool = bkm.WheelZoomTool(
        dimensions="height",
        maintain_focus=False,
        zoom_on_axis=True,
    )
    fig.add_tools(wheelzoom_tool)
    fig.toolbar.active_scroll = wheelzoom_tool
    fig.add_tools(bkm.HoverTool(tooltips=None))  # Need hover to inspect
    wheelzoom_callback = CustomJS(
        args=dict(source=source, labels=[*labels.values()]),
        code="""
        const plot = cb_obj.origin
        // if(plot.y_range.start < 0){ plot.y_range.start = 0; }
        // if(plot.y_range.end > 1){ plot.y_range.end = 1; }
        const index = plot.renderers[0].data_source.inspected.indices[0]
        const data = source.data
        if (index == undefined) {
            plot.y_range.start = 0; plot.y_range.end = 1;
        } else {
            const iheight = data.height[index];
            const iend = data.y[index] + iheight/2;
            const istart = data.y[index] - iheight/2;
            if(plot.y_range.start > istart){ plot.y_range.start = istart; }
            if(plot.y_range.end < iend){ plot.y_range.end = iend; }
        }
        for (const label of labels) { label.change.emit() }
        """,
    )
    fig.js_on_event(bke.MouseWheel, wheelzoom_callback)


def hbm_add_pan_tool(fig, labels):
    """TODO: pinch to zoom bokeh bug: https://github.com/bokeh/bokeh/issues/12731"""
    pan_tool = bkm.PanTool(
        dimensions="height",
    )
    fig.add_tools(pan_tool)
    fig.toolbar.active_drag = pan_tool
    pan_callback = CustomJS(
        args=dict(labels=[*labels.values()]),
        code="""
        for (const label of labels) { label.change.emit() }
        """,
    )
    fig.js_on_event(bke.Pan, pan_callback)


def get_search_widget(corpus, xbtype, xfig, dfig, selection_mode):
    # Block search tool
    xsource = xfig.select_one("{}_map_data".format(xbtype))
    dsource = dfig.select_one("doc_map_data")
    xblocks, _ = corpus.get_blocks_levels(xbtype)
    dblocks, _ = corpus.get_blocks_levels("doc")

    # Build completion list
    completions = []
    term_to_mapindex = {
        k: corpus.lblock_to_mapindex[(1, v)] for k, v in xblocks[1].items()
    }
    completions.extend(f"/ {term}" for term in sorted(term_to_mapindex))
    # doc_to_mapindex = {
    #     k: corpus.lblock_to_mapindex[(1, v)]
    #     for k, v in dblocks[1].items()
    # }
    # completions.extend(f"/i {id_}" for id_ in sorted(doc_to_mapindex))
    title_to_mapindices = {
        title: [corpus.lblock_to_mapindex[(1, dblocks.loc[idx, 1])] for idx in idxs]
        for title, idxs in corpus.data.groupby(corpus.col_title).groups.items()
    }
    completions.extend(f"/d {title}" for title in sorted(title_to_mapindices))
    completions.extend(
        "/b " + corpus.lblock_to_label[_level, _block]
        for _btype in (xbtype, "doc")
        for _blocks, _levels in [corpus.get_blocks_levels(_btype)]
        for _level in _levels
        for _block in _blocks[_level].unique()
    )

    searchbox = bkm.AutocompleteInput(
        placeholder=(
            "🔍 Find blocks: enter text to see choices,"
            " shown preceded by '/' for terms, '/b' for labels, '/d' for titles"
            "(Press ESC to unselect all)"
        ),
        completions=sorted(completions),
        max_completions=128,
        case_sensitive=False,
        search_strategy="includes",
        sizing_mode="stretch_width",
        align="center",
    )
    searchbox_cb = CustomJS(
        args=dict(
            xsource=xsource,
            term_to_mapindex=term_to_mapindex,
            dsource=dsource,
            label_to_mapindex=corpus.label_to_mapindex,
            title_to_mapindices=title_to_mapindices,
            selection_mode=selection_mode,
        ),
        code=r"""
        if (this.value == "") return;
        let indices, _source, _level, _btype, _block
        const text = this.value;
        let match = text.match(/\/b (L\d+([DTE])\d+)/)
        if (match) {
            _btype = match[2];
            indices = [label_to_mapindex[match[1]]]
            if (_btype == "D") { _source = dsource; } else { _source = xsource; }
        }
        else {
            match = text.match(/\/d (.+)/)
            if (match) {
                indices = title_to_mapindices[match[1]]
                _source = dsource
            }
        }
        if (!match) {
            indices = [term_to_mapindex[text.slice(2)]]
            _source = xsource
        }
        if (indices != undefined) {
            if (selection_mode.value == "single") {
                _source.selected.indices = indices;
            } else {
                _source.selected.indices = [
                    ...new Set(_source.selected.indices.concat(indices))
                ];
            }
        } else {
            _source.selected.indices = [];
        }
        this.value = "";
        """,
    )
    searchbox.js_on_change("change:value", searchbox_cb)

    return bkl.row(
        searchbox, selection_mode, align="center", sizing_mode="stretch_width"
    )


def get_hbm_nav_buttons(fig, btype, labels):
    source = fig.select_one("{}_map_data".format(btype))
    width = 70
    height = int(width / phi)

    up_button = bkm.Button(label="▲", width=width, height=height, margin=(5, 10, 1, 10))
    down_button = bkm.Button(
        label="▼", width=width, height=height, margin=(1, 10, 5, 10)
    )
    move_buttons_js = """
    let enact_move = false;
    let old_index
    let new_index
    const data = source.data
    if (source.selected.indices.length == 0) {
        if (move == -1) {
            new_index = data.x.length - 1;
        }
        else {
            new_index = data.x.indexOf(1);
        }
        old_index = new_index;
        enact_move = true;
    }
    else if (source.selected.indices.length == 1) {
        old_index = source.selected.indices[0]
        new_index = old_index + move;
        enact_move = (0 <= new_index) && (new_index < data.label.length);
        enact_move = enact_move && (data.x[old_index] == data.x[new_index]);
    }
    if (enact_move) {
        source.selected.indices = [new_index];

        // Adapt the frame to the new selection
        const old_height = data.height[old_index];
        const new_height = data.height[new_index];
        const old_delta = fig.y_range.end - fig.y_range.start;
        let new_delta = new_height * old_delta / old_height;
        if (new_delta < new_height) {new_delta = new_height};
        if (new_delta > 1) {new_delta = 1};
        let new_end = data.y[new_index] + new_delta/2;
        let new_start = data.y[new_index] - new_delta/2;
        if (new_start < 0) {new_end += -new_start; new_start = 0;}
        if (new_end > 1) {new_start -= new_end - 1; new_end = 1;}
        fig.y_range.start = new_start;
        fig.y_range.end = new_end;
        for (const label of labels) { label.change.emit() }
    }
    """
    up_button.js_on_click(
        CustomJS(
            args={
                "fig": fig,
                "source": source,
                "labels": [*labels.values()],
                "move": 1,
            },
            code=move_buttons_js,
        )
    )
    down_button.js_on_click(
        CustomJS(
            args={
                "fig": fig,
                "source": source,
                "labels": [*labels.values()],
                "move": -1,
            },
            code=move_buttons_js,
        )
    )

    zoom_button = bkm.Button(
        label="⇳",  # ⬍ or ⇳ or ⇕ or 🖽
        width=width,
        height=height,
        margin=(5, 10, 0, 10),
        stylesheets=[bkm.InlineStyleSheet(css=".bk-btn {font-size: 17px};")],
    )
    zoom_button_js = """
    let new_start
    let new_end
    const data = source.data
    const indices = source.selected.indices
    if (indices.length == 0) {
        new_start = 0
        new_end = 1
    }
    else {
        const old_start = fig.y_range.start
        const old_end = fig.y_range.end
        new_start = Math.min(...indices.map(x => data.y[x] - data.height[x] / 2))
        new_end = Math.max(...indices.map(x => data.y[x] + data.height[x] / 2))
        if (old_start == new_start && old_end == new_end) {
            new_start = 0
            new_end = 1
        }
    }
    fig.y_range.start = new_start;
    fig.y_range.end = new_end;
    for (const label of labels) { label.change.emit() }
    """
    zoom_button.js_on_click(
        CustomJS(
            args={
                "fig": fig,
                "source": source,
                "labels": [*labels.values()],
            },
            code=zoom_button_js,
        )
    )

    return bkl.Column(up_button, down_button, zoom_button, sizing_mode="stretch_width")


def get_doc_histogram_data(corpus, series: pandas.Series = None):
    series = corpus.data[corpus.col_time] if series is None else series
    series, xindex = try_time_index(series)
    blocks, levels = corpus.get_blocks_levels("doc")
    choice_vals = []
    for map_level in list(reversed(levels)):
        map_hbindex = sorted_hierarchical_block_index(blocks, levels, map_level)
        for map_hb in map_hbindex:
            bdata = corpus.data[blocks[map_level] == map_hb[-1]]
            val = bdata.groupby(series).size().reindex(xindex).fillna(0)
            choice_vals.append(val)
    choice_vals[0].index.name = series.name
    return choice_vals


def get_doc_histogram(choice_vals, tap_fig):
    xaxis = choice_vals[0].index
    is_time = is_time_type(xaxis)
    source = bkm.ColumnDataSource(
        {
            "x": xaxis,
            "y": [0] * len(xaxis),
            "yrel": [0] * len(xaxis),
            "ytot": choice_vals[0],
        }
    )

    fig = bkp.figure(
        toolbar_location=None,
        tools="",
        min_height=150,
        sizing_mode="stretch_both",
        x_axis_type="datetime" if is_time else "linear",
        # x_axis_label=f"{xaxis.name}",
        y_axis_label="documents",
    )

    if is_time:
        fig.xaxis.formatter = DatetimeTickFormatter(days="%d %b")

    rel_rend = fig.line(
        "x", "yrel", source=source, color="red", y_range_name="rel", legend_label="rel"
    )
    fig.line("x", "y", source=source, color="grey", legend_label="abs")

    fig.y_range.start = 0.0
    fig.extra_y_ranges = {"rel": bkm.DataRange1d(renderers=[rel_rend], start=0.0)}
    fig.add_layout(
        bkm.LinearAxis(y_range_name="rel", major_label_text_color="red"), "right"
    )
    fig.legend.location = "top_left"
    fig.x_range.bounds = "auto"
    dochist_cb = CustomJS(
        args=dict(
            fig=fig,
            source=source,
            choice_vals=choice_vals,
        ),
        code="""
        const index = (
            cb_obj.indices === undefined || cb_obj.indices[0] === undefined ?
            0 : cb_obj.indices[0]
        )
        const data = {...source.data}
        data.y = choice_vals[index]
        data.yrel = new Float64Array(data.y).map((val, i) => val ? val / data.ytot[i] : val)
        source.data = data
        """,
    )
    bio.curdoc().js_on_event("document_ready", dochist_cb)
    tap_source = tap_fig.select_one("doc_map_data")
    tap_source.selected.js_on_change("change:indices", dochist_cb)

    wheelzoom_tool = bkm.WheelZoomTool(
        dimensions="width",
        maintain_focus=False,
        zoom_on_axis=True,
    )
    pan_tool = bkm.PanTool(dimensions="width")
    hover_tool = bkm.HoverTool(
        tooltips=[("", ("@x{%F}" if is_time else "@x") + " (@y / @ytot)")],
        formatters={"@x": "datetime"} if is_time else {},
        mode="vline",
        attachment="right",
        renderers=[rel_rend],
    )
    fig.add_tools(wheelzoom_tool, pan_tool, hover_tool)
    fig.toolbar.active_scroll = wheelzoom_tool
    fig.toolbar.active_drag = pan_tool

    return fig


def get_multi_histogram_data(corpus, ybtype, series: pandas.Series = None):
    annotations_spe = load_annotations(
        corpus, get_xblock_yblocks_elements, "doc", ybtype
    )
    annotations_com = load_annotations(
        corpus, get_subxblocks_yblocks_elements, "doc", ybtype
    )

    lblock_to_label = corpus.lblock_to_label
    yblocks, ylevels = corpus.get_blocks_levels(ybtype)
    y_element_to_block = yblocks[1]
    if ybtype == "ext":
        doc_exts = corpus.get_doc_exts()

    def counting_f(domain_data, level, xblock):
        annotations = annotations_spe if level == 1 else annotations_com

        xblock_yblocks = annotations[level][xblock]["blocks"]
        # number of terms in domain_data belonging to each yblock
        yblocks_count = {lblock_to_label[1, yb]: 0 for yb in xblock_yblocks}
        if ybtype == "ter":
            for doc in domain_data[corpus.column]:
                for yb in {
                    yb
                    for sen in doc
                    for ter in sen
                    if (yb := y_element_to_block[ter]) in xblock_yblocks
                }:
                    yblocks_count[lblock_to_label[1, yb]] += 1
        else:
            for doc_idx in domain_data.index:
                for yb in {
                    yb
                    for ext in doc_exts[doc_idx]
                    if (yb := y_element_to_block[ext]) in xblock_yblocks
                }:
                    yblocks_count[lblock_to_label[1, yb]] += 1
        yblocks_count = pandas.Series(yblocks_count, dtype="float64").fillna(0)
        return yblocks_count

    series = corpus.data[corpus.col_time] if series is None else series
    series, xindex = try_time_index(series)

    dblocks, dlevels = corpus.get_blocks_levels("doc")
    choice_vals = []
    for level in list(reversed(dlevels)):
        hbindex = sorted_hierarchical_block_index(dblocks, dlevels, level)
        for hb in hbindex:
            domain_data = corpus.data[dblocks[level] == hb[-1]]
            df_sums = domain_data.groupby(series).apply(counting_f, level, hb[-1])
            val = df_sums.reindex(xindex).fillna(0)
            choice_vals.append(val)
    choice_vals[0].index.name = xindex.name
    return choice_vals


def get_multi_histogram(dfs, tap_fig):
    xaxis = dfs[0].index
    is_time = is_time_type(xaxis)
    fig = bkp.figure(
        toolbar_location=None,
        tools="",
        sizing_mode="stretch_both",
        x_axis_type="datetime" if is_time else "linear",
        x_axis_label=f"{xaxis.name}",
        y_axis_label="occurrences",
    )

    if is_time:
        fig.xaxis.formatter = DatetimeTickFormatter(days="%d %b")
    fig.y_range.start = 0.0
    tap_source = tap_fig.select_one("doc_map_data")
    multihist_cb = CustomJS(
        args=dict(
            tap_source=tap_source.selected,
            xaxis=xaxis.to_list(),
            choice_yaxis=[df.to_dict(orient="list") for df in dfs],
            fig=fig,
            colors=colorcet.glasbey_dark[1:],
        ),
        code="""
        const ColumnDataSource = Bokeh.Models.get("ColumnDataSource")
        const Line = Bokeh.Models.get("Line")
        const VAreaStep = Bokeh.Models.get("VAreaStep")
        const index = tap_source.indices === undefined ? undefined : tap_source.indices[0]
        fig.x_range.bounds = "auto"
        fig.renderers = []
        let cur_y, prev_y
        cur_y = prev_y = xaxis.map(x => 0)
        const block2yaxis = index === undefined ? {} : choice_yaxis[index]
        let num = 0
        for (const yname in block2yaxis) {
            const y_diff = block2yaxis[yname]
            cur_y = prev_y.map((x, i) => x + y_diff[i])
            const source = new ColumnDataSource(
                {data: {x: xaxis, y1: prev_y, y2: cur_y, y: y_diff}}
            )
            /* Old style using VAreaStep
            const varea = new VAreaStep({
                x: { field: "x" },
                y1: { field: "y1" },
                y2: { field: "y2" },
                fill_color: colors[num],
                step_mode: "center",
            });
            fig.add_glyph(varea, source)
            */
            const line = new Line({
                x: { field: "x" },
                y: { field: "y" },
                line_color: colors[num],
            });
            fig.add_glyph(line, source)
            prev_y = cur_y
            num += 1
            if (num === 5) { break }
        }
        if (num == 0) {
            const source = new ColumnDataSource({data: {x: xaxis, y: cur_y}})
            const line = new Line({x: { field: "x" }, y: { field: "y" }});
            fig.add_glyph(line, source)
            // fig.x_range.reset()
            // fig.y_range.reset()
            fig.renderers[0].visible = false
        }
        fig.x_range.reset()
        fig.y_range.reset()
        """,
    )
    bio.curdoc().js_on_event("document_ready", multihist_cb)
    tap_source.selected.js_on_change("change:indices", multihist_cb)

    relative_mode = bkm.Select(value="absolute", options=["absolute", "relative"])
    fig.js_on_event(
        bke.Tap,
        CustomJS(
            args=dict(relative_mode=relative_mode, reload_data=multihist_cb),
            code="""
        const renderers = cb_obj.origin.renderers
        if (!renderers[0].data_source.data.hasOwnProperty("y")) return
        if (relative_mode.value == "absolute") {
            let total = renderers[0].data_source.data.y.map(x => 0)
            for (const rend of renderers) {
                const data = rend.data_source.data
                total = total.map((x, i) => x + data.y[i])
            }
            for (const rend of renderers) {
                const data = {...rend.data_source.data}
                data.y = data.y.map((x, i) => x ? x / total[i] : 0)
                rend.data_source.data = data
            }
            relative_mode.value = "relative"
        } else {
            reload_data.execute()
            relative_mode.value = "absolute"
        }
    """,
        ),
    )

    wheelzoom_tool = bkm.WheelZoomTool(
        dimensions="width",
        maintain_focus=False,
        zoom_on_axis=True,
    )
    pan_tool = bkm.PanTool(dimensions="width")
    hover_tool = bkm.HoverTool(
        tooltips=[("", ("@x{%F}" if is_time else "@x") + " (@y)")],
        formatters={"@x": "datetime"} if is_time else {},
        mode="mouse",
        attachment="left",
    )
    fig.add_tools(wheelzoom_tool, pan_tool, hover_tool)
    fig.toolbar.active_scroll = wheelzoom_tool
    fig.toolbar.active_drag = pan_tool

    return fig
