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

import json
import os
from os import path

from lxml import etree, html
import pandas

from .. import ioio


def parse_data(source, parser, parser_args={}, name=None):
    """
    Parameters
    ----------
    source: str
        File to be parsed.
    parser: str
        Source format: any of `get_{parser}`.
    parser_args: dict
        Some parsers can take arguments
    name: str
        Register under name instead of source's name
    """
    name = name or getattr(source, "name", str(source))
    if parser in parsers:
        data = parsers[parser](source, **parser_args)
    else:
        raise ValueError(f"Unknown parser: {parser}")
    return data


#################################
# Parsers for different formats #
#################################


def get_pickle(fpath):
    return pandas.DataFrame(ioio.load(fpath, fmt="pickle"))


def get_csv(fpath, read_csv_args={}):
    df = pandas.read_csv(fpath, **read_csv_args)
    return df


def get_csvdir(csv_dir, read_csv_args={}):
    fnames = [name for name in os.listdir(csv_dir) if name.endswith(".csv")]
    df = pandas.read_csv(path.join(csv_dir, fnames.pop(0)), **read_csv_args)
    for name in fnames:
        df = df.append(
            pandas.read_csv(path.join(csv_dir, name), low_memory=False),
            ignore_index=True,
            sort=False,
            **read_csv_args,
        )
    return df


def get_esmo(esmo_path):
    data = list()
    years = sorted(int(i) for i in os.listdir(esmo_path))
    # get converted PDF files
    for year in years:
        year_path = path.join(esmo_path, str(year), "xml")
        for sec in os.listdir(year_path):
            if sec.endswith(".json"):
                sec_path = path.join(year_path, sec)
                with open(sec_path) as sec_file:
                    content = json.load(sec_file)
                for i, item in enumerate(content):
                    abstext = " ".join(line["text"] for line in item["abstract"])
                    if not item["abstract"] or len(abstext) < 10:
                        print("Defective abstract {} at {}".format(i, sec_path))
                        continue
                    if item["separator"] is not None:
                        data.append([abstext, year])
    # get converted HTML files
    for year in years:
        year_path = path.join(esmo_path, str(year), "content")
        for sec in os.listdir(year_path):
            if sec.endswith(".json"):
                sec_path = path.join(year_path, sec)
                with open(sec_path) as sec_file:
                    content = json.load(sec_file)
                for a in content["abstracts"]:
                    htext = html.fromstring(a["text"])
                    htext.find("h2").getparent().remove(htext.find("h2"))
                    abstract = ". ".join(
                        [
                            a["title"],
                            " ".join(a["authors"].keys()),
                            " ".join(sum(a["authors"].values(), [])),
                            htext.text_content(),
                        ]
                    )
                    data.append([abstract, year])
    return pandas.DataFrame(data, columns=["original", "year"])


def get_getpapers(getpapers_path):
    data = list()
    names = [
        n
        for n in os.listdir(getpapers_path)
        if path.isdir(path.join(getpapers_path, n))
    ]
    noabstract = []
    for name in names:
        with open(path.join(getpapers_path, name, "eupmc_result.json")) as f:
            content = json.load(f)
        try:
            year = int(content["journalInfo"][0]["yearOfPublication"][0])
            abstract = content["abstractText"][0]
            pmid = content["id"][0]
            citations = int(content["citedByCount"][0])
            title = content["title"][0]
            if (
                "authorList" in content
                and "author" in content["authorList"][0]
                and all("fullName" in x for x in content["authorList"][0]["author"])
            ):
                authors = [x["fullName"][0] for x in content["authorList"][0]["author"]]
            else:
                authors = []
            if "affiliation" in content:
                affiliations = content["affiliation"]
            else:
                affiliations = []
            if any(
                map(
                    lambda x: len(x) != 1,
                    (
                        content["abstractText"],
                        content["id"],
                        content["citedByCount"],
                        content["title"],
                        content["journalInfo"][0]["yearOfPublication"],
                    ),
                )
            ):
                raise Exception("Non-unique item!")
            if not len(abstract):
                raise Exception("Empty abstract!")
            data.append([abstract, year, pmid, citations, title, authors, affiliations])
        except KeyError:
            noabstract.append(name)
    if noabstract:
        print(
            "Warning: In <" + getpapers_path + '> missing "abstractText":',
            ", ".join(noabstract),
        )
    df = pandas.DataFrame(
        data,
        columns=[
            "original",
            "year",
            "pmid",
            "epmc_citations",
            "title",
            "authors",
            "affiliations",
        ],
    )
    pmid_sorted_idx = df.pmid.astype(int).sort_values().index
    df = df.loc[pmid_sorted_idx].sort_values("year", kind="mergesort")
    return df


def get_pubmed(pubmed_file):
    data = list()
    ctx = etree.iterparse(pubmed_file, tag="PubmedArticle")
    article = "MedlineCitation/Article/"
    print()
    for a, e in ctx:
        pmid = str(e.xpath("MedlineCitation/PMID/text()")[0])
        print("\rExtracting pmid: {:17}".format(pmid), end="")

        year_j = e.xpath(article + "Journal/JournalIssue/PubDate/Year/text()")
        year_m = e.xpath(article + "Journal/JournalIssue/PubDate/MedlineDate/text()")
        year_a = e.xpath(article + "ArticleDate/Year/text()")
        assert len(year_j) < 2 and len(year_m) < 2 and len(year_a) < 2
        year_j, year_m, year_a = map("".join, (year_j, year_m, year_a))
        years = [int(y) for y in (year_j, year_a) if y != ""]
        if year_m != "":
            years.append(int(year_m.split()[0].split("-")[-1]))
        year = min(years)

        abstract = e.xpath(article + "Abstract/AbstractText/text()")
        if not abstract:
            continue
        abstract = "".join(abstract)

        title = str(e.xpath(article + "ArticleTitle/text()")[0])

        authors = list()
        affiliations = list()
        for ee in e.xpath(article + "AuthorList/Author"):
            if ee.xpath("CollectiveName"):
                continue
            authors.append(
                " ".join(ee.xpath("ForeName/text()") + ee.xpath("LastName/text()"))
            )
            affiliations.extend(
                map(str, ee.xpath("AffiliationInfo/Affiliation/text()"))
            )

        language = list(map(str, e.xpath(article + "Language/text()")))

        journal = e.xpath(article + "Journal/ISOAbbreviation/text()")
        if journal:
            journal = str(journal[0])
        else:
            journal = str(e.xpath(article + "Journal/Title/text()")[0])

        data.append(
            [abstract, year, pmid, title, authors, affiliations, language, journal]
        )

        e.clear()  # clean up children
        while e.getprevious() is not None:
            del e.getparent()[0]  # clean up preceding
    print()
    df = pandas.DataFrame(
        data,
        columns=[
            "original",
            "year",
            "pmid",
            "title",
            "authors",
            "affiliations",
            "language",
            "journal",
        ],
    )
    pmid_sorted_idx = df.pmid.astype(int).sort_values().index
    df = df.loc[pmid_sorted_idx].sort_values("year", kind="mergesort")
    return df


def get_getpapersdir(getpapers_store):
    fpaths = [
        path.join(getpapers_store, name)
        for name in os.listdir(getpapers_store)
        if path.isdir(path.join(getpapers_store, name))
    ]
    return pandas.concat((get_getpapers(fpath) for fpath in fpaths), ignore_index=True)


parsers = {k[4:]: v for k, v in locals().items() if k.startswith("get_")}
