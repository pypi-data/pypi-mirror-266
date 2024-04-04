# Corporalogister
#
# Author(s):
# * Ale Abdo <abdo@member.fsf.org>
#
# License:
# [GNU-GPLv3+](https://www.gnu.org/licenses/gpl-3.0.html)
#
# Project:
# <https://en.wikiversity.org/wiki/The_dynamics_and_social_organization_of_innovation_in
#  _the_field_of_oncology>
#
# Reference repository for this file:
# <https://gitlab.com/solstag/sashimi>
#
# Contributions are welcome, get in touch with the author(s).


import multiprocessing
import os
from os import path
from pathlib import Path
from collections import OrderedDict
from copy import deepcopy
import logging

import pandas

from .misc import _try_import
from .ioio import ioio
from .corpus import Corpus
from .scorology import Scorology

logger = logging.getLogger(__name__)
gensim = _try_import("gensim")


class VectorModels(Scorology, Corpus):
    """
    Word embedding model training and scoring
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        os.makedirs(self.embeddings_path, exist_ok=True)
        self.embeddings = OrderedDict()
        self.shuffled_index = None

        if self._to_load.get("models", []):
            for model in self._to_load["models"]:
                self.load_models_from_store(model)
            if len(self.loaded["data"]) == len(
                self.loaded["models"]
            ) == 1 and path.basename(self.loaded["models"][0]).startswith(
                path.splitext(path.basename(self.loaded["data"][0]))[0] + "-"
            ):
                index_name = self.loaded["models"][0] + ".index.pickle.xz"
                self.shuffled_index = ioio.load(Path(index_name))
                print("Index loaded: {}".format(index_name))
            else:
                print("Index not loaded")

    models_path = property(lambda self: path.join(self.storage_dir, "models"))

    def set_storage_dir(self, storage_dir):
        storage_dir = path.normpath(storage_dir)
        os.makedirs(self.embeddings_path, exist_ok=True)
        super().set_storage_dir(storage_dir)

    def clear_models(self):
        self.embeddings = OrderedDict()
        self.loaded["models"] = []

    def load_models_from_store(self, fdir):
        models = OrderedDict()
        for fname in sorted(
            os.listdir(fdir), key=lambda x: path.getctime(path.join(fdir, x))
        ):
            if fname.isdigit():
                fname = int(fname)
            models[fname] = ioio.load(Path(fdir, str(fname)))
            print("Models loaded: {}".format(path.join(fdir, str(fname))))
        self.update_models(models, fdir)

    def update_models(self, models, fullname):
        if not self.embeddings.keys().isdisjoint(models):
            print(
                "Warning: models were overwritten upon loading: {}".format(
                    set(self.embeddings).intersection(models)
                )
            )
        self.embeddings.update(models)
        self.loaded["models"].append(path.normpath(fullname))

    def load_models(
        self,
        name,
        balance,
        iterations,
        window,
        dimensions,
        mode="document",
        sg=False,
        hs=True,
        groupby=None,
        load=True,
        store=True,
        localvocab=False,
    ):
        if name is None:
            if len(self.loaded["data"]) == 1:
                name = path.splitext(path.basename(self.loaded["data"][0]))[0]
            else:
                raise Exception(
                    'Must provide "name" when more than one dataset is loaded'
                )
        else:
            name = path.normpath(name)
        name = (
            "-".join(
                [
                    name.replace("/", "++").replace(".", "+"),
                    str("sg" if sg else "cb"),
                    str("hs" if hs else "ns"),
                    str(mode),
                    str(iterations),
                    str(window),
                    str(dimensions),
                    str(balance),
                    str(localvocab),
                    str(groupby),
                    str(self.column),
                ]
            )
            + ".vectors"
        )
        fullname = path.join(self.embeddings_path, name)

        if load:
            try:
                return self.load_models_from_store(fullname)
            except FileNotFoundError:
                pass

        if window == "full":
            window = max(len(d) for d in list(self.itersentences("document")))
            print("Window set to {}".format(window))

        models = OrderedDict()
        # Get data shuffled to reduce training bias
        sdata = self.shuffled_data()
        # Create the base model, hs=1 and negative=0 are required by .score()
        basemodel = gensim.models.Word2Vec(
            workers=multiprocessing.cpu_count(),
            iter=iterations,
            window=window,
            size=dimensions,
            sg=sg,
            hs=hs,
            negative=0 if hs else 5,
        )
        if not localvocab:
            basemodel.build_vocab(self.itersentences(mode, sdata[self.column]))
        # Train a model for each group of documents
        grouped_data = sdata.groupby((lambda x: 0) if groupby is None else groupby)
        print("Training these models:", list(grouped_data.groups))
        for gname, gdata in self.balance_groups(grouped_data, balance):
            print("\rTraining {:<42}".format(gname), end="")
            models[gname] = deepcopy(basemodel)
            trainlist = list(self.itersentences(mode, gdata[self.column]))
            if localvocab:
                models[gname].build_vocab(trainlist)
            models[gname].train(
                trainlist, total_examples=len(trainlist), epochs=models[gname].iter
            )
            if store:
                ioio.store(models[gname], Path(fullname, f"{gname}.pickle.xz"))
                print("\nModels stored: {}".format(gname))

        if store:
            ioio.store(
                self.shuffled_index,
                Path(self.embeddings_path, f"{name}.index.pickle.xz"),
            )
            print("Model training index stored: {}".format(fullname + ".index"))

        self.update_models(models, fullname)

    def calc_scores(self, mode="document", lenfix=True):
        allscores = pandas.DataFrame()
        print("Calculating scores for: {}".format(list(self.embeddings.keys())))
        for name, model in self.embeddings.items():
            print("\rCalculating {:<42}".format(name), end="")
            # Get sentences, indexes and length of documents to correct likelihoods
            sentencelist = list(self.itersentences(mode=mode))
            indexlist = list(self.indexsentences(mode=mode))
            lenabs = pandas.Series(
                (
                    len([w for w in sentence if w in model.wv.vocab])
                    for sentence in self.itersentences(mode=mode)
                ),
                name="lenabs",
            )
            assert len(sentencelist) == len(indexlist) == len(lenabs)
            # the score (log likelihood) of each sentence for the model
            scores = pandas.Series(model.score(sentencelist, len(sentencelist)))
            if lenfix:
                if model.sg:
                    w = model.window
                    sgfix = lenabs.apply(
                        lambda l: max(0, l - 2 * w) * 2 * w
                        + min(l, 2 * w) * min(l - 1, w)
                        + sum([int(i / 2) for i in range(min(l, 2 * w))])
                    )
                    scores = scores.div(sgfix)
                else:
                    scores = scores.div(lenabs)  # abstract-size correction
            scorenans = scores[scores.isnull()]
            if not scorenans.empty:
                print("NaN found for model {}: {}".format(name, list(scorenans.index)))
            allscores[name] = scores.groupby(indexlist).mean().loc[self.data.index]
        print()
        return allscores

    def load_scores(self, mode="document"):
        print("Loading scores for {}".format(self.column))
        fname = f"scores-{self.column}.pickle.xz"
        try:
            self.scores = ioio.load(Path(self.analysis_dir, fname))
        except FileNotFoundError:
            self.scores = self.calc_scores(mode)
            ioio.store(self.scores, Path(self.analysis_dir, fname))

    def plot_wordpair_similarity_matrix(
        self, words, name="", scale="linear", upper=False, diagonal=True
    ):
        functions = OrderedDict(
            (mname, getattr(model, "similarity"))
            for mname, model in self.embeddings.items()
        )
        return self.plot_wordpair_matrix(
            words,
            functions,
            funcname="similarity",
            name=name,
            scale=scale,
            upper=upper,
            diagonal=diagonal,
        )

    def plot_wordpair_similarity_profile(self, words, name=""):
        functions = OrderedDict(
            (mname, getattr(model, "similarity"))
            for mname, model in self.embeddings.items()
        )
        return self.plot_wordpair_profile(
            words, functions, funcname="similarity", name=name
        )
