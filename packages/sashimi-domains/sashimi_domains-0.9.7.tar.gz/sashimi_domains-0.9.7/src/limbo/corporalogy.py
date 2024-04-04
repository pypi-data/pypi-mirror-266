# coding: utf-8

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

########################
# Document-Term Matrix #
########################
# Seemed like a good idea once upon a time, but turns out to be useless.


def load_dtm(self, store=False, from_file=True):
    """
    Calculates the boolean Document X Term matrix.

    See also: load_dtm_conc (same function but concurrent)
    """
    fname = naming.gen("document_term_matrix", {"column": self.column}, ".pickle")
    if from_file:
        try:
            self.dtm = ioio.load(fname, self.data_dir)
            return
        except FileNotFoundError:
            pass

    index = self.data.index
    vocab = list(self.get_vocab())
    data, rows, cols = [], [], []
    docs = self.data[self.column].apply(lambda x: set(sum(x, ())))  # bool:set

    from progress.bar import Bar

    Bar.etam = property(lambda self: self.eta // 60)
    bar = Bar(
        "Processing",
        max=len(index),
        suffix="%(percent).1f%% - %(elapsed)ds - %(etam)dm " + "(%(index)d/%(max)d)",
    )

    for row, ind in enumerate(index):
        doc = docs[ind]
        for col, term in enumerate(vocab):
            if term in doc:  # bool:in
                data.append(True)  # bool:in
                rows.append(row)
                cols.append(col)
        bar.next()
    bar.finish()

    print("Instantiating document term matrix")
    matrix = coo_matrix((data, (rows, cols)), dtype=bool)
    dtm = pandas.SparseDataFrame(
        data=matrix, index=index, columns=vocab, default_fill_value=False
    )
    self.dtm = dtm
    if store:
        print("Storing document term matrix")
        ioio.store(self.dtm, fname, self.data_dir)


def load_dtm_conc(self, store=False, from_file=True):
    """
    Calculates the boolean Document X Term matrix using concurrent processes.
    """
    fname = naming.gen("document_term_matrix", {"column": self.column}, ".pickle")
    if from_file:
        try:
            self.dtm = ioio.load(fname, self.data_dir)
            print("Loaded from file")
            return
        except FileNotFoundError:
            pass

    from multiprocessing.managers import BaseManager
    from concurrent.futures import ProcessPoolExecutor

    index = self.data.index
    vocab = list(self.get_vocab())
    docs = self.data[self.column].apply(lambda x: set(sum(x, ())))  # bool:set

    class MyManager(BaseManager):
        pass

    MyManager.register("tqdm", tqdm)
    with MyManager() as manager:
        bar = manager.tqdm(total=len(index))
        with ProcessPoolExecutor() as executor:
            step = 1 + len(index) // executor._max_workers
            indexes = [
                index[n * step : (n + 1) * step] for n in range(executor._max_workers)
            ]
            result = []
            for n, idx in enumerate(indexes):
                args = [vocab, docs, idx, n * step, bar]
                result.append(executor.submit(process_slice, *args))
        bar.close()
    print("Instantiating document term matrix")
    data, rows, cols = [sum(x, []) for x in zip(*[r.result() for r in result])]
    matrix = coo_matrix(
        (data, (rows, cols)), shape=(len(index), len(vocab)), dtype=bool
    )
    dtm = pandas.SparseDataFrame(
        data=matrix, index=index, columns=vocab, default_fill_value=False
    )
    self.dtm = dtm
    if store:
        print("Storing document term matrix")
        ioio.store(self.dtm, fname, self.data_dir)


def process_slice(vocab, docs, index, istart, bar):
    """
    Used in `load_dtm_conc`.
    """
    data, rows, cols = [], [], []
    for row, ind in enumerate(index, istart):
        doc = docs[ind]
        for col, term in enumerate(vocab):
            if term in doc:  # bool:in
                data.append(True)
                rows.append(row)
                cols.append(col)
        bar.update()
    return data, rows, cols
