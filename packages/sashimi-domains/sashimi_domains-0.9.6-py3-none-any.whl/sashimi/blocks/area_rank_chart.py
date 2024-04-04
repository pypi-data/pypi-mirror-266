import math
from numpy import linspace, cos, pi

import colorcet
import bokeh.models as bkm
from bokeh.io import output_file, show
from bokeh.layouts import row, column  # , Spacer
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import pandas as pd

from .tables import get_subxblocks, get_labels


################
# Domain plots #
################


def domain_charts(corpus, domain_labels, outfile="evoplot.html"):
    fig = build_graphics(
        corpus,
        [
            corpus.level_block_to_hblock(level, block, btype)
            for dlabel in domain_labels
            for btype, level, block in [corpus.label_to_tlblock(dlabel)]
        ],
    )
    if outfile is None:
        return fig
    output_file(outfile)
    show(fig)


def subdomain_charts(corpus, xlevel, xb, sxlevel=None, outfile="evoplot.html"):
    layout = column(
        build_graphics(corpus, [corpus.level_block_to_hblock(xlevel, xb, "doc")]),
        build_graphics(
            corpus, get_subxblocks(corpus, "doc", xlevel, xb, sxlevel=sxlevel)
        ),
        # rank_graphics(),
    )
    if outfile is None:
        return layout
    output_file(outfile)
    show(layout)


def build_graphics(corpus, dhblocks):
    """
    Stacked charts showing the comparative evolution of domains.
    """
    x = sorted(corpus.data[corpus.col_time].unique())

    def get_sizes(level_block):
        level, block = level_block
        return (
            corpus.data[corpus.dblocks[level] == block]
            .groupby(corpus.col_time)
            .size()
            .reindex(x)
            .fillna(0)
        )

    dlevels = [corpus.hblock_to_level_block(dhb, "doc")[0] for dhb in dhblocks]
    labels = get_labels(corpus)

    cats_data = list(reversed(list(zip(dhblocks, dlevels))))
    cats_data = sorted(
        cats_data, key=lambda x: get_sizes((x[1], x[0][-1])).sum(), reverse=True
    )
    cats = [corpus.lblock_to_label[level, dhb[-1]] for dhb, level in cats_data]
    cats = [f"{x}: {labels.get(x, '[no label]')}" for x in cats]

    out_size = corpus.data.groupby(corpus.col_time).size().reindex(x)
    in_size = sum(get_sizes((level, dhb[-1])) for (dhb, level) in cats_data).astype(int)
    has_in_size = not out_size.equals(in_size)

    palette = colorcet.glasbey_dark[1 : 1 + len(cats_data)]

    def make_plot(norm, scale, title, labels):
        p = figure(
            title=title,
            y_range=cats + [""],
            width=1920 // (3 if has_in_size else 2),
            height=1080,
            x_range=(min(x), max(x)),
            toolbar_location=None,
            tools="",
        )

        def ridge(category, data):
            return [(category, dat * scale * len(dhblocks) / 2) for dat in data]

        for i, (cat, (dhb, level)) in enumerate(
            zip(reversed(cats), reversed(cats_data))
        ):
            source = ColumnDataSource(data=dict(x=x))
            y_counts = (
                corpus.data[corpus.dblocks[level] == dhb[-1]]
                .groupby(corpus.col_time)
                .size()
                .reindex(x)
                .fillna(0)
            )
            y_values = y_counts / norm
            y1 = len(y_values) * [(cat, 0.0)]
            y2 = ridge(cat, y_values)
            source.add(y2, cat)
            source.add(y1, f"{cat}_zero")
            source.add(y_counts, f"{cat}_counts")
            source.add(norm, "norm")

            p.varea(
                x="x",
                y1=f"{cat}_zero",
                y2=cat,
                color=palette[i],
                alpha=0.5,
                source=source,
            )
            line = p.line(
                x="x",
                y=cat,
                color="black",
                source=source,
            )

            tip = f"@{{{cat}_counts}}" + ("" if title == "Absolute" else " / @{norm}")
            p.add_tools(
                bkm.HoverTool(
                    renderers=[line],
                    tooltips=[("", tip)],
                    mode="vline",
                )
            )

        p.outline_line_color = None
        p.background_fill_color = "#efefef"
        p.ygrid.grid_line_color = None
        p.xgrid.grid_line_color = "#dddddd"
        p.xgrid.ticker = p.xaxis.ticker
        p.axis.minor_tick_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.axis_line_color = None
        if not labels:
            p.yaxis.major_label_text_font_size = "0px"

        return p

    layout = row(
        make_plot(pd.Series(1, index=x), 1 / in_size.mean(), "Absolute", True),
        make_plot(out_size, out_size.sum() / in_size.sum(), "Corpus relative", False),
        align="end",
    )
    if has_in_size:
        layout.append(make_plot(in_size, 1, "Ensemble relative", False))

    return layout


###################
# Area rank chart #
###################


