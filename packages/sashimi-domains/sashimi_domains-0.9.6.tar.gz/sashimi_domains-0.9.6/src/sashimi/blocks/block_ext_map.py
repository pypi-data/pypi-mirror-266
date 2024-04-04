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

import os, numpy, pandas
from itertools import chain
import bokeh.plotting as bkp, bokeh.models as bkm, bokeh.layouts as bkl

# import bokeh.palettes as bkpa, bokeh.events as bke
# from bokeh.models.callbacks import CustomJS
from tqdm import tqdm
import colorcet

from .util import sorted_hierarchical_block_index


def plot_block_ext_map(
    self,
    extzfunc,
    title,
    ext,
    blocks=None,
    norm="bytime",
    scale="linear",
    labels="auto",
):
    args = locals()
    figs = (
        [bkl.Spacer(height=200)]
        + [plot_block_ext_map_s(**args)]
        + [bkl.Spacer(height=200)]
    )
    desc = extzfunc.__name__
    fname = os.path.join(
        self.blocks_adir,
        "block_{}_matrix-{}-n_{}-s_{}-l_{}.html".format(
            self.col_time, desc, norm, scale, labels
        ),
    )
    bkp.output_file(
        fname,
        mode="inline",
        title="Block {} {} ({})".format(self.col_time, desc, scale),
    )
    bkp.save(bkl.column(figs))


class ExtZfuncs:
    def count(self, data, ext, index):
        count = data[ext].value_counts().reindex(index)
        return count.where(count.notnull(), 0)

    def density(self, data, ext, index):
        count = data[ext].value_counts().reindex(index)
        count = count.where(count.notnull(), 0)
        all_count = self.data[ext].value_counts().reindex(index)
        return count / all_count


def plot_block_ext_map_s(
    self,
    extzfunc,
    title,
    ext,
    block_selection=None,
    norm="bytime",
    scale="linear",
    block_labels=None,
):
    """
    Colormap to display the evolution of some extended dimension witin blocks.

    Colors can represent, for example, journals/authors/institutions within,
    or crossing, blocks at that given level.

    TODO: numeric or chart group sizes?
    TODO: keyf, documents containing not total count?
    """
    blocks, levels, sblocks = self.get_blocks_levels_sample("doc")
    lscape = get_level_block_ext_landscape(self, extzfunc, ext)

    cmapper = bkm.LogColorMapper if scale == "log" else bkm.LinearColorMapper

    lrows = {}

    for level in tqdm(reversed(levels[:]), total=len(levels), desc="Level"):
        if block_selection is not None and level not in block_selection:
            continue

        bindex = sorted_hierarchical_block_index(blocks, levels, level)
        lrows[level] = []

        for b in tqdm(bindex, desc="Block"):
            if (
                block_selection is not None
                and block_selection[level] is not None
                and b[-1] not in block_selection[level]
            ):
                continue

            cmap = cmapper(
                colorcet.b_diverging_bwr_40_95_c42[128:],
                low=lscape[level].min().min(),
                high=lscape[level].max().max(),
            )

            source = dict((k, []) for k in ("x", "z"))
            for e_i, e_val in lscape[level][b[-1]].sort_index().items():
                source["x"].append(e_i)
                source["z"].append(e_val)

            fig = bkp.figure(
                toolbar_location=None,
                tools="",
                title=None,
                width=600,
                frame_height=34,
                min_border=2,
                x_range=(min(source["x"]) - 0.5, max(source["x"]) + 0.5),
                y_range=(-0.5, 0.5),
                x_axis_location="above",
            )
            fig.grid.visible = False
            fig.axis.visible = False

            source = bkm.ColumnDataSource(data=source)
            fig.rect(
                "x",
                0,
                1,
                1,
                source=source,
                fill_color={"field": "z", "transform": cmap},
            )
            lrows[level].append((fig, b))

    for level in lrows:
        lrows[level][0][0].xaxis.visible = True
        for i in range(len(lrows[level])):
            fig, label = lrows[level][i]
            label = ((block_labels or {}).get(level, {}) or {}).get(label[-1], label)
            lrows[level][i] = bkl.row(
                fig,
                bkm.Div(
                    align="center",
                    style={"margin-top": "22px"} if fig.xaxis.visible else None,
                    text="{}".format(label),
                ),
            )
        if len(lrows) > 1:
            lrows[level].insert(0, bkm.Div(text="Level {}".format(level)))

    return bkl.column(list(chain(*lrows.values())))


