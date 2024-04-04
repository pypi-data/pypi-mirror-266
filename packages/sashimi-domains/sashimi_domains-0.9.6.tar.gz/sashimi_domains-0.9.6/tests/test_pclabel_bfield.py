import graph_tool.all as gt
import numpy as np

from sashimi.graph_models.domain_chained_model import gen_chained_nested_blockstate

VERBOSE = True

if VERBOSE:
    log = print
else:

    def log(*args, **kwargs):
        None


def test_all(name="celegansneural", minimize=True):
    g = get_graph(name)
    split_N = get_half_N(g)
    bs, pclabel, bfield = get_state_test_params(g, split_N)

    bstate = gt.BlockState(g, bs[0], pclabel=pclabel, bfield=bfield)
    nbstate = get_nbstate(g, bs, pclabel, bfield)

    if minimize:
        slice_eql, slice_dif = get_slices(split_N)
        test_bstate(bstate, slice_eql, slice_dif)
        test_nbstate(nbstate, slice_eql, slice_dif)

    return bstate, nbstate


def test_bstate(bstate, slice_eql, slice_dif):
    b = bstate.b.a.copy()
    bstate.multiflip_mcmc_sweep(beta=np.inf, niter=10)
    if VERBOSE:
        log("b equal")
        log(b[slice_eql])
        log("b dif")
        log(b[slice_dif])
        log(bstate.b.fa[slice_dif])
        log(flush=True)
    assert np.array_equal(bstate.b.fa[slice_eql], b[slice_eql])
    assert not np.array_equal(bstate.b.fa[slice_dif], b[slice_dif])


def test_nbstate(nbstate, slice_eql, slice_dif):
    bs = [b.copy() for b in nbstate.get_bs()]
    for i in range(1000):  # this should be sufficiently large
        nbstate.multiflip_mcmc_sweep(
            beta=np.inf, niter=10, ls=[*range(len(nbstate.levels) - 1)]
        )
    bstate_slice_dif = slice_dif
    for i, (b, bstate) in enumerate(zip(bs, nbstate.levels)):
        if VERBOSE:
            log(f"l{i} b equal")
            log(b[slice_eql])
            log(len({*b[slice_eql]}))
            log(f"l{i} b dif")
            log(b[slice_dif])
            log(bstate.b.fa[bstate_slice_dif])
            log(len({*bstate.b.fa[bstate_slice_dif]}))
            log(flush=True)
        assert np.array_equal(b[slice_eql], bstate.b.fa[slice_eql])
        if len({*bstate.b.fa[bstate_slice_dif]}) > 1:
            assert not np.array_equal(b[slice_dif], bstate.b.fa[bstate_slice_dif])
        slice_eql = b[slice_eql]
        slice_dif = b[slice_dif]
        bstate_slice_dif = bstate.b.fa[bstate_slice_dif]
    nbstate.print_summary()


def get_state_test_params(g, split_N):
    N = g.num_vertices()
    b = np.array(range(N))
    b_split = np.array(range(N))
    bs_top = [np.array([0, 1]), np.array([0, 1]), np.array([0, 1]), np.array([0, 0])]
    pclabel = g.new_vertex_property("int")
    bfield = g.new_vertex_property("vector<double>")
    for i, v in enumerate(g.vertices()):
        if i < split_N:
            b_split[i] = 0
            pclabel[v] = 0
            bfield[v] = freeze_in_block(b[i])
        else:
            pclabel[v] = 1
            b_split[i] = 1
    return [b, b.copy(), b_split] + bs_top, pclabel, bfield


def propagate_bfield(nbstate):
    for bstate_under, bstate_current in zip(nbstate.levels, nbstate.levels[1:-1]):
        for i, v in enumerate(bstate_current.g.vertices()):
            if any(
                bstate_under.bfield[w]
                for j, w in enumerate(bstate_under.g.vertices())
                if bstate_under.b[j] == i
            ):
                bstate_current.bfield[v] = freeze_in_block(bstate_current.b[i])
    return nbstate


def get_nbstate(g, bs, pclabel=None, bfield=None):
    nbstate = gt.NestedBlockState(
        g, bs, state_args={"pclabel": pclabel, "bfield": bfield}
    )
    propagate_bfield(nbstate)
    return nbstate