def area_rank_chart(
    corpus, selector, grouper, averager, level, labels=None, rel=True, outfile=None
):
    """
    Plots an area rank chart of domains, with the grouper dimension on the
    x-axis and domain sizes on the y-axis.

    Restricts corpus to given selector, then group by grouper and by blocks of
    the given level. Get the group's sizes, then average on averager. For
    example, if grouper corresponds to periods with variable number of years,
    then averager should be the year, so that larger periods aren't inflated.
    """
    if labels is None:
        labels = get_labels(corpus)

    def get_label(b):
        label = corpus.lblock_to_label[level, b]
        return f"{label}: {labels.get(label, '[no label]')}"

    y_counts = (
        corpus.data.loc[selector]
        .groupby([grouper, corpus.dblocks[level]])
        .size()
        .div(corpus.data.groupby(grouper)[averager].unique().map(len), level=0)
    )
    y_abs = [
        y_counts.loc[(idx,)].sort_values(ascending=False)
        for idx in y_counts.index.levels[0]
    ]
    y_range = y_abs[0].index
    for y_abs_o in y_abs[1:]:
        y_range = y_range.union(y_abs_o.index)
    msize_abs = max(yi.max() for yi in y_abs)
    if rel:
        y_rel = [x / x.sum() for x in y_abs]
        msize_rel = max(yi.max() for yi in y_rel)
    points_in_unit_width = 900 // len(y_abs)
    fig = figure(
        # title=title,
        width=1920,
        height=1080,
        x_range=(0, len(y_abs) - 1),
        x_axis_location="above",
        y_range=(len(y_range), 0),
        toolbar_location="above",
        # tools="",
    )
    fig.axis.major_label_text_font_size = "17px"
    fig.xaxis.minor_tick_line_color = None
    fig.xaxis.major_label_orientation = math.pi / 4
    fig.xaxis.ticker = list(range(len(y_counts.index.levels[0])))
    fig.xaxis.major_label_overrides = {
        i: str(j) for i, j in enumerate(y_counts.index.levels[0])
    }
    fig.ygrid.visible = False
    fig.yaxis.ticker = yticker = [i + 1 / 2 for i in range(len(y_abs[0]))]
    fig.yaxis.major_label_overrides = {
        i: str(j) for i, j in zip(yticker, y_abs[0].index.map(get_label))
    }

    # add end ticks and labels
    ryaxis = bkm.LinearAxis(ticker=bkm.FixedTicker())
    fig.add_layout(ryaxis, "right")
    ryaxis.major_label_text_font_size = "17px"
    ryaxis.ticker = ryticker = [i + 1 / 2 for i in range(len(y_abs[-1]))]
    ryaxis.major_label_overrides = {
        i: str(j) for i, j in zip(ryticker, y_abs[-1].index.map(get_label))
    }

    palette = pd.Series(colorcet.glasbey[: len(y_range)], index=y_range)

    plot_connections(fig, y_abs, msize_abs, "solid", palette, points_in_unit_width)
    if rel:
        plot_connections(fig, y_rel, msize_rel, "dotted", palette, points_in_unit_width)

    if outfile is None:
        return fig
    output_file(outfile)
    show(fig)


def plot_connections(fig, y_data, msize_data, line_dash, palette, points_in_unit_width):
    def plot():
        fig.varea(xs, y0s, y1s, color=palette[idx], alpha=0.5)
        fig.line(xs, y0s, color="black", line_dash=line_dash)
        fig.line(xs, y1s, color="black", line_dash=line_dash)

    for start, (y0, y1) in enumerate(zip(y_data, y_data[1:])):
        for i, (idx, size0) in enumerate(y0.items()):
            y0pos = i + 1 / 2
            if idx in y1.index:
                y1pos = (len(y1.loc[:idx]) - 1) + 1 / 2
                size1 = y1.loc[idx]
                length = 1
            else:
                y1pos = y0pos
                size1 = size0
                length = 0.1
            xs, y0s, y1s = connection(
                y0pos,
                y1pos,
                size0 / msize_data,
                size1 / msize_data,
                start,
                length,
                points_in_unit_width,
            )
            plot()
    for i, (idx, size) in enumerate(y_data[-1].items()):
        start = len(y_data) - 1
        if len(y_data) > 2 and idx not in y_data[-2].index:
            ypos = i + 1 / 2
            xs, y0s, y1s = connection(
                ypos,
                ypos,
                size / msize_data,
                size / msize_data,
                start,
                -0.1,
                points_in_unit_width,
            )
            plot()


def connection(y0, y1, s0, s1, start, length, points_in_unit_width):
    def connect(x):  # from 0 to 1
        return y0 + (y1 - y0) * (1 - cos(x * pi)) / 2

    def spread(x):
        return s0 * (1 - x) + s1 * x

    xs = linspace(start, start + length, int(abs(length) * points_in_unit_width))
    nxs = linspace(0, 1, int(abs(length) * points_in_unit_width))
    y0s = [connect(x) - spread(x) / 2 for x in nxs]
    y1s = [connect(x) + spread(x) / 2 for x in nxs]
    return xs, y0s, y1s