def old():

    for level in reversed(levels):
        print("Processing level {}".format(level))
        columns = tuple(
            sorted(
                [
                    tuple(reversed(x))
                    for x in blocks[levels[level - 1 :]]
                    .groupby(level)
                    .first()
                    .itertuples()
                ]
            )
        )
        m = pandas.DataFrame(
            columns=columns,
            index=numpy.sort(data[self.col_time].unique()),
            dtype=numpy.float64,
        )
        yticks = []
        levellabels = (m.columns.size <= 200) if labels is "auto" else labels
        if not levellabels and labels:
            print("Level has over 200 columns, skipping labels")

        # compute matrix
        for b in m.columns:
            m[b] = zmethod(self, data[blocks[level] == b[-1]], level, m)
        om = m.copy()
        if norm == "bytime":
            m = m.div(m.sum(axis=1), axis=0)
        elif norm:
            raise Exception("Undefined normalization: {}".format(norm))

        # add yticks labels
        if levellabels:
            for b in m.columns:
                pick = get_dblock_elements(self, "ter", b, "local_specificity", 5)
                yticks.append("{} {}".format(pick, b))
        else:
            yticks = list(map(str, m.columns))

        # insert lines to highlight the block hierarchy
        if level != levels[-1]:
            prev = m.columns[-1][-2]
            for i, c in reversed(list(enumerate(m.columns))):
                if c[-2] != prev:
                    m.insert(i + 1, numpy.nan, numpy.nan, allow_duplicates=True)
                    om.insert(i + 1, numpy.nan, numpy.nan, allow_duplicates=True)
                    yticks.insert(i + 1, str(i))
                    prev = c[-2]

        # set up grid and figure
        fig = bkp.figure(
            toolbar_location=None,
            tools="",
            title="Block level {}: {}".format(level, desc),
            width=1600,
            height=(256 + 32 * m.columns.size),
            x_axis_location="above",
            x_axis_label=self.col_time,
            y_range=yticks,
            y_axis_label="block",
            x_range=(m.index.min() - 0.5, m.index.max() + 0.5),
        )
        fig.title.text_font_size = "17px"
        fig.yaxis.major_label_text_font_size = "17px"
        fig.xaxis[0].ticker.desired_num_ticks = m.index.size
        fig.xaxis.minor_tick_line_color = None
        fig.xaxis.major_label_orientation = numpy.pi / 4
        cmap = (bkm.LogColorMapper if scale == "log" else bkm.LinearColorMapper)(
            palette, low=m.min().min(), high=m.max().max()
        )
        grid_x, grid_y = numpy.meshgrid(m.index, yticks)
        ogrid_x, ogrid_y = numpy.meshgrid(m.index, m.columns)
        datasource = dict(
            index=grid_x.flatten(),
            columns=grid_y.flatten(),
            colors=m.values.T.flatten(),
            values=om.values.T.flatten(),
            ocols=list(map(str, ogrid_y.flatten())),
        )

        # add grid dependent labels
        if levellabels:
            datasource["titles"] = numpy.concatenate(
                [
                    [
                        " | ".join(
                            titles
                            if titles.empty
                            else titles.sample(min(10, titles.size))
                        )
                        for iy in m.index
                        for titles in (
                            data.loc[
                                (self.dblocks[level] == b[-1]) & (data.year == iy),
                                self.col_title,
                            ],
                        )
                    ]
                    if b is not numpy.nan
                    else [""] * len(m.index)
                    for b in m.columns
                ]
            )
            datasource["terms"] = numpy.concatenate(
                [
                    self.get_dblock_time_terms(b, "local_specificity", n=10)
                    if b is not numpy.nan
                    else [""] * len(m.index)
                    for b in m.columns
                ]
            )

        # plot colormap
        source = bkm.ColumnDataSource(data=datasource)
        fig.rect(
            "index",
            "columns",
            1,
            1,
            source=source,
            color={"field": "colors", "transform": cmap},
        )

        # plot colorbar
        if m.columns.size != 1:
            ticker = {"ticker": bkm.LogTicker()} if scale == "log" else {}
            color_bar = bkm.ColorBar(color_mapper=cmap, location=(0, 0), **ticker)
            fig.add_layout(color_bar, "right")

        # add hover tooltip
        fig.add_tools(
            bkm.HoverTool(
                tooltips="""
        <div style="width: 400px; padding:10px 5px; font-size: 17px">
             <div style="text-align:center">@ocols : @index</div>
             <span style="color:#3333dd">value:</span> @values<br />
             <span style="color:#3333dd">color:</span> @colors<br />
             <span style="color:#3333dd">specific terms:</span><br />
             @terms<br />
             <span style="color:#3333dd">titles:</span><br />
             @titles
        </div>
        """
            )
        )

        figs.append(fig)
        return figs


def get_level_block_ext_landscape(self, extzfunc, ext):
    """
    Applies extzfunc for each level, for each block, for all values of an
    extended dimension.

    Parameters
    ----------
    extzfunc: function
        The function which returns the series of values for a level.
    ext: string
        Column name for extended dimension.

    Returns
    -------
    lscape: dict of pandas.DataFrames
        for each level, the dataframe of ext series over its blocks.
    """
    blocks, levels, sblocks = self.get_blocks_levels_sample("doc")

    lscape = {}

    for level in levels:
        lidx = blocks[level].unique()
        bidx = self.data[ext].unique()
        lscape[level] = pandas.DataFrame(index=bidx)
        for block in lidx:
            sbdata = self.data.loc[sblocks[level] == block]
            lscape[level][block] = extzfunc(self, sbdata, ext, bidx)
    return lscape