def get_graph(name):
    if name in gt.collection.data:
        return gt.collection.data[name]
    g = gt.Graph()
    if name == "n12e2":
        g.add_edge_list([(0, 10), (0, 11)])
    if name == "n4e3":
        g.add_edge_list([(0, 1), (0, 2), (0, 3)])
    if name != "n0e0" and not g.num_vertices():
        raise ValueError("Graph name undefined")
    return g


def freeze_in_block(block):
    """
    Returns the bfield value to freeza a vertex at block.
    """
    return block * [-np.inf] + [0, -np.inf]


def get_half_N(g):
    return ((g.num_vertices() - 1) // 2) + 1


def get_slices(split_N):
    return slice(split_N), slice(split_N, None)


def inspect_params(nbstate, split_N):
    N = nbstate.g.num_vertices()
    limit = 10 if VERBOSE else N
    low_sel = [*range(0, min(split_N, limit))]
    high_sel = [*range(max(split_N, N - limit), N)]
    for level, bstate in enumerate(nbstate.levels):
        b_low = bstate.b.fa[low_sel]
        pclabel_low = bstate.pclabel.fa[low_sel]
        bfield_low = np.array([*bstate.bfield])[low_sel]
        b_high = bstate.b.fa[high_sel]
        pclabel_high = bstate.pclabel.fa[high_sel]
        bfield_high = np.array([*bstate.bfield])[high_sel]
        log(f"L{level}")
        log(b_low)
        log(pclabel_low)
        log(bfield_low)
        log(b_high)
        log(pclabel_high)
        log(bfield_high)
        log(flush=True)
        assert {*pclabel_low} == {0}
        assert not any(x for x in bfield_high)
        if level < len(nbstate.levels) - 1:
            assert {*pclabel_high} == {1}
            assert len(bfield_low) and all(bfield_low)
        else:
            assert {*pclabel_high} == {0}
            assert not any(bfield_low)
        low_sel = bstate.b.fa[low_sel]
        high_sel = bstate.b.fa[high_sel]


def get_nbstate_with_sashimi(g, bs, pclabel, bext="max"):
    """ """
    split_N = get_half_N(g)
    g.vp["type"] = g.new_vertex_property("int", pclabel.a * 2)
    for i, b in enumerate(bs):
        bs[i] = bs[i][:split_N]
        split_N = max(bs[i]) + 1
    nbstate = gen_chained_nested_blockstate(g, bs, bext)
    return nbstate


def minimal_example_pclabel_multiflip():
    """
    https://git.skewed.de/count0/graph-tool/-/issues/746
    """
    import graph_tool.all as gt
    import numpy as np

    g = gt.collection.data["celegansneural"]
    N = g.num_vertices()

    pclabel = np.array([int(i > N / 2) for i in range(N)])
    nbstate = gt.minimize_nested_blockmodel_dl(g, state_args={"pclabel": pclabel})

    while not np.isnan(nbstate.entropy()):
        nbstate.multiflip_mcmc_sweep(beta=np.inf, niter=10)

    level_entropies = {i: nbstate.level_entropy(i) for i in range(len(nbstate.levels))}
    print(level_entropies)

    return nbstate, level_entropies


def minimal_example_pclabel_not_zero_contiguous():
    """
    https://git.skewed.de/count0/graph-tool/-/issues/747
    """
    import graph_tool.all as gt
    import numpy as np

    g = gt.collection.data["celegansneural"]
    N = g.num_vertices()

    pclabel_0_2 = np.array([2 * int(i > N / 2) for i in range(N)])  # 0s and 2s
    pclabel_1_2 = np.array([1 + int(i > N / 2) for i in range(N)])  # 1s and 2s

    for pclabel in [pclabel_0_2, pclabel_1_2]:
        # Case of blockstate constructed with NestedBlockState
        b = np.array([int(i > N / 2) for i in range(N)])
        bstate = gt.BlockState(g, b, pclabel=pclabel)
        assert np.isnan(bstate.entropy())
        # Case of blockstate returned by minimize_nested_blockmodel_dl()
        bstate = gt.minimize_blockmodel_dl(g, state_args={"pclabel": pclabel})
        assert np.isnan(bstate.entropy())


if __name__ == "__main__":
    test_all()
