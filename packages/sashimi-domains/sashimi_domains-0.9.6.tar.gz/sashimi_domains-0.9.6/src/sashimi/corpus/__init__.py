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

# stdlib
from collections import Counter
from copy import deepcopy
from functools import cache
from itertools import combinations, chain
import logging
from pathlib import Path
import re

# external
import numpy
import pandas
import matplotlib
from matplotlib import pyplot as plt, colors
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm

# internal
from ..config import (
    STORAGE_DIR_KEY,
    STORAGE_DIR_DEFAULT,
    ANALYSIS_DIR_KEY,
    RESOURCES_DIR_KEY,
    ANALYSIS_DIR_DEFAULT,
    RESOURCES_DIR_DEFAULT,
    get_config_path,
    load_config,
)
from ..misc import (
    clearattrs,
    makep,
    makep_fromdict,
    _fset_dir,
    property_getfuncdir,
    get_hash,
)
from ..naming import naming
from ..ioio import ioio
from . import nlp

logger = logging.getLogger(__name__)

matplotlib.use("Agg")  # TODO do we still need this?


class Corpus:
    """
    Create, save and modify core data from corpora of text and metadata.

    Parameters
    ==========
    config_path: from where to load the state of a previous run
    storage_dir: where to store data, inputs and reports (defaults to "./auto_sashimi")
    analysis_dir: where to store reports (defaults to `{storage_dir}/reports`)
    resources_dir: where to look for resources (defaults to `{storage_dir}/resources`)
    text_sources: column containing textual data (must be string or sequence of strings)
    column: column containing tokens; or column name to use when tokenizing text_sources
    col_*: column to be used as * dimension (title, time, url, id, etc)
    load_data: whether to automatically load data processed in a previous run
    """

    def __init__(
        self,
        # data locations
        config_path=None,
        storage_dir=None,
        analysis_dir=None,
        resources_dir=None,
        # data properties
        token_sources=None,
        text_sources=None,
        column=None,
        # whether to autoload previously processed data
        load_data=True,
        # kwargs admit column labels: col_title, col_time, col_url...
        **kwargs,
    ):
        assert STORAGE_DIR_KEY in locals()
        assert ANALYSIS_DIR_KEY in locals()
        assert RESOURCES_DIR_KEY in locals()
        wargs = locals()

        if config_path is not None:
            self.config_path = config_path
        to_load = load_config(get_config_path(config_path, analysis_dir, storage_dir))

        # Load properties
        prop_defaults = {
            STORAGE_DIR_KEY: STORAGE_DIR_DEFAULT,
            "suffix_data": ".json.xz",
            "column": None,
            "token_sources": [],
            "text_sources": [],
        }
        self._load_properties(wargs, to_load, prop_defaults)

        # Load directory structure
        def get_dir(dir_path, load_key, default_name):
            return Path(
                dir_path
                if dir_path is not None
                else to_load["properties"].pop(load_key)
                if load_key in to_load["properties"]
                else self.storage_dir / default_name
            )

        self.analysis_dir = get_dir(
            analysis_dir, ANALYSIS_DIR_KEY, ANALYSIS_DIR_DEFAULT
        )
        self.resources_dir = get_dir(
            resources_dir, RESOURCES_DIR_KEY, RESOURCES_DIR_DEFAULT
        )

        # Load column labels
        arg_labels = {k[4:]: v for k, v in kwargs.items() if k.startswith("col_")}
        self._column_labels = dict.fromkeys(self._column_label_keys, None)
        self._column_labels.update(to_load.pop("column_labels", {}))
        self._column_labels.update(arg_labels)

        # Load data
        self.data = pandas.DataFrame()
        self.odata = pandas.DataFrame()
        self.loaded = {"data": []}
        if load_data and (data_to_load := to_load.pop("data", False)):
            self.load_from_store(data_to_load)

        self._to_load = to_load

    def _load_properties(self, wargs, to_load, prop_defaults):
        """
        Loads properties with keys in `prop_defaults`, prefering in order:
        - values passed in wargs
        - values passed in to_load
        - values from prop_defaults
        """
        prop_to_load = to_load["properties"]
        for prop in prop_defaults:
            if wargs.get(prop, None) is not None:
                setattr(self, prop, wargs[prop])
            elif prop in prop_to_load:
                setattr(self, prop, prop_to_load.pop(prop))
            else:
                setattr(self, prop, prop_defaults[prop])

    def register_config(self, config_path=None):
        """
        Stores a file containing a json dict with the relevant settings of the class,
        for traceability and to afford reloading the class with those values.
        Stores all data load choices, at its root.
        Stores all class properties that start with "_", under "properties".
        Stores all column labels, under "column_labels".

        TODO: move loaded into a box, make it nested {data:{bstate: {chainedbstate:}}}

        """
        if config_path is None and hasattr(self, "config_path"):
            config_path = self.config_path
        config_path = get_config_path(config_path, self.analysis_dir)
        properties = dict(
            (p, getattr(self, p))
            for p in dir(type(self))
            if (type(getattr(type(self), p)) is property) and hasattr(self, "_" + p)
        )
        config = deepcopy(self._to_load)
        config.update(self.loaded)
        config.setdefault("properties", {}).update(properties)
        config.setdefault("column_labels", {}).update(self._column_labels)
        formatter_args = {
            "indent": 2,
            "sort_keys": True,
            "default": lambda x: str(x) if isinstance(x, Path) else x,
        }
        ioio.store(config, config_path, fmt="json", formatter_args=formatter_args)

    ####################
    # Class properties #
    ####################

    def _set_column(self, column, strict=True):
        if (
            not strict
            or not hasattr(self, "data")
            or self.data.empty
            or column in self.data.columns
        ):
            self.cache_clear(clear_static="ter")
            self._column = column
        else:
            raise KeyError("`column` must be a valid key in the data.")

    column = makep("column", True, _set_column, None)
    token_sources = makep("token_sources")
    text_sources = makep("text_sources")
    suffix_data = makep("suffix_data")
    _column_label_keys = {
        "affiliations",
        "authors",
        "id",
        "time",
        "title",
        "url",
        "venue",
    }
    for key in _column_label_keys:
        _prop = makep_fromdict("_column_labels", key, True, True, None)
        exec(f"col_{key} = _prop")
    del _prop

    storage_dir = makep(STORAGE_DIR_KEY, True, _fset_dir(STORAGE_DIR_KEY), None)
    analysis_dir = makep(ANALYSIS_DIR_KEY, True, _fset_dir(ANALYSIS_DIR_KEY), None)
    resources_dir = makep(RESOURCES_DIR_KEY, True, _fset_dir(RESOURCES_DIR_KEY), None)
    data_store = property_getfuncdir(lambda self: self.storage_dir / "data")

    def _gen_data_name(self, names):
        return naming.gen("|".join(names), [], self.suffix_data)

    data_name = property(
        lambda self: self._gen_data_name(self.loaded["data"])
        if self.loaded["data"]
        else None
    )
    data_dir = property_getfuncdir(lambda self: self.data_store / self.data_name)
    data_adir = property_getfuncdir(lambda self: self.analysis_dir / self.data_name)

    def get_document_ids(self, data=None):
        """
        The names attributed to document vertices in the graph representation.
        """
        if data is None:
            data = self.data
        document_ids = (
            data.index.to_series().astype(str)
            if self.col_id is None
            else data[self.col_id].astype(str)
        )
        if not document_ids.is_unique:
            raise ValueError("Document ids must be unique")
        return document_ids

    ################
    # I/O methods #
    ################

    def load_data(self, data: pandas.DataFrame, name=None):
        """
        Loads data into `self.data`.

        (data: Dataframe)
        (name: str) if None, use `data.name`
        """
        name = name or getattr(data, "name", None)
        name = [name] if isinstance(name, str) else name
        if name is None:
            raise ValueError("No `name` found for data.")
        if not self.odata.empty:
            data.index = data.index + (1 + self.odata.index.max())
        self.odata = pandas.concat([self.odata, data], verify_integrity=True)
        self.set_sample(self.data.index.union(data.index))
        self.loaded["data"].extend(name)

    def store_data(self, columns=None, overwrite=False):
        """
        Data is stored under `self.data_store` inside a directory carrying the
        same name as the file to be saved. The file name itelf is derived from
        the value of `self.loaded["data"]`.

        If you want to store it somewhere else, use `ioio.store_pandas` instead.
        """
        columns = [columns] if isinstance(columns, str) else columns
        data = self.data if columns is None else self.data[columns]
        fpath = self.data_dir / self.data_name
        if not overwrite and fpath.exists():
            raise ValueError(
                f"File {self.data_name} already exists in {self.data_dir}. "
                f"If you are sure, pass `overwrite=True`"
            )
        ioio.store_pandas(data, fpath)
        print(f"Stored: {fpath.name} in {fpath.parent}")

    def load_from_store(self, name, return_not_load=False):
        """
        Loads data `name` from store into `self.data`.

        Parameters
        ----------
        name: str
            Data name or names in store. (See `self.list_datasets()`)
        """
        name = [name] if isinstance(name, str) else name
        name_in_store = self._gen_data_name(name)
        data = ioio.load_pandas(self.data_store / name_in_store / name_in_store)
        if return_not_load:
            return data
        self.load_data(data, name=name)

    def list_datasets(self):
        return [
            fpath.name[: -len(self.suffix_data)]
            for fpath in self.data_store.iterdir()
            if ioio.uncompressed_suffix(fpath)
            == ioio.uncompressed_suffix(Path(f"_{self.suffix_data}"))
        ]

    ################
    # Data methods #
    ################

    def check_column(self, default_name="_tokens"):
        column = self.column
        if column is None:
            column = default_name
            if column in self.data:
                raise ValueError(f"Key `{column}` already present in data.")
            self.data[column] = [[] for _ in range(len(self.data))]
        else:
            if column not in self.data:
                # raise ValueError("Attribute `.column` is set but is not a key in data.")
                logger.warning(
                    f'Attribute `.column` is set to "{column}", which is not a key in data. '
                    "Processed tokens will be added to a new column."
                )
                self.data[column] = [[] for _ in range(len(self.data))]
            else:
                logger.warning(
                    f'Attribute `.column` already set to "{column}". '
                    "Processed tokens will be appended to existing ones."
                )
        return column

    def process_sources(
        self, ngrams=1, language=None, stop_words=False, tokens_to_doc=None
    ):
        """
        Normalize token data from columns in `self.token_sources` and tokenize and process textual
        data from columns in `self.text_sources`. If `self.column` is set, append the result to
        current contents, otherwise store the result in a new column and set `self.column`.

        Textual data may be either strings or an iterable yielding strings.
        Output is of the form: Document[Sentence[Token...]...]

        (ngrams) translate colocations of up to `ngrams` terms.
        (language) use language to tokenize and possibly pick stop_words
        (stop_words)
          if boolean, whether to use spacy's default stop_words for the language;
          may also be an iterable of words to use as stop_words
        (tokens_to_doc)
          function used to normalize token sources;`None` will use the default one
        """
        if not len(self.token_sources) and not len(self.text_sources):
            raise ValueError("Neither `.token_sources` nor `.text_sources` are set.")

        default_colname = "_tokens__" + ";".join(
            [",".join(self.token_sources), ",".join(self.text_sources)]
        )
        if ngrams in (2, 3):
            default_colname += "__" + "ng{}".format(ngrams)
        column = self.check_column(default_name=default_colname)

        if self.token_sources:
            self.data[column] += nlp.process_token_sources(
                self.data[self.token_sources],
                to_doc=tokens_to_doc,
            )

        if self.text_sources:
            self.data[column] += nlp.process_text_sources(
                self.data[self.text_sources],
                ngrams=ngrams,
                language=language,
                stop_words=stop_words,
            )

        # Log empty and duplicated entries
        empty = ~self.data[column].astype(bool)
        duplicated_tokens = self.data[column].loc[~empty].duplicated()
        duplicated_text = (
            self.data.loc[~empty, self.text_sources]
            .applymap(tuple, na_action="ignore")
            .duplicated()
        )
        logger.info(
            ("Created" if self.column is None else "Appended to")
            + f" `{column}` with:\n"
            f"  {empty.sum()} empty entries and\n"
            f"  {duplicated_tokens.sum()} duplicated token entries of which\n"
            f"  {duplicated_text.sum()} were already duplicated at text source.\n"
        )
        self.column = column

    def transform_corpus(self, trans=[], remove_empty=False, remove_dupes=[]):
        """
        Parameters
        ----------
        trans : a set of transformations to apply tokens. See below.
        remove_epty: remove rows with empty (nan) values in `self.column`
        remove_dupes: keep only the first row with duplicate values for any of the given columns

        Transformations
        --------------
        New columns will be named in the form: `{self.column}_{transform}`

        Available transforms are:
        'set' - terms appear once per document
        'red' - vocabulary is reduced to 20% highest graded terms
        'redset' - apply red to vocabulary and set to document
        'propo' - each document is cut to its 20% highest graded terms
        'proposet' - apply set to document then propo

        Example
        -------
        corpus.transform_corpus(trans=['set'], remove_dupes=[corpus.column + '_set'])

        Returns
        -------
        A copy of the data with added columns and removed rows
        """
        data = self.data.copy()
        trans = {trans} if isinstance(trans, str) else {*trans}
        remove_dupes = {*remove_dupes}
        print("Transforming corpus into {}".format(trans))

        def trans_col_name(x):
            "Returns the column name used for a given transformation"
            return "_".join([self.column, x])

        def get_propo(d, setit=False):
            # wfreq[w]>=5 matches word2vec default vocab cut
            s = pandas.Series(w for s in d for w in s if dfreq[w] >= 5)  # w or d ?
            if setit:
                s = s[~s.duplicated()]
            # s = s.sample(frac=1) # if comntd: deterministic but prefer early
            idx = s.apply(lambda x: -grade[x]).sort_values().index
            idx = idx[: int(len(s) / 5)]
            s = s.loc[idx].sort_index()
            return (tuple(s),)

        # Calculate accessory quantities
        if trans.intersection({"red", "redset", "propo", "proposet"}):
            grade, wfreq, dfreq = self.get_graded_vocab(self.column)
        if trans.intersection({"red", "redset"}):
            vocab = filter(lambda x: dfreq[x] > (len(data) / 1000), grade.keys())
            vocab = sorted(vocab, key=lambda x: grade[x])
            mingrade = grade[vocab[-int(len(vocab) / 5)]]
            vocab = set(vocab[-int(len(vocab) / 5) :])
            print(
                "Reduced {} terms with dfreq {} and grade {} retaining {} terms".format(
                    len(grade.keys()), len(data) / 1000, mingrade, len(vocab)
                )
            )

        # Apply transformations
        if (tran := "set") in trans:
            data[trans_col_name(tran)] = [
                (tuple(sorted(set(w for s in d for w in s))),)
                for d in data[self.column]
            ]
        if (tran := "red") in trans:
            data[trans_col_name(tran)] = [
                tuple(tuple(w for w in s if w in vocab) for s in d)
                for d in data[self.column]
            ]
        if (tran := "redset") in trans:
            data[trans_col_name(tran)] = [
                (tuple(sorted(set(w for s in d for w in s if w in vocab))),)
                for d in data[self.column]
            ]
        if (tran := "propo") in trans:
            data[trans_col_name(tran)] = data[self.column].transform(get_propo)
        if (tran := "proposet") in trans:
            data[trans_col_name(tran)] = data[self.column].transform(
                get_propo, setit=True
            )

        # Log duplicate transform entries
        for tran in trans:
            col = trans_col_name(tran)
            print(f"Duplicated in `{col}`: {data[col].duplicated().sum()}")

        # Remove empty or duplicated
        to_remove = {}
        if remove_empty:
            to_remove[None] = ~data[self.column].astype(bool)
        if remove_dupes_text := remove_dupes.intersection(self.text_sources):
            to_remove[remove_dupes_text] = (
                data[self.text_sources].applymap(tuple).duplicated()
            )
        for col in remove_dupes.difference(self.text_sources):
            to_remove[col] = data[col].duplicated()
        if to_remove:
            print(
                "Empty (None) or duplicated to be removed:",
                *[[k, v.sum()] for k, v in to_remove.items()],
            )
            b_remove = numpy.add.reduce(to_remove).astype(bool)
            data = data[~b_remove]
            print(f"Eliminated {b_remove.sum()} entries")

        return data

    def get_data(self, fields=None, search={}):
        """
        fields: list of self.data fields to return
        search: dict of 'field'->'regex' to filter data
        """
        if not search:
            return self.data.loc[:, fields] if fields else self.data

        def picker(s):
            if type(search[s.name]) is str:
                return (
                    s.astype(str).apply(re.compile(search[s.name]).search).astype(bool)
                )
            elif type(search[s.name]) in (int, float):
                return s == search[s.name]
            else:
                return s.apply(search[s.name]).astype(bool)

        picks = self.data.loc[:, search.keys()].apply(picker).all(axis=1)
        return self.data.loc[picks, fields] if fields else self.data.loc[picks]

    def filter_terms(self, func, column=None):
        if column is None:
            column = self.column
        return self.data[column].transform(
            lambda d: tuple(tuple(w for w in s if func(w)) for s in d)
        )

    def find_terms(self, terms=[], pattern=r"", column=None):
        if column is None:
            column = self.column
        if not terms and not pattern:
            raise ValueError("Must provide `terms` or `pattern`")
        patterns = []
        if terms:
            patterns.append(r"^(?:" + r"|".join(terms) + r")$")
        if pattern:
            patterns.append(pattern)
        rx = re.compile(r"|".join(patterns))

        def func(doc):
            return tuple(w for s in doc for w in s if rx.search(w))

        return self.data[column].map(func)

    def get_col_type(self, column):
        if self.data[column].dtype.kind in "Mm":
            return "string"
        if self.data[column].dtype.kind in "ifu":
            return "int"

    def clear_data(self):
        self.cache_clear(clear_static=True)
        self.data, self.odata = pandas.DataFrame(), pandas.DataFrame()
        self.loaded["data"] = []

    def cache_clear(self, clear_static=False):
        if clear_static and clear_static != "ext":
            clearattrs(self, ["ter_documents"])
        if clear_static and clear_static != "ter":
            clearattrs(self, ["ext_documents"])
        for m in dir(type(self)):
            m = getattr(type(self), m)
            if hasattr(m, "cache_clear"):
                m.cache_clear()

    ###################
    # Data derivation #
    ###################

    def get_doc_terms(self):
        return self.data[self.column].map(lambda d: [w for s in d for w in s])

    def get_vocab(self):
        if hasattr(self, "ter_documents"):
            return set(self.ter_documents.keys())
        else:
            return set(chain(*self.get_doc_terms()))

    def get_doc_exts(self):
        match_keys, get_matches = self.make_matcher()
        d = {}
        for key in match_keys:
            for match in get_matches(key):
                d.setdefault(match, []).append(key)
        return self.data.index.to_series().map(lambda x: d.get(x, []))

    def load_ter_documents(self):
        self.load_x_documents("ter")

    def load_ext_documents(self):
        self.load_x_documents("ext")

    def load_x_documents(self, btype):
        docs = self.get_doc_terms() if btype == "ter" else self.get_doc_exts()
        if btype == "ter":
            d = dict((key, Counter()) for key in self.get_vocab())
        elif btype == "ext":
            match_keys, get_matches = self.make_matcher()
            d = dict((key, Counter()) for key in match_keys)
        for i_doc, doc in tqdm(docs.items(), total=len(docs), desc="Doc"):
            for element in doc:
                d[element][i_doc] += 1
        setattr(self, f"{btype}_documents", d)

    def make_matcher(self, extend=None, multi=False, na_action="ignore"):
        """
        (extend) None | {"prop": [str], "matcher": [None|str]}
            If None, uses `corpus.extended` otherwise `corpus.graph_extend`.
            `prop` is the column whose values will be used to form new nodes.
            If all values are lists, they get exploded before matching.
            `matcher` can be:
            - None: edges link documents to items found in `prop`.
            - str: file in resources dir containing a dictionary mapping node names to
            regular expressions to be applied at `prop` to connect keys to documents.

        (multi) `get_matches()` keeps duplicates when an exploded value matches more than once

        :match_keys: nodes of the extended dimension
        :get_matches: given a node, returns the corresponding documents

        Usage:
        match_keys, get_matches = self.make_matcher()

        TODO: move multi and na_action into graph_extend?
        """
        extend = extend or self.extended or self.graph_extend
        prop = self.data[extend["prop"]]
        if prop.dropna().map(lambda x: isinstance(x, list)).all():
            prop = prop.explode()
        if na_action == "ignore":
            prop = prop.dropna()  # dropna after explode() as []→nan
        prop = prop.astype(str)

        def get_matches_no_matcher(key):
            return prop[prop == key].index.unique()

        def get_matches_no_matcher_multi(key):
            return prop[prop == key].index

        def get_matches_matcher(key):
            return prop.loc[prop.str.contains(matcher[key], na=False)].index.unique()

        def get_matches_matcher_multi(key):
            return prop.loc[prop.str.contains(matcher[key], na=False)].index

        if matcher_name := extend["matcher"] is None:
            match_keys = prop.unique()
            get_matches = (
                get_matches_no_matcher_multi if multi else get_matches_no_matcher
            )
        else:
            matcher = ioio.load(self.resources_dir / matcher_name)
            match_keys = matcher.keys()
            get_matches = get_matches_matcher_multi if multi else get_matches_matcher

        return match_keys, get_matches

    def serify(self, axis):
        return self.data[axis] if type(axis) is str else axis

    def samplify(self, sample, source):
        if sample is None:
            index = source.index
        elif isinstance(sample, int):
            index = source.sample(sample).index
        elif isinstance(sample, pandas.Series) and sample.dtype == "bool":
            index = source.loc[sample.index].loc[sample].index
        elif isinstance(sample, (pandas.Series, pandas.DataFrame)):
            index = source.index.intersection(sample.index)
        elif len(sample) == len(source) and all(type(x) is bool for x in sample):
            index = source.loc[sample].index
        else:
            index = source.index.intersection(sample)
        return index

    def set_sample(self, sample, keep=False):
        if keep:
            new_data = self.data.loc[self.samplify(sample, self.data)]
        else:
            new_data = self.odata.loc[self.samplify(sample, self.odata)]
        if not self.data.index.equals(new_data.index):
            self.cache_clear()
        self.data = new_data.copy()

    def get_sample_hash(self, *, doc, ter=False, ext=False):
        hashes = {}
        if doc and not self.data.index.equals(self.odata.index):
            hashes["D"] = get_hash(self.data.index)
        if ter and hasattr(self, "_orig_tblocks"):
            if not self.tblocks.index.equals(self._orig_tblocks.index):
                hashes["T"] = get_hash(self.tblocks.index)
        if ext and hasattr(self, "_orig_eblocks"):
            if not self.eblocks.index.equals(self._orig_eblocks.index):
                hashes["E"] = get_hash(self.eblocks.index)
        return "".join(x + y for x, y in hashes.items())

    @cache
    def get_graded_vocab_cached(self, column, sampled):
        return self.get_graded_vocab(column, sampled)

    def get_graded_vocab(self, column=None, sampled=True):
        """
        Ranks a vocabulary by how concentrated a term appears, given its
        overall frequency, regarding the actual and expected number of
        documents it appears in.
        (column) label of a Series[Document[Sentence[Terms]]]
        """
        data = self.data if sampled else self.odata
        col_data = data[self.column if column is None else column]
        ndocs = len(col_data)
        docs = col_data.apply(lambda d: [w for s in d for w in s])
        vocab = self.get_vocab()
        wfreq = Counter(w for d in docs for w in d)
        dfreq = Counter(w for d in docs for w in set(d))

        def expected_spread(w):
            return ndocs * (1 - ((ndocs - 1) / ndocs) ** wfreq[w])

        def concentration(w):
            return expected_spread(w) / dfreq[w]

        graded_vocab = dict((w, concentration(w)) for w in vocab)
        return graded_vocab, wfreq, dfreq

    #####################
    # Data manipulation #
    #####################

    def itersentences(self, mode, docs=None):
        if docs is None:
            docs = self.data[self.column]
        if mode == "document":
            return ([w for s in d for w in s] for d in docs)
        elif mode == "sentences":
            return (s for d in docs for s in d)

    def indexsentences(self, mode, docs=None):
        if docs is None:
            docs = self.data[self.column]
        if mode == "document":
            return docs.index
        elif mode == "sentences":
            return (i for i, d in docs.iteritems() for s in d)

    def shuffled_data(self, data=None, reshuffle=False):
        if data is None:
            data = self.data
        if (self.shuffled_index is None) or reshuffle:
            self.shuffled_index = list(self.data.index)
            numpy.random.shuffle(self.shuffled_index)
        return data.loc[self.shuffled_index]

    def balance_groups(self, grouped_data, balance):
        """
        Balance the size of groups of documents according to a chosen method
        """
        if balance == "nobalance":
            for g, ga in grouped_data:
                yield g, ga
        elif balance == "randomfill":
            # Fill them up to match the largest group
            maxsize = max(grouped_data.size())
            for group, gdata in grouped_data:
                size = len(gdata)
                factor = int(maxsize / size)
                rest = maxsize - size * factor
                yield group, pandas.concat(
                    [gdata for i in range(factor)] + [gdata[:rest]]
                )
        elif balance == "randomsample":
            # Cut them to match the smallest group
            minsize = min(grouped_data.size())
            for group, gdata in grouped_data:
                yield group, gdata[:minsize]
        elif balance == "demisample":
            # Cut them to match half the smallest group
            deminsize = int(min(grouped_data.size()) / 2)
            for group, gdata in grouped_data:
                yield group, gdata[:deminsize]
        elif balance == "antidemisample":
            # The complement of demiample
            minsize = min(grouped_data.size())
            deminsize = int(min(grouped_data.size()) / 2)
            for group, gdata in grouped_data:
                yield group, gdata[deminsize:minsize]
        else:
            raise Exception("Balance method not found: " + balance)

    def balanced_data(self, groupby, balance):
        return pandas.concat(
            gdata
            for group, gdata in self.balance_groups(
                self.shuffled_data().groupby(groupby), balance
            )
        ).sort_index()

    ############
    # Analysis #
    ############

    def norm_by_mean(self, s, normby):
        normby = self.serify(normby)
        s_avgby = s.groupby(normby).mean()
        return s / normby.apply(lambda x: s_avgby.loc[x])

    def plot_hist(self, s, by=None, scale="linear", bins=10):
        s, by = map(self.serify, (s, by))
        plt.figure(figsize=(17, 10))
        if bins == "cat":
            bins = len(s.unique())
        s.hist(by=by, bins=bins)
        plt.title(
            "{} histogram".format(s.name.capitalize())
            + ("by {}".fomat(by.name) if by is not None else "")
        )
        plt.savefig(
            self.data_adir
            / "hist-{}{}.pdf".format(s.name, ("-by-{}" if by is not None else ""))
        )
        plt.close()

    def plot_cor_s(self, xaxis, yaxis, scale=("linear", "linear"), xlim=None, ax=None):
        xscale, yscale = (scale, scale) if type(scale) == str else scale
        if ax is None:
            ax = plt
            ax.figure(figsize=(17, 10))
            ax.title("{} X {}".format(xaxis.name, yaxis.name))
        ax.scatter(xaxis, yaxis)
        if xscale == "log":
            bins = (
                numpy.logspace(
                    numpy.log10(xaxis.min() + 1), numpy.log10(xaxis.max() + 1.2)
                )
                - 1.1
            )
            xaxis = pandas.cut(xaxis, bins, labels=bins[1:])
            if ax == plt:
                ax.xscale(xscale)
            else:
                ax.set_xscale(xscale)
        yavg = yaxis.groupby(xaxis).mean()
        ax.plot(numpy.array(yavg.index), yavg, color="red", linewidth=2)
        # ax.axhline()
        if ax == plt:
            ax.yscale(yscale)
        else:
            ax.set_yscale(yscale)
        if xlim:
            ax.xlim(**xlim)
        if ax == plt:
            ax.savefig(
                self.data_adir
                / "cor-{}-x-{}-{}.pdf".format(xaxis.name, yaxis.name, "".join(scale))
            )
            input("Press enter to close the plot.")
            ax.close()

    def plot_cor(
        self, xaxis, yaxis, groupby=None, scale=("linear", "linear"), xlim=None
    ):
        xaxis, yaxis, groupby = map(self.serify, (xaxis, yaxis, groupby))
        if groupby is None:
            return self.plot_cor_s(xaxis, yaxis, scale, xlim)
        grouped = xaxis.groupby(groupby)
        for i, (name, group) in enumerate(grouped):
            ax = plt.subplot(int(len(grouped) / 2) + 1, 2, i + 1)
            ax.set_title(name)
            self.plot_cor_s(group, yaxis.loc[group.index], scale, xlim, ax)
        ax.figure.set_size_inches(17.0, len(grouped) * 1.7)
        ax.figure.tight_layout()
        ax.figure.suptitle("{} X {}".format(xaxis.name, yaxis.name), fontsize=17)
        plt.subplots_adjust(top=0.95)
        plt.savefig(
            self.data_adir
            / "cor-{}-{}-x-{}-{}.pdf".format(
                xaxis.name, groupby.name, yaxis.name, "".join(scale)
            )
        )
        plt.close()

    def print_cor(self, xaxis, yaxis, groupby=None):
        from scipy.stats import pearsonr, spearmanr

        xaxis, yaxis, groupby = map(self.serify, (xaxis, yaxis, groupby))
        grouped = xaxis.groupby(groupby) if groupby else (xaxis.name, xaxis)
        for name, group in grouped:
            print(
                "==Pandas==\npearson: {}\nspearman: {}\n".format(
                    group.corr(yaxis, method="pearson"), pearsonr(group, yaxis)
                )
            )
            print(
                "==Scipy==\npearson: {}\nspearman: {}\n".format(
                    group.corr(yaxis, method="spearman"), spearmanr(group, yaxis)
                )
            )

    def plot_term_frequency_profile(self, terms, groupby=None, level="term"):
        """* level: can be either term or doc"""
        ax = plt.axes()
        docs = self.get_doc_terms()
        what = (
            (lambda x, y: int(y in x)) if level == "doc" else (lambda x, y: x.count(y))
        )
        for term in terms:
            ax = (
                docs.apply(what, args=(term,))
                .groupby(self.data[groupby])
                .sum()
                .plot(ax=ax, label=term)
            )
        plt.legend()
        input("Tell me when to stop!")
        plt.close()

    def plot_termpair_matrix(
        self,
        terms,
        functions,
        funcname,
        name="",
        scale="linear",
        upper=False,
        diagonal=True,
    ):
        fname = self.data_adir / "{}-matrix{}-{}.pdf".format(
            funcname, (("-" + name) if name else ""), scale
        )
        with PdfPages(fname) as pdf:
            for key, function in functions.items():
                sim = pandas.DataFrame(columns=terms, index=terms, dtype=numpy.float64)
                for i in sim.index:
                    for j in sim.columns:
                        if not diagonal and sim.index.get_loc(i) == sim.columns.get_loc(
                            j
                        ):
                            sim.loc[i, j] = numpy.nan
                        elif upper and sim.index.get_loc(i) < sim.columns.get_loc(j):
                            sim.loc[i, j] = numpy.nan
                        else:
                            sim.loc[i, j] = function(i, j)
                plt.figure(figsize=(10, 7))
                norm = colors.LogNorm() if scale == "log" else colors.Normalize()
                plt.pcolormesh(
                    numpy.ma.masked_array(sim.as_matrix(), sim.isnull()),
                    cmap="OrRd",
                    norm=norm,
                )  # , vmin=0, vmax=1)
                plt.yticks(numpy.arange(0.5, len(sim.index), 1), sim.index)
                plt.xticks(
                    numpy.arange(0.5, len(sim.columns), 1), sim.columns, rotation=45
                )
                plt.xlabel("destination")
                plt.ylabel("source")
                plt.xlim(xmax=len(sim.columns))
                plt.ylim(ymax=len(sim.index))
                plt.colorbar()
                plt.title("{} {}".format(funcname, key))
                pdf.savefig()
                plt.close()

    def plot_termpair_profile(self, terms, functions, funcname, name=""):
        fname = (
            self.data_adir / funcname
            + "-prof"
            + (("-" + name) if name else "")
            + ".pdf"
        )
        with PdfPages(fname) as pdf:
            for w1, w2 in combinations(terms, 2):
                plt.plot(
                    list(functions),
                    [function(w1, w2) for function in functions.values()],
                )
                plt.title("{}( {}, {} )".format(funcname, w1, w2))
                pdf.savefig()
                plt.close()
