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

from collections import Counter
from functools import cache

import pandas as pd

from ..corpus import Corpus
from ..graph_models import blockstate_to_dataframes
from .hierarchical_block_map import composite_hierarchical_block_map
from . import zmethods
from .tables import subxblocks_report, xblocks_report
from .network_map import network_map


class Blocks:
    """
    Methods to produce visualisations and analysis from an existing blockstate.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.col_title is None:
            print("Warning: `col_title` is not set")

    @property
    def dblocks_levels(self):
        return [x for x in self.dblocks if isinstance(x, int)]

    @property
    def tblocks_levels(self):
        return [x for x in self.tblocks if isinstance(x, int)]

    @property
    def eblocks_levels(self):
        return [x for x in self.eblocks if isinstance(x, int)]

    def get_blocks_levels(self, btype=None, *, orig=False) -> tuple[pd.DataFrame, list]:
        """
        Parameters
        ----------
        btype: the type of block to return ('doc', 'ter' or 'ext')

        Returns
        -------
        blocks: the original blocks
        levels: the levels
        """
        bprefix = "_orig_" if orig else ""
        if btype is None:
            return {
                "doc": (
                    getattr(self, f"{bprefix}dblocks", self.dblocks),
                    self.dblocks_levels,
                ),
                "ter": (
                    getattr(self, f"{bprefix}tblocks", self.tblocks),
                    self.tblocks_levels,
                ),
                "ext": (
                    getattr(self, f"{bprefix}eblocks", self.eblocks),
                    self.eblocks_levels,
                ),
            }
        elif btype == "doc":
            return getattr(self, f"{bprefix}dblocks", self.dblocks), self.dblocks_levels
        elif btype == "ter":
            return getattr(self, f"{bprefix}tblocks", self.tblocks), self.tblocks_levels
        elif btype == "ext":
            return getattr(self, f"{bprefix}eblocks", self.eblocks), self.eblocks_levels
        else:
            raise ValueError("Unrecognized `btype`.")

    def hblock_to_level_block(self, hb, btype):
        blocks, levels = self.get_blocks_levels(btype)
        levels = ["v", *levels]
        level, block = levels[-len(hb)], hb[-1]
        true_hb = self.level_block_to_hblock(level, block, btype)
        if hb == true_hb:
            return level, block
        else:
            raise ValueError(f"False hblock: {hb}")

    def level_block_to_hblock(self, level, block, btype):
        blocks, levels = self.get_blocks_levels(btype)
        if level == "v":
            levels = ["v", *levels]
        b = blocks.loc[blocks[level].eq(block), levels[levels.index(level) :]]
        return tuple(reversed(b.iloc[0].tolist()))

    def get_sublevel(self, level, btype):
        _, levels = self.get_blocks_levels(btype)
        return levels[levels.index(level) - 1]

    def domain_labels_to_selection(self, labels):
        level_blocks = {}
        for label in labels:
            _, level, block = self.label_to_tlblock[label]
            level_blocks.setdefault(level, []).append(block)
        sel = pd.Series(False, self.data.index)
        for level, blocks in level_blocks.items():
            sel |= self.dblocks[level].isin(blocks)
        return sel

    def set_sample(self, sample, keep=False, trim=True):
        Corpus.set_sample(self, sample=sample, keep=keep)
        if trim:
            self.trim_to_sample()

    def trim_to_sample(self):
        self.cache_clear(clear_static=True)
        if not hasattr(self, "dblocks"):
            return
        if not hasattr(self, "_orig_dblocks"):
            self._orig_dblocks = self.dblocks.copy()
        self.dblocks = self._orig_dblocks.loc[self.data.index].copy()
        if hasattr(self, "tblocks") and not self.tblocks.empty:
            self.load_ter_documents()
            if not hasattr(self, "_orig_tblocks"):
                self._orig_tblocks = self.tblocks.copy()
            self.tblocks = self._orig_tblocks[
                self._orig_tblocks.index.isin(self.ter_documents)
            ].copy()
        if hasattr(self, "eblocks") and not self.eblocks.empty:
            self.load_ext_documents()
            if not hasattr(self, "_orig_eblocks"):
                self._orig_eblocks = self.eblocks.copy()
            self.eblocks = self._orig_eblocks[
                self._orig_eblocks.index.isin(self.ext_documents)
            ].copy()
        blockstate_to_dataframes.remove_redundant_levels(self)
        blockstate_to_dataframes.gen_mapindex(self)

    def find_blocks(self, lscape, finder):
        """
        Returns the blocks that correspond to features defined in finder.
        For example, blocks with the highest or lowest values, or with
        the highest or lowest differences in values across the landscape.

        Parameters
        ----------
        lscape: dict of pandas.Series or pandas.DataFrames
            The landscape of values for each level over its blocks.
        finder: str or function
            Finds the desired blocks in the landscape.

        Returns
        -------
        found: dict
            Dictionary containing whatever `finder` looked for.
        """
        if callable(finder):
            return finder(self, lscape)

        found = dict()
        if finder == "level_max_min_absmin":
            for level, ls_l in lscape.items():
                if isinstance(ls_l, pd.Series):
                    found[level] = dict(
                        max=ls_l.idxmax, min=ls_l.idxmin, absmin=ls_l.abs().idxmin()
                    )
                elif isinstance(ls_l, pd.DataFrame):
                    idxmax = ls_l.max().idxmax()
                    idxmin = ls_l.min().idxmin()
                    idxabsmin = ls_l.abs().min().idxmin()
                    found[level] = dict(
                        max=(ls_l.idxmax()[idxmax], idxmax),
                        min=(ls_l.idxmin()[idxmin], idxmin),
                        absmin=(ls_l.abs().idxmin()[idxabsmin], idxabsmin),
                    )
                else:
                    raise ValueError("Unrecognized type in values of `lscape`.")
        return found

    def domain_map(self, title=None, diff_idxs=None, chained=False, **kwargs):
        idx_all = self.data.index.copy()
        idx_all.name = "all"
        btype = "ext" if chained else "ter"

        if not diff_idxs:
            kwargs_ = dict(
                norm=["bylevelmax", "bylevelmax"],
                scale=["linear", "linear"],
                bheight=["proval", "hierarchical"],
            )
            kwargs_.update(kwargs)
            return composite_hierarchical_block_map(
                self,
                ["doc", btype],
                zmethod=[
                    zmethods.density,
                    zmethods.x_link_density_gen(btype),
                ],
                link_p_func=zmethods.p_rel,
                page_title=title,
                **kwargs_,
            )

        else:
            idx0, idx1 = diff_idxs
            kwargs_ = dict(
                norm=["bylevelmax", "bylevelmax"],
                scale=["linear", "log"],
                bheight=["proval", "hierarchical"],
            )
            kwargs_.update(kwargs)
            return composite_hierarchical_block_map(
                self,
                ["doc", btype],
                zmethod=[
                    zmethods.density_pair_gen(idx0, idx1, zmethods.p_diff),
                    zmethods.x_link_density_pair_gen(idx0, idx1, zmethods.p_rel, btype),
                ],
                link_p_func=zmethods.p_rel,
                page_title=title,
                **kwargs_,
            )

    def subxblocks_tables(self, xbtype, xlevel, xb, ybtype, ylevel=1):
        outpaths = []
        outdir = self.blocks_adir if ybtype == "ter" else self.chained_adir
        if xb is None:
            xblocks, _ = self.get_blocks_levels(xbtype)
            xbtargets = xblocks[xlevel].unique()
        elif isinstance(xb, list):
            xbtargets = xb
        else:
            xbtargets = [xb]
        for xbt in xbtargets:
            if sample_hash := self.get_sample_hash(doc=True, ter=True, ext=True):
                sample_hash = f"-sample:{sample_hash}"
            outfile = f"table{sample_hash}-{self.lblock_to_label[xlevel, xbt]}"
            outfile += f"-L{ylevel}{ybtype[0].upper()}.html"
            fname = subxblocks_report(
                self,
                xbtype,
                xlevel,
                xbt,
                ybtype,
                ylevel,
                outfile=outdir / outfile,
            )
            outpaths.append(fname)
        return outpaths if isinstance(xb, list) or xb is None else outpaths.pop()

    def xblocks_tables(self, *args, **kwargs):
        return xblocks_report(self, *args, **kwargs)

    def domain_network(self, *args, **kwargs):
        return network_map(self, "doc", *args, **kwargs)

    def network_map(self, *args, **kwargs):
        return network_map(self, *args, **kwargs)

    def filter_topic_terms_from_corpus(self, tlevel, tblock, column=None):
        """
        Removes all terms belonging to a topic from the corpus.
        """
        topic_terms = set(self.tblocks[self.tblocks[tlevel].eq(tblock)].index)
        return self.filter_terms(lambda term: term not in topic_terms, column)

    @cache
    def get_xelement_yelements(self, xbtype, ybtype):
        if (xbtype, ybtype) == ("doc", "ter"):
            series = pd.Series(self.get_doc_terms(), index=self.dblocks.index)
        if (xbtype, ybtype) == ("doc", "ext"):
            series = pd.Series(self.get_doc_exts(), index=self.dblocks.index)
        if (xbtype, ybtype) == ("ter", "doc"):
            series = pd.Series(self.ter_documents, index=self.tblocks.index)
        if (xbtype, ybtype) == ("ext", "doc"):
            series = pd.Series(self.ext_documents, index=self.eblocks.index)
        return series.map(
            lambda x: x
            if isinstance(x, Counter)
            else Counter()
            if (isinstance(isna := pd.isna(x), bool) and isna)
            else Counter(x)
        )

    def get_xsel_yblocks_counts(self, xbtype, xsel, ybtype, ylevel):
        xelement_yelements = self.get_xelement_yelements(xbtype, ybtype)
        xblocks, _ = self.get_blocks_levels(xbtype)
        yblocks, _ = self.get_blocks_levels(ybtype)
        yelement2yblock = (lambda x: x) if ylevel is None else yblocks[ylevel].get
        xblock_yblocks_c = Counter()
        for val in xelement_yelements.loc[xsel]:
            xblock_yblocks_c.update(yelement2yblock(el) for el in val.elements())
        return xblock_yblocks_c

    @cache
    def get_xblock_yblocks_counts(self, xbtype, xlevel, xb, ybtype, ylevel):
        xblocks, _ = self.get_blocks_levels(xbtype)
        xsel = (xblocks.index == xb) if xlevel is None else xblocks[xlevel].eq(xb)
        return self.get_xsel_yblocks_counts(xbtype, xsel, ybtype, ylevel)

    def get_antixblock_sel(self, xbtype, xlevel, xb, antixlevel=None):
        """
        Selects the complement of a block `xb` of level `xlevel` and type `xbtype`.
        (antixlevel): restrict selection to this parent (higher) xlevel
        """
        xblocks, _ = self.get_blocks_levels(xbtype)
        xsel = (xblocks.index == xb) if xlevel is None else xblocks[xlevel].eq(xb)
        xsel = ~xsel
        if antixlevel is not None:
            if antixlevel <= xlevel:
                raise ValueError("`antixlevel` must be higher than `xlevel`")
            antixlevel_xblock_containing_xb = xblocks.loc[~xsel, antixlevel].iloc[0]
            antixsel = xblocks[antixlevel].eq(antixlevel_xblock_containing_xb)
            xsel = xsel & antixsel
        return xsel

    @cache
    def get_antixblock_yblocks_counts(
        self,
        xbtype,
        xlevel,
        xb,
        antixlevel=None,
        ybtype="ter",
        ylevel=1,
    ):
        xsel = self.get_antixblock_sel(xbtype, xlevel, xb, antixlevel)
        return self.get_xsel_yblocks_counts(xbtype, xsel, ybtype, ylevel)

    def get_xblock_yblocks_stat(
        self, stat, xbtype, xlevel, xb, ybtype, ylevel, ybs=None
    ):
        """
        Gets the `stat` = "count" or "frac_presence" of yblocks in xblocks.
        """
        ybs = None if ybs is None else set(ybs)
        if stat not in ("count", "frac_presence"):
            raise ValueError(f"Unkown statistics: {stat}")
        xelements_yelements = self.get_xelement_yelements(xbtype, ybtype)
        xblocks, _ = self.get_blocks_levels(xbtype)
        yblocks, _ = self.get_blocks_levels(ybtype)

        # functions to abstract different cases
        yelement2yblock = (lambda x: x) if ylevel is None else yblocks[ylevel].get

        def yelements2yblocks(xel_yels):
            return (yelement2yblock(el) for el in xel_yels.elements())

        yelements2yblocks4stat = (
            yelements2yblocks
            if (stat == "count")
            else (lambda xel_yels: set(yelements2yblocks(xel_yels)))
        )
        any_cum_func = len if stat == "count" else bool

        # calculations
        xblock_yblocks_c = Counter()
        xblock_yblocks_any = 0
        sel = (xblocks.index == xb) if xlevel is None else xblocks[xlevel].eq(xb)
        for xel_yels in xelements_yelements.loc[sel]:
            yblocks4stat = [*yelements2yblocks4stat(xel_yels)]
            xblock_yblocks_c.update(yblocks4stat)
            xblock_yblocks_any += any_cum_func(
                [yb for yb in yblocks4stat if (ybs is None) or (yb in ybs)]
            )

        stat_s = pd.Series(xblock_yblocks_c).sort_values()
        stat_s.name = self.lblock_to_label[xlevel, xb]
        stat_s["any"] = xblock_yblocks_any
        stat_s = stat_s.div(sel.sum()) if stat == "frac_presence" else stat_s
        return stat_s

    def get_dblock_xcount(self, b, btype):
        dlevel, db = self.hblock_to_level_block(b, "doc")
        xc = self.get_xblock_yblocks_counts("doc", dlevel, db, btype, None)
        xct = sum(xc.values())
        return xc, xct

    def get_dblock_xblock_count(self, b, btype):
        dlevel, db = self.hblock_to_level_block(b, "doc")
        xc = self.get_xblock_yblocks_counts("doc", dlevel, db, btype, 1)
        xct = sum(xc.values())
        return xc, xct
