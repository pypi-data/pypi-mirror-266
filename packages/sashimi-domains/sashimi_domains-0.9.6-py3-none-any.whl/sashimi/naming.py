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

import re
from os import path
from itertools import chain

####################
# Naming utilities #
####################


class naming:
    esc, itemsep, valsep, pathsep = "~", "; ", "=", "_"
    seps = [esc, itemsep, valsep, pathsep, path.sep, path.extsep]
    _count = 0
    for x in seps:
        for y in seps:
            _count += x in y
    assert _count == len(seps)

    @classmethod
    def escape(cls, name):
        """
        Escape the path separator and argument delimiter in names.
        The escape char gets escaped if we're sure it is not already escaping.
        """
        name = re.sub(
            "(?<!["
            + cls.itemsep[0]
            + cls.pathsep
            + cls.esc
            + "])"
            + cls.esc
            + "(?!["
            + cls.esc
            + "])",
            2 * cls.esc,
            name,
        )
        name = re.sub(cls.itemsep, cls.itemsep[0] + cls.esc, name)
        name = re.sub(path.sep, cls.pathsep + cls.esc, name)
        return name

    @classmethod
    def check(cls, *args):
        forbidden = (cls.esc, path.sep, cls.itemsep, cls.valsep)
        if any(y in x for x in args for y in forbidden):
            raise ValueError

    @classmethod
    def gen(cls, base, params, suffix):
        params = [tuple(map(str, x)) for x in params]
        cls.check(*chain(*params), suffix)
        base = cls.escape(base)
        params = (map(cls.escape, x) for x in params)
        name = cls.itemsep.join(chain([base], map(cls.valsep.join, params)))
        return path.extsep.join([name, suffix.lstrip(path.extsep)])


def get_output_path(corpus, hash_dims, fname_base, fname_params, fname_suffix):
    """
    (hash_dims: list) dimensions for the sample hash, among "doc", "ter" and "ext".
    """
    if sample_hash := corpus.get_sample_hash({dim: True for dim in hash_dims}):
        fname_params = [("sample", sample_hash), *fname_params]

    target_dir = (
        corpus.chained_dir if "ext" in hash_dims is True else corpus.blocks_adir
    )
    fpath = target_dir / naming.gen(fname_base, fname_params, fname_suffix)
    return fpath
