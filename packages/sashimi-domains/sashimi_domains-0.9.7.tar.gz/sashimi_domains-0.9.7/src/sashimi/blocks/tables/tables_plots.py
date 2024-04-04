from bokeh.plotting import figure
from bokeh.embed import components
import bokeh.models as bkm


def get_time_plot(corpus, xbtype, xlevel, xb):
    """
    TODO: replace with block histogram from hbm?
    """
    blocks, _ = corpus.get_blocks_levels(xbtype)
    if xbtype == "doc":
        data_all = blocks.groupby(corpus.data[corpus.col_time]).size()
        data_abs = (
            blocks[blocks[xlevel].eq(xb)]
            .groupby(corpus.data[corpus.col_time])
            .size()
            .reindex(data_all.index, fill_value=0)
        )
        data_rel = data_abs / data_all

    p = figure(
        title=f"TOT: {data_abs.sum()} ; REL: {data_abs.sum()/data_all.sum():.2}",
        frame_width=250,
        frame_height=200,
        toolbar_location=None,
        tools="",
    )
    rel_rend = p.line(
        data_rel.index,
        data_rel.values,
        color="red",
        y_range_name="rel",
        legend_label="rel",
    )
    p.line(data_abs.index, data_abs.values, color="grey", legend_label="abs")
    p.y_range.start = 0.0
    p.extra_y_ranges = {"rel": bkm.DataRange1d(renderers=[rel_rend], start=0.0)}
    p.add_layout(
        bkm.LinearAxis(y_range_name="rel", major_label_text_color="red"), "right"
    )
    p.legend.location = "top_left"
    return components(p)
