# coding: utf-8

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


import graph_tool.all as gt
import multiprocessing, numpy, os, pandas, pickle, colorcet
from functools import cache, partial
from itertools import combinations, chain
from heapq import nsmallest
from collections import OrderedDict, Counter, defaultdict
from nltk.corpus import stopwords
from scipy.spatial.distance import pdist
from matplotlib import pyplot as plt, colors
from matplotlib.backends.backend_pdf import PdfPages
import bokeh.plotting as bkp, bokeh.models as bkm, bokeh.layouts as bkl
import bokeh.palettes as bkpa
from tqdm import tqdm

from . import naming

# import pdb; # pdb.set_trace()


class BlockologyLimbo:
    """
    Former Blockology methods needing revision.
    """

    def plot_block_time_matrix(
        self,
        zmethod=None,
        norm="bytime",
        scale="linear",
        desc=None,
        labels="auto",
        palette="Inferno256",
    ):
        """
        Colormap to display the evolution of aggregates at different levels.
        Colors can represent, for example, journals/authors/institutions within,
        or crossing, blocks at that given level.

        TODO: numeric or chart group sizes?
        TODO: keyf, documents containing not total count?
        """
        data = self.data
        blocks = self.dblocks.loc[data.index]
        levels = self.dblocks_levels
        if zmethod is None:

            def zmethod(self, bdata, l, m):
                count = bdata.groupby(self.time).count().loc[m.index]
                return count.where(count.notnull(), 0)

            if desc is None:
                desc = "count"
        else:
            if desc is None:
                desc = zmethod.__name__
            assert desc != "count"

        fname = os.path.join(
            self.analysis_dir,
            "block_{}_matrix-{}-n_{}-s_{}-l_{}.html".format(
                self.time, desc, norm, scale, labels
            ),
        )

        figs = []
        figs.append(bkl.Spacer(height=200))

        for level in reversed(levels):
            print("Processing level {}".format(level))
            columns = tuple(
                sorted(
                    [
                        tuple(reversed(x))
                        for x in blocks[levels[levels.index(level) :]]
                        .groupby(level)
                        .first()
                        .itertuples()
                    ]
                )
            )
            m = pandas.DataFrame(
                columns=columns,
                index=numpy.sort(data[self.time].unique()),
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
                    pick = self.get_dblock_words(b, "local_specificity", 5)
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
                x_axis_label=self.time,
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
                                    (self.blocks[level] == b[-1]) & (data.year == iy),
                                    self.labels["title"],
                                ],
                            )
                        ]
                        if b is not numpy.nan
                        else [""] * len(m.index)
                        for b in m.columns
                    ]
                )
                datasource["words"] = numpy.concatenate(
                    [
                        self.get_dblock_time_words(b, "local_specificity", n=10)
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
                 <span style="color:#3333dd">specific words:</span><br />
                 @words<br />
                 <span style="color:#3333dd">titles:</span><br />
                 @titles
            </div>
            """
                )
            )

            figs.append(fig)

        figs.append(bkl.Spacer(height=200))
        bkp.output_file(
            fname,
            mode="inline",
            title="Block {} {} ({})".format(self.time, desc, scale),
        )
        bkp.save(bkl.column(figs))

    def plot_level_time_matrix(
        self, zmethod=None, norm=None, scale="linear", desc=None
    ):
        """
        Colormap to display the evolution of aggregates at different levels.
        Colors can represent, for example, journals/authors/institutions within, or
        crossing, blocks at that given level.
        """
        data = self.data
        blocks = self.blocks.loc[data.index]

        if zmethod is None:

            def zmethod(self, bdata, l, m):
                # FIXME: check `unique` below
                return (
                    self.blocks.loc[bdata.index, l]
                    .groupby(bdata[self.time])
                    .unique()
                    .apply(len)
                )

            if desc is None:
                desc = "count"
        else:
            if desc is None:
                desc = zmethod.__name__
            assert desc != "count"

        fname = os.path.join(
            self.analysis_dir,
            "level_{}_matrix-{}-n_{}-s_{}".format(self.time, desc, norm, scale),
        )

        # Compute matrix
        m = pandas.DataFrame(
            columns=[x for x in blocks if type(x) is int],
            index=numpy.sort(data[self.time].unique()),
            dtype=numpy.float64,
        )
        for level in m.columns:
            m[level] = zmethod(self, data, level, m)
        om = m.copy()
        if norm == "bylevel":
            m = m.div(m.sum(axis=0), axis=1)
        elif norm == "numblocks":
            m = m.div(blocks[m.columns].apply(lambda x: len(x.unique())), axis=1)
        elif norm:
            raise Exception("Undefined normalization: {}".format(norm))

        # Plot figure
        if False:
            plt.figure(figsize=(10, 7))
            norm = colors.LogNorm() if scale == "log" else colors.Normalize()
            plt.pcolormesh(
                numpy.ma.masked_array(m.values, m.isnull()).T, cmap="OrRd", norm=norm
            )
            plt.xticks(numpy.arange(0.5, len(m.index), 1), m.index, rotation=45)
            plt.yticks(numpy.arange(0.5, len(m.columns), 1), m.columns)
            plt.xlabel(self.time)
            plt.ylabel("level")
            plt.colorbar()
            plt.title("Level {} matrix: {}".format(self.time, desc))
            plt.savefig(fname + ".pdf")
            plt.close()

        # Bokeh plot
        m.columns = list(map(str, m.columns))  # convert column labels to please Bokeh

        fig = bkp.figure(
            toolbar_location=None,
            tools="",
            width=1280,
            height=1280,
            title="Level {} aggregate {}".format(self.time, desc),
            x_axis_label=self.time,
            y_axis_label=desc,
            y_range=(-0.02, 0.40),
        )
        fig.xaxis[0].ticker.desired_num_ticks = m.index.size
        fig.xaxis.minor_tick_line_color = None
        fig.xaxis.major_label_orientation = numpy.pi / 4
        cpal = bkpa.Category10[len(m.columns)]
        source = bkm.ColumnDataSource(m)
        for n, col in enumerate(reversed(m.columns)):
            fig.line(
                "index",
                col,
                source=source,
                legend="level {}".format(col),
                color=cpal[n],
                line_width=3,
            )
            fig.circle("index", col, source=source, color=cpal[n], size=6)
        bkp.output_file(
            fname + ".html", title="Level {} agg {} ({})".format(self.time, desc, scale)
        )
        bkp.save(fig)

    def plot_inblocktime_cor(self, yaxis, scale="linear"):
        """
        Correlate with item's position inside its block's temporal sequence.
        """
        yaxis, time = map(self.serify, (yaxis, self.time))
        blocks = self.blocks.loc[time.index]
        fname = os.path.join(
            self.analysis_dir,
            "inblocktimecor-{}-x-{}-{}.pdf".format(
                time.name, yaxis.name, "".join(scale)
            ),
        )

        with PdfPages(fname) as pdf:
            ylim = (yaxis.loc[blocks.index].min(), yaxis.loc[blocks.index].max())
            for level in reversed(x for x in blocks if type(x) is int):
                x, y = list(), list()
                for b in blocks[level].unique():  # FIXME: check unique
                    btime = time.loc[blocks[level] == b].sort_values()
                    btime = pandas.Series(range(btime.size), index=btime.index)
                    qtiles = btime.quantile([x / 10 for x in range(11)])
                    c = pandas.cut(
                        btime, qtiles, include_lowest=True, labels=list(range(1, 11))
                    )
                    x.extend(c)
                    y.extend(yaxis.loc[btime.index])
                points = pandas.Series(y, index=x)
                plt.yscale(scale)
                xedges = numpy.linspace(
                    points.index.min() - 0.5, points.index.max() + 0.5, num=11
                )
                yedges = (
                    numpy.logspace(
                        numpy.log10(points.min() + 0.02),
                        numpy.log10(points.max() + 1),
                        num=22,
                    )
                    if scale == "log"
                    else numpy.linspace(points.min(), points.max(), num=11)
                )
                H, xedges, yedges = numpy.histogram2d(
                    x,
                    points.replace(0, 0.02) if scale == "log" else y,
                    bins=(xedges, yedges),
                )
                X, Y = numpy.meshgrid(xedges, yedges)
                plt.pcolormesh(X, Y, H.T, norm=colors.LogNorm())
                plt.xticks(xedges + 0.5)
                plt.colorbar()
                plt.plot(points.groupby(points.index).mean(), color="red", linewidth=2)
                plt.title("Block level {}: {}".format(level, yaxis.name))
                pdf.savefig()
                plt.close()

    def plot_series(self, df, scale="linear", desc=None, styles=None):
        """
        Use Bokeh to plot a bunch of series passed as args
        """
        if not desc:
            desc = ", ".join(c for c in df.columns)
        fname = os.path.join(
            self.analysis_dir,
            "series of {} by {} - s_{}".format(desc, df.index.name, scale),
        )

        fig = bkp.figure(
            toolbar_location=None,
            tools="",
            width=1280,
            height=1024,
            title="Series of {} by {}".format(desc, df.index.name),
            x_axis_label=df.index.name,
            y_axis_label="value",
        )
        if df.index.size < 30:
            fig.xaxis[0].ticker.desired_num_ticks = df.index.size
            fig.xaxis.minor_tick_line_color = None
        fig.xaxis.major_label_orientation = numpy.pi / 4
        cpal = bkpa.Category10[max(len(df.columns), 3)]
        source = bkm.ColumnDataSource(df)
        styles = styles if styles else df.columns.size * ["line"]
        for n, (col, style) in enumerate(zip(df.columns, styles)):
            if style == "line":
                fig.line(
                    df.index.name,
                    col,
                    source=source,
                    legend="level {}".format(col),
                    color=cpal[n],
                    line_width=3,
                )
                fig.circle(df.index.name, col, source=source, color=cpal[n], size=6)
            if style == "vbar":
                fig.vbar(
                    df.index.name,
                    top=col,
                    width=0.5,
                    source=source,
                    legend="{} ".format(col),
                    color=cpal[n],
                )
        bkp.output_file(
            fname + ".html",
            title="Series of {} by {} ({})".format(desc, df.index.name, scale),
        )
        bkp.save(fig)

    @cache
    def get_dblock_time_wordcount(self, b, column=None):
        column = self.column if column is None else column
        level = len(self.dblocks_levels) - len(b) + 1
        bdata = self.data.loc[self.dblocks[level] == b[-1]]
        tc = OrderedDict()
        for n, g in bdata.groupby(self.time):
            tc[n] = Counter(w for d in g[column].values for w in sum(d, ()))
        return tc

    def get_dblock_time_words(self, b, order, n=10):
        twc = self.get_dblock_time_wordcount(b)
        ret = pandas.Series(index=list(twc))
        if order == "local_specificity":
            if len(b) > 1:
                uptwc = self.get_dblock_time_wordcount(b[:-1])
            else:
                uptwc = twc
            for time in twc:
                wc, upwc = twc[time], uptwc[time]

                def keyf(x):
                    return -wc[x] * numpy.log1p(wc[x]) / upwc[x]

                ret[time] = " ".join(sorted(wc, key=keyf)[:n])
        elif order == "global_specificity":
            if len(b) > 1:
                toptwc = self.get_dblock_time_wordcount(b[:-1])
            else:
                toptwc = twc
            for time in twc:
                wc, topwc = twc[time], toptwc[time]

                def keyf(x):
                    return -wc[x] * numpy.log1p(wc[x]) / topwc[x]

                ret[time] = " ".join(sorted(wc, key=keyf)[:n])
        elif order == "frequency":

            def keyf(x):
                return lambda x: -wc[x]

        for time in set(self.data[self.time].unique()).difference(twc):
            ret[time] = ""
        return ret

    def plot_blockwords_time_matrix(self, level0, node0, limit=100, scale="linear"):
        """
        Plots the relative frequency of the `limit` words most employed in
         bloc `node0` from `level0` of a BlockState.
        A document histogram is placed on top to better understand the
        dispersion.
        If `limit` is 0, all words are displayed, but this tends to crash
        matplotlib.
        """
        level1 = 0
        if data is None:
            data = self.data
        blocks = self.blocks.loc[data.index]

        g = self.state.levels[level1].g
        p = self.state.project_partition(level0 - 1, level1)
        nodes0 = [v for v in g.vertices() if p[v] == node0 and v in blocks["v"]]
        nodes1 = sorted(
            set(w for v in nodes0 for w in v.out_neighbors()),
            key=lambda x: g.vp["name"][x],
        )
        m = pandas.DataFrame(
            0,
            columns=[g.vp["name"][v] for v in nodes1],
            index=sorted(set(g.ep[self.time])),
        )
        for v in nodes0:
            for e in v.out_edges():
                m.loc[g.ep[self.time][e], g.vp["name"][e.target()]] += 1
        m = m.div(m.sum(axis=1), axis=0)  # normalize within year
        m = m.loc[:, m.sum().sort_values().index[-limit:]]
        desc = [node0]
        for bs in self.state.levels[level0:-1]:
            desc.insert(0, bs.b[desc[0]])
        desc = tuple(desc)
        fname = os.path.join(
            self.analysis_dir, "blockwords_{}_matrix-{}.pdf".format(self.time, desc)
        )
        with PdfPages(fname) as pdf:
            # plot a document histogram
            ax = plt.figure(figsize=(20, 4)).gca()
            pandas.Series(
                data.loc[self.blocks[level0] == node0, self.time].value_counts(
                    sort=False
                ),
                index=sorted(data[self.time].unique()),
            ).plot.bar(ax=ax)
            ax.set(
                title="Documents per {} in {}".format(self.time, desc),
                ylabel="count",
                xlabel=self.time,
            )
            plt.xticks(rotation=45)
            plt.tight_layout()
            pdf.savefig()
            plt.close()

            # plot the matrix
            ax = plt.figure(figsize=(20, 2 + m.columns.size / 4)).gca()
            norm = colors.LogNorm() if scale == "log" else colors.Normalize()
            plt.pcolormesh(
                numpy.ma.masked_array(m.values, m.isnull()).T, cmap="OrRd", norm=norm
            )
            plt.colorbar(shrink=17 / max(17, plt.gcf().get_figheight()))
            plt.title("Word {} matrix: {}".format(self.time, desc), y=1.02)
            ax.set(xlabel=self.time, ylabel="words")
            plt.tick_params(top=True, labeltop=True)
            plt.xticks(numpy.arange(0.5, len(m.index), 1), m.index, rotation=45)
            plt.yticks(numpy.arange(0.5, len(m.columns), 1), m.columns)
            plt.tight_layout()
            pdf.savefig()
            plt.close()

    @cache
    def get_crossblock_links(self, level0, node0, level1):
        """
        For node node0 at level L0, get out and in neighbours relative to L1
        plus weights.
        * L0==L1: node0's in and out neighbours
        * L0>L1: project node0 onto several nodes in L1, add their out and in
                 neighbours
        * L0<L1: take node0's out and in neighbours, project them onto L1
        Returns two dictionaries, mapping out and in neighbours to weights.
        """
        links, inlinks = dict(), dict()
        if level0 == level1:
            if level0 == 0:
                v0 = self.state.g.vertex(node0)
                for e in v0.out_edges():
                    links[e.target()] = links.get(e.target(), 0) + 1
                if self.state.g.is_directed():
                    for e in v0.in_edges():
                        inlinks[e.source()] = inlinks.get(e.source(), 0) + 1
            else:
                g = self.state.level[level0 - 1].bg
                v0 = g.vertex(node0)
                for e in v0.out_edges():
                    links[e.target()] = links.get(e.target(), 0) + g.ep["eweight"][e]
                if self.state.g.is_directed():
                    for e in v0.in_edges():
                        inlinks[e.source()] = (
                            inlinks.get(e.source(), 0) + g.ep["eweight"][e]
                        )
            if v0 in links and self.state.g.is_directed():
                links[v0] /= 2
        if level0 > level1:
            g = (
                self.state.levels[level1 - 1].bg
                if level1 > 0
                else self.state.levels[level1].g
            )
            p = self.state.project_partition(level0 - 1, level1)
            nodes0 = (v for v in g.vertices() if p[v] == node0)
            for v in nodes0:
                for e in v.out_edges():
                    links[e.target()] = links.get(e.target(), 0) + (
                        g.ep["eweight"][e] if level1 > 0 else 1
                    )
                if self.state.g.is_directed():
                    for e in v.in_edges():
                        inlinks[e.source()] = inlinks.get(e.source(), 0) + (
                            g.ep["eweight"][e] if level1 > 0 else 1
                        )
        elif level0 < level1:
            g = (
                self.state.level[level0 - 1].bg
                if level0 > 0
                else self.state.level[level0].g
            )
            p = self.state.project_partition(level1 - 1, level0)
            v = g.vertex(node0)
            for e in v.out_edges():
                links[p[e.target()]] = links.get(e.target(), 0) + (
                    g.ep["eweight"][e] if level0 > 0 else 1
                )
            if self.state.g.is_directed():
                for e in v.in_edges():
                    inlinks[p[e.source()]] = inlinks.get(e.source(), 0) + (
                        g.ep["eweight"][e] if level0 > 0 else 1
                    )
        return links, inlinks

    def get_label_keys(self, keyf, llinks, ulinks, tlinks, m, b):
        lblinks = dict(i for i in llinks.items() if i[0][-2] == b[-2])
        nb = len(lblinks)

        def mb(x):
            return ulinks[x] / nb

        blinks = lblinks[b]

        def expected_spread(x):
            return nb * (1 - ((nb - 1) / nb) ** ulinks[x])

        def spread(x):
            return (
                nb
                - sum(abs(lblinks[lb].get(x, 0) - mb(x)) / mb(x) for lb in lblinks) / 2
            )

        func = {
            "cool": lambda x: -(blinks[x] / ulinks[x]) * numpy.log(blinks[x]),
            "naive": lambda x: ulinks[x] / blinks[x],
            "tfcon": lambda x: -blinks[x] * numpy.log(expected_spread(x) / spread(x)),
        }[keyf]

        def debugfunc(x):
            import pdb

            if expected_spread(x) == 0 or spread(x) <= 0:
                print(spread(x), ulinks[x], lblinks[b][x], mb(x), b, x)
                pdb.set_trace()
            return func(x)

        return func

    def serve_blockmodel(self, port=8888):
        from http import server

        class Handler(server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/exit":
                    raise SystemExit
                spath = self.path.split("/")
                if spath[1] == "block":
                    self.wfile.write("block".encode())
                elif spath[1] == "nodelinks":
                    self.wfile.write("nodelinks".encode())
                elif spath[1] == "nodeinfo":
                    self.wfile.write("nodeinfo".encode())
                else:
                    self.send_error(404)

        srvr = server.HTTPServer(("localhost", port), Handler)
        try:
            try:
                srvr.serve_forever()
            except SystemExit:
                pass
        except KeyboardInterrupt:
            print("Stopping server...")
        srvr.shutdown()
        srvr.server_close()
