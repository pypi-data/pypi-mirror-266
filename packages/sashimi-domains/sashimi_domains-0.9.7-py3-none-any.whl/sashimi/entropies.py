import itertools
import math


def mean(x):
    """
    This is more efficient than both math.mean() and np.mean()
    """
    return sum(x) / len(x)


#############
# entropies #
#############


def pt_entropy(p, q=None):
    """pointwise [relative] entropy"""
    if q is None:
        return -math.log2(p)
    if q > 0 and p == 0:
        return -math.inf
    return math.log2(p / q)


def ept_entropy(p, q=None, pe=None):
    """expectation-weighted pointwise [relative] entropy"""
    pe = p if pe is None else pe
    return 0.0 if pe == 0 else pe * pt_entropy(p, q)


def entropy(p, q=None, pe=None):
    """total expectation-weighted [relative] entropy"""
    pe = p if pe is None else pe
    q = [None] * len(p) if q is None else q
    return sum(ept_entropy(p, q, pe) for p, q, pe in zip(p, q, pe))


def hier_ept_entropy(ps, qs=None, pes=None):
    """expectation-weighted mean of pointwise relative entropies"""
    if pes is None:
        ps, pes = itertools.tee(ps)
    return mean(
        [0.0 if pe == 0 else pe * pt_entropy(p, q) for p, q, pe in zip(ps, qs, pes)]
    )


def make_nested_specificity(counts, up_counts):
    counts = itertools.repeat(counts) if isinstance(counts[0], dict) else counts

    def nested_specificity(x):
        return hier_ept_entropy(
            (c[x] / ct for c, ct in counts),
            [up_c[x] / up_ct for up_c, up_ct in up_counts]
            or [1 / len(next(iter(counts))[0])],
        )

    return nested_specificity


def make_nested_commonality(sub_counts, up_counts):
    def nested_commonality(x):
        pe = mean([sc_tot and sc[x] / sc_tot for sc, sc_tot in sub_counts])
        return mean(
            [
                hier_ept_entropy(
                    itertools.repeat(sc_tot and sc[x] / sc_tot),
                    [uc[x] / uc_tot for uc, uc_tot in up_counts] or [1 / len(sc)],
                    pes=itertools.repeat(pe),
                )
                for sc, sc_tot in sub_counts
            ]
        )

    return nested_commonality
