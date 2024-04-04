from functools import cache, partial

import numpy as np
from tqdm import tqdm
from bokeh.models.callbacks import CustomJS

from .util import sorted_hierarchical_block_index, make_normalization_factor_js


def link_maps(
    corpus,
    source_btype,
    source_fig,
    source_blocks,
    source_levels,
    target_btype,
    target_fig,
    target_blocks,
    target_levels,
    values,
    selection_mode,
    pfunc=None,
    norm="bylevelmax",
):
    """
    Once linked, clicking on a block in the source map produces a change on the target map's z-axis.

    Currently this implements an x_{doc,link}_density_pair calculation with pfunc against all.

    Tested with norm='bylevelmax' and pfunc=p_rel (scale='log').

    Parameters
    ==========
    values:
        A `pandas.Series` of scalar values with `MultiIndex` like
        (source level, source block, target level, target block)
    """
    # flip around `values` if docs are target, and make sure index is sorted
    if target_btype == "doc":
        values = values.reorder_levels([2, 3, 0, 1])
    values = values.sort_index()

    # size calculating functions
    if "ter" in (source_btype, target_btype):
        doc_xs_sizes = corpus.get_doc_terms().transform(len)
    elif "ext" in (source_btype, target_btype):
        doc_xs_sizes = corpus.get_doc_exts().transform(len)

    def get_doc_source_links_sizes(source_level, source_b):
        return doc_xs_sizes.loc[source_blocks[source_level].eq(source_b)].sum()

    @cache
    def get_x_source_links_sizes(target_level):
        return target_blocks.groupby(target_level)[target_level].agg(
            lambda x: doc_xs_sizes.loc[x.index.intersection(doc_xs_sizes.index)].sum()
        )

    def get_doc_source_doc_sizes(source_level, source_b, target_level):
        return source_blocks[source_level].eq(source_b).sum()

    def get_x_source_doc_sizes(source_level, source_b, target_level):
        return target_blocks.groupby(target_level).size()

    # TODO param to choose between link and doc
    get_doc_source_sizes, get_x_source_sizes = (
        get_doc_source_links_sizes,
        get_x_source_links_sizes,
    )

    # apply pfunc between local values and total (top of hierarchy) values
    def apply_pfunc(vals):
        if pfunc is not None:
            if source_btype == "doc":
                ((b_top, g_top),) = values[(max(source_levels),)].groupby(level=0)
                vals_all = g_top[(b_top, target_level)]
                sizes = get_doc_source_sizes(max(source_levels), b_top)
                return pfunc(vals, vals_all / sizes)
            elif target_btype == "doc":
                (val_all,) = values[(source_level, source_hb[-1], max(target_levels))]
                (size,) = get_x_source_sizes(max(target_levels))
                return pfunc(vals, val_all / size)
            else:
                return vals

    get_target_hbindex = cache(partial(sorted_hierarchical_block_index, target_blocks))
    fix_nans = make_fix_nans(getattr(pfunc, "__name__", None))

    st_val = []  # st_val[source_map_index][target_map_index]: values
    total_blocks = sum(source_blocks.groupby(level).ngroups for level in source_levels)
    prog = tqdm(desc=f"Linking {source_btype} to {target_btype}", total=total_blocks)
    for source_level in list(reversed(source_levels)):
        source_hbindex = sorted_hierarchical_block_index(
            source_blocks, source_levels, source_level
        )
        for source_hb in source_hbindex:
            st_val.append([])
            for target_level in reversed(target_levels):
                target_hbindex = get_target_hbindex(tuple(target_levels), target_level)
                target_bindex = [thb[-1] for thb in target_hbindex]

                vals = values.loc[(source_level, source_hb[-1], target_level)]

                # fraction of domain
                sizes = (
                    get_doc_source_sizes(source_level, source_hb[-1])
                    if source_btype == "doc"
                    else get_x_source_sizes(target_level)
                )
                vals = vals / sizes

                # pfunc with baseline
                vals = apply_pfunc(vals)

                # store non normalized data (after fixing possible? nans)
                st_val[-1].extend(vals.map(fix_nans).loc[target_bindex].to_list())

            prog.update()
    prog.close()

    level_bounds = (
        target_blocks[reversed(target_levels)]
        .agg(lambda s: len(s.unique()))
        .cumsum()
        .to_list()
    )

    target_datasource = target_fig.select_one("{}_map_data".format(target_btype))
    source_datasource = source_fig.select_one("{}_map_data".format(source_btype))
    link_cb = CustomJS(
        args=dict(
            selected=source_datasource.selected,
            target_datasource=target_datasource,
            st_value=st_val,
            level_bounds=level_bounds,
            norm=norm,
            pfunc_kind=getattr(pfunc, "__name__", None),
            selection_mode=selection_mode,
        ),
        code=(link_maps_js()),
    )
    source_datasource.selected.js_on_change("change:indices", link_cb)
    selection_mode.js_on_change("value", link_cb)


def link_maps_js():
    return (
        make_fix_nans_js()
        + make_normalization_factor_js()
        + """
    const num_sources = selected.indices.length
    const new_target_data = { ...target_datasource.data }
    const combine = function(sm) {
        if (sm == "single") { return x => x[0] }
        if (sm == "multi AND") { return x => Math.min(...x) }
        if (sm == "multi OR") { return x => Math.max(...x) }
    }(selection_mode.value)
    const repr = function(x) {
        if ((0 < x) && (x < 1)) { return '(' + (1/x).toPrecision(2) + ')' }
        else { return x.toPrecision(2)}
    }
    const normalization_factor = make_normalization_factor(norm)
    const fix_nans = make_fix_nans(pfunc_kind)
    if (num_sources == 0) { // simple volue map
        new_target_data.z = [...new_target_data.o_z]
        new_target_data.value = [...new_target_data.o_value]
        new_target_data.text = new_target_data.o_value.map(x => x.toPrecision(2))
    }
    else if (num_sources > 0) { // single or multiple source relative map
        const value = [...st_value[selected.indices[0]]]
        if (num_sources > 1) {
            for (let i = 0; i < value.length; i++) {
                const values_i = [value[i]]
                for (const index of selected.indices.slice(1)) {
                    values_i.push(st_value[index][i])
                }
                value[i] = combine(values_i)
            }
        }
        let z
        if (pfunc_kind == "p_rel") {
            z = value.map(Math.log)
        } else {
            z = [...value]
        }
        let prev_bound = 0
        for (const bound of level_bounds) {
            const norm_factor = normalization_factor(z.slice(prev_bound, bound))
            z.splice(
                prev_bound,
                bound - prev_bound,
                ...z.slice(prev_bound, bound).map(x => x / norm_factor).map(fix_nans),
            )
            prev_bound = bound
        }
        new_target_data.value = value
        new_target_data.z = z
        new_target_data.text = value.map(repr)
    }
    target_datasource.data = new_target_data
    """
    )


def make_fix_nans(kind):
    """
    from Python we're fixing for 'value'
    that means BEFORE log and normalization
    """
    if kind is None:
        return lambda x: x
    elif kind in ("p_rel", "p_diff"):
        nan_value = int(kind == "p_rel")
        return lambda x: nan_value if np.isnan(x) else x
    else:
        raise ValueError


def make_fix_nans_js():
    """
    from Javascript we're fixing for 'z' (color)
    that means AFTER log and normalization
    """
    return """
    function make_fix_nans(kind) {
        if (kind == "p_rel" || kind == "p_diff") return x => Number.isNaN(x) ? 0 : x
        else return x => x
    }
    """
