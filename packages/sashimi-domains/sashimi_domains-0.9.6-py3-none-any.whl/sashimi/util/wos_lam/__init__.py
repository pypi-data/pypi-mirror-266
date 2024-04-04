# WosLam, a tiny library for the WOS Links Article Match API
#
# Author(s):
# * Ale Abdo <abdo@member.fsf.org>
#
# License:
# [GNU-GPLv3+](https://www.gnu.org/licenses/gpl-3.0.html)
#
# Reference repository for this file:
# <https://gitlab.com/solstag/sashimi>
#
# Contributions are welcome, get in touch with the author(s).

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from lxml import etree
import pkg_resources


class WosLam:
    """
    Access WebOfScience Links Article Match API.
    Appropriate WOS credentials must be provided during instantiation.
    See the API documentation for details on fields and queries:
    <http://ipscience-help.thomsonreuters.com/LAMRService/WebServiceOperationsGroup/requestAPIWoS/descriptionXMLrequest.html>
    """

    def __init__(self, user, password):
        self.apiurl = "https://ws.isiknowledge.com/cps/xrpc"
        self.whatfields = (
            "timesCited",
            "ut",
            "doi",
            "pmid",
            "sourceURL",
            "citingArticlesURL",
            "relatedRecordsURL",
        )
        self.lookupfields = {"doi", "ut", "pmid", "isbn"}
        tpl_path = pkg_resources.resource_filename("sashimi", "wos_api_request.tpl")
        with open(tpl_path) as tplfile:
            self.reqtpl = tplfile.read().format(user=user, password=password)

    def get(self, fields, queries):
        """
        Gets information from WOS as dictionaries.
        fields - list of strings
        queries - list of dictionaries of type 'id'->'value'
        Returns:
        iterator over dictionaries containing the results for each query
        """
        for i in range(0, len(queries), 50):
            part = queries[i : i + 50]
            for r in self.get_50(fields, part):
                yield r
            print("Got {} of {}".format(i + 50, len(queries)))

    def get_50(self, fields, queries):
        if len(queries) > 50:
            raise Exception("Queries are limited to 50 elements")
        reply = self.get_raw(fields, queries)
        root = etree.fromstring(reply)
        xns = {"x": "http://www.isinet.com/xrpc42"}
        if root.xpath("//x:error", namespaces=xns):
            raise Exception("Request returned errors, likely bad credentials")
        qxpath = '//x:map[@name="cite_{}"]'
        fxpath = '*/*[@name="{}"]/text()'
        for count, q in enumerate(queries):
            elm = root.xpath(qxpath.format(count), namespaces=xns)[0]
            r = dict()
            for name in fields:
                try:
                    r[name] = elm.xpath(fxpath.format(name))[0]
                except IndexError as e:
                    print("Not found {} for {}".format(fields, q))
                    r[name] = None
            yield r

    def get_raw(self, fields, queries):
        what = self.get_what(fields)
        lookup = self.get_lookup(queries)
        request = self.get_request(what, lookup)
        with urlopen(request) as f:
            return f.read()

    def get_request(self, what, lookup):
        return Request(
            self.apiurl, self.reqtpl.format(what=what, lookup=lookup).encode()
        )

    def get_what(self, fields):
        what = []
        for f in fields:
            if f in self.whatfields:
                what.append("<val>{}</val>".format(f))
            else:
                raise Exception("Invalid field: {}".format(f))
        return "\n".join(what)

    def get_lookup(self, queries):
        lookup = []
        for count, q in enumerate(queries):
            if q and self.lookupfields.issuperset(q):
                lookup.append('<map name="cite_{}">'.format(count))
                for k in q:
                    lookup.append('<val name="{}">{}</val>'.format(k, q[k]))
                lookup.append("</map>")
            else:
                raise Exception("Invalid field in: {}".format(list(q.keys())))
        return "\n".join(lookup)

    # Convenience functions

    def convert(self, c_from, c_to, items):
        for r in self.get([c_to], [{c_from: v} for v in items]):
            yield r[c_to]

    def pmid_to_timescited(self, pmids):
        return self.convert("pmid", "timesCited", pmids)

    def doi_to_timescited(self, dois):
        return self.convert("doi", "timesCited", dois)
