from functools import cache
import os
import random
from random import randint
from string import ascii_lowercase
from tempfile import TemporaryDirectory

import pandas as pd
import sashimi

if "BASE_DIR" not in locals():
    BASE_DIR = TemporaryDirectory(prefix="sashimi_test-")
    os.chdir(BASE_DIR.name)
    print(BASE_DIR.name)

if "VALUES_EXAMPLE_DATA" not in locals():
    VALUES_EXAMPLE_DATA = [0, 1, 3]
    # VALUES_EXAMPLE_DATA = [3]


@cache
def example_data():
    if EXAMPLE_DATA == 0:
        df = pd.DataFrame(
            {
                "tokens": [
                    (("bla", "bla"),),
                    (("bla", "ble"),),
                    [["bli"], ["blo", "blu"]],
                    (("bla", "ble", "bli"),),
                ],
                "title": ["bla", "ble", "bli", "blo"],
                "meta": [1, 2, 4, 2],
                "url": [
                    "https://usp.br",
                    "https://fsf.org",
                    "https://hyr.science",
                    "file:///home/",
                ],
                "time": ["1998", "1999", "", "2002"],
            }
        )
    elif EXAMPLE_DATA == 1:
        df = pd.DataFrame(
            {
                "tokens": [[["bla", "bla"]], [["bla", "ble"]], [["bla", "ble", "bli"]]],
                "title": ["bla", "ble", "bli"],
                "meta": [1, 2, 2],
            }
        )
    elif EXAMPLE_DATA == 3:
        random.seed("cafu")
        num_documents = 500
        num_topics = 20
        topics = {
            num: [
                "".join(
                    ascii_lowercase[i]
                    for i in (
                        randint(0, len(ascii_lowercase) - 1)
                        for _ in range(0, randint(2, 20))
                    )
                )
                for _ in range(0, randint(10, 30))
            ]
            for num in range(0, num_topics)
        }
        tokens = [
            [
                [
                    topics[t % num_topics][randint(0, len(topics[t % num_topics]) - 1)]
                    for t in range(i, i + num_topics // 4)
                ]
            ]
            for i in range(num_documents)
        ]
        df = pd.DataFrame(
            {
                "tokens": tokens,
                "title": [" ".join(tok[0][0 : randint(3, 6)]) for tok in tokens],
                "meta": [tok[0][-1] for tok in tokens],
                "time": [2 * len(tok[0][0]) for tok in tokens],
            }
        )
    df.name = str(EXAMPLE_DATA)
    return df


@cache
def example_corpus(overwrite=False):
    df = example_data()
    corpus = sashimi.GraphModels(load_data=False)
    corpus.load_data(df)
    corpus.column = "tokens"
    corpus.col_title = "title"
    if "url" in df:
        corpus.col_url = "url"
    if "time" in df:
        corpus.col_time = "time"
    corpus.store_data(overwrite=overwrite)
    return corpus


@cache
def example_corpus_dtm():
    corpus = example_corpus()
    corpus.load_domain_topic_model()
    corpus.state.entropy()
    corpus.register_config(f"{corpus.data_name}-dtm.json")
    return corpus


@cache
def example_corpus_dcm():
    corpus = example_corpus_dtm()
    corpus.set_chain("meta")
    corpus.load_domain_chained_model()
    corpus.state.entropy()
    corpus.register_config(f"{corpus.data_name}-dcm.json")
    return corpus


def test_data_store_load():
    corpus = example_corpus()
    data = corpus.load_from_store(corpus.loaded["data"], return_not_load=True)
    return corpus.data.compare(data)


def test_corpus_dtm_maps():
    corpus = example_corpus_dtm()
    dm = corpus.domain_map()
    dns = corpus.domain_network(doc_level=1, edges="specific")
    dnc = None
    if 2 in corpus.dblocks_levels:
        dnc = corpus.domain_network(doc_level=2, edges="common")
    return dm, dns, dnc


def test_corpus_dcm_maps():
    corpus = example_corpus_dcm()
    dm = corpus.domain_map()
    dm = corpus.domain_map(chained=True)
    dns = corpus.domain_network(doc_level=1, ext_level=1, edges="specific")
    dnc = None
    if 2 in corpus.dblocks_levels:
        dnc = corpus.domain_network(doc_level=2, ext_level=1, edges="common")
    return dm, dns, dnc


def load_test_corpus(number, kind="dtm"):
    name = f"{number}.json.xz-{kind}.json"
    corpus = sashimi.GraphModels(name)
    if kind == "dtm":
        corpus.load_domain_topic_model()
    else:
        corpus.load_domain_chained_model()
    return corpus


def cache_clear():
    cleared, caching = 0, 0
    names_obj = globals()
    for name, obj in names_obj.items():
        if name.startswith("test_") or name.startswith("example_"):
            if hasattr(obj, "cache_clear"):
                if obj.cache_info().currsize:
                    obj.cache_clear()
                    cleared += 1
                caching += 1
    return {"cleared": cleared, "caching": caching}


def gen_name_test():
    names_obj = globals()
    for name, obj in names_obj.items():
        if name.startswith("test_"):
            yield name, obj


def main():
    global EXAMPLE_DATA
    cache_clear()
    for EXAMPLE_DATA in VALUES_EXAMPLE_DATA:
        try:
            print("EXAMPLE_DATA:", EXAMPLE_DATA)
            for name, test in gen_name_test():
                print(name)
                print(test())
        finally:
            cache_clear()


if __name__ == "__main__":
    main()
