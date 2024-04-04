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

from ..util.wos_lam import WosLam


def load_wos_citations(self, user=None, password=None, pmids=None):
    if pmids is None:
        pmids = self.data.pmid
    fpath = Path(self.data_dir, f"wos_citations{self.suffix_data}")
    try:
        wos_citations = ioio.load_pandas(fpath)
    except FileNotFoundError:
        wos_citations = pandas.Series()
    new_pmids = pmids[~pmids.isin(wos_citations.index)]
    print(
        "Found {} stored, downloading {} new citation counts".format(
            pmids.size - new_pmids.size, new_pmids.size
        )
    )
    if not new_pmids.empty:
        try:
            new_citations = pandas.Series()
            wos = WosLam(user, password)
            for pmid, cited in zip(new_pmids, wos.pmid_to_timescited(new_pmids)):
                new_citations.loc[pmid] = 0 if cited is None else int(cited)
        finally:
            wos_citations = wos_citations.append(new_citations, verify_integrity=True)
            wos_citations.name = "WoS citations"
            ioio.store_pandas(wos_citations, fpath)
    self.wos_citations = wos_citations.loc[self.data.pmid]
    self.wos_citations.index = self.data.index
    print('wos_citations loaded, remember to self.norm_by_mean( , normby="year")')
