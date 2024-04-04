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


class GraphologyLimbo(Blockology, Scorology, Corporalogy):
    def __init__(self):
        self.sext = ".score"

    def from_vector_model(self, model, mode=None, savename=False):
        """
        TODO: use wmdistance ? use multigraph ?
        """
        print("Building graph...")
        g = gt.Graph(directed=False)
        g.vp["name"] = g.new_vertex_property("string")
        g.vp["count"] = g.new_vertex_property("int")
        g.ep["distance"] = g.new_edge_property("float")

        stop = set(stopwords.words("english"))
        # prevocab = [w for w in model.wv.vocab if model.wv.vocab[w].count>500]
        prevocab = [w for w in model.wv.vocab if model.wv.vocab[w].index <= 3000]
        vocab = [w for w in prevocab if w not in stop]
        vecvoc = numpy.array([model[w] for w in vocab])

        print("Adding vertices...")
        for word in vocab:
            v = g.add_vertex()
            g.vp["name"][v] = word
            g.vp["count"][v] = model.wv.vocab[word].count
        print("\n|V|: {}\n".format(g.num_vertices()))

        print("Adding edges...")
        if mode == None:

            def edges():
                vwords = list(g.vertices())
                count = 0
                pdistances = pdist(vecvoc, "cosine")
                for v1 in g.vertices():
                    print(count, end=" ", flush=True)
                    vwords.pop(0)
                    for v2 in vwords:
                        if pdistances[count] < 0.25:
                            yield (int(v1), int(v2), pdistances[count])
                        count += 1

        g.add_edge_list(edges(), eprops=[g.ep["distance"]])

        print("\n|V|, |E|: {}, {}\n".format(g.num_vertices(), g.num_edges()))
        # cleanup g
        f = g.new_vertex_property("bool")
        p = g.degree_property_map("total")
        for v in g.vertices():
            f[v] = bool(p[v])
        g.set_vertex_filter(f)
        g.purge_vertices()
        g.clear_filters()
        print(
            "\n|V|, |E|: {}, {} after cleanup\n".format(g.num_vertices(), g.num_edges())
        )

        if isinstance(savename, str):
            g.save(savename)
        return g

    def get_vector_graph_state(self, g, savename=False):
        g.ep["similarity"] = g.new_edge_property("int")
        for e in g.edges():
            g.ep["similarity"][e] = numpy.floor(5 * (1 - g.ep["distance"][e]))

        state = gt.minimize_nested_blockmodel_dl(
            g, state_args=dict(eweight=g.ep["similarity"])
        )  # , overlap=True)

        if savename:
            with open(savename + ".pic", "wb") as f:
                pickle.dump(state, f)

        return state

    def from_vector_vocab(
        self,
        data,
        mode,
        savename=False,
        nostopwords=False,
        reducevocab=False,
        directed=False,
    ):
        stopw = set(stopwords.words("english"))
        basemodel = gensim.models.Word2Vec(workers=multiprocessing.cpu_count())
        basemodel.build_vocab(sum(d, ()) for d in data.abstract)
        vocab = basemodel.wv.vocab

        g = gt.Graph(directed=directed)
        g.vp["name"] = g.new_vertex_property("string")
        g.ep[self.time] = g.new_edge_property("int")
        if mode.endswith("multi"):
            g.ep["multi"] = g.new_edge_property("int")

        vocabmaxi = max(vocab[w].index for w in vocab)

        evocab = {x for x in vocab}
        if nostopwords:
            evocab.difference_update(stopw)
        if reducevocab:
            grade, wfreq, dfreq = self.get_graded_vocab()
            evocab = sorted(evocab, key=lambda x: grade[x])
            evocab = set(list(filter(lambda x: dfreq[x] > 99, evocab))[-1000:])

        print("Vocabinfo (len, maxi, nonstop):", len(vocab), vocabmaxi, len(evocab))

        g.add_vertex(vocabmaxi + 1)
        for w in vocab:
            g.vp["name"][vocab[w].index] = w  # not safe if isolated v
        print("Lenabs:", len(data))

        def edges_seq():
            for n, i in enumerate(data.index):
                if not n % 10:
                    print(n, end="\r", flush=True)
                for sentence in data.abstract.loc[i]:
                    words = [w for w in sentence if w in evocab]
                    for first, second in zip(words, words[1:]):
                        yield (
                            vocab[first].index,
                            vocab[second].index,
                            data[self.time].loc[i],
                        )
            print()

        def edges_doc():
            for n, i in enumerate(data.index):
                if not n % 10:
                    print(n, end="\r", flush=True)
                words = {w for s in data.abstract.loc[i] for w in s if w in evocab}
                for first, second in combinations(words, 2):
                    yield (
                        vocab[first].index,
                        vocab[second].index,
                        data[self.time].loc[i],
                    )
            print()

        def edges_doc_multi():
            for gname, group in data.groupby(self.time):
                multi = {}
                for n, abstract in enumerate(group.abstract):
                    if not n % 10:
                        print(gname, n, end="\r", flush=True)
                    words = {w for s in abstract for w in s if w in evocab}
                    for pair in map(frozenset, combinations(words, 2)):
                        multi[pair] = multi.get(pair, 0) + 1
                print()
                for pair in multi:
                    yield (*[vocab[e].index for e in pair], gname, multi[pair])

        edges = {"seq": edges_seq, "doc": edges_doc, "doc_multi": edges_doc_multi}[mode]
        g.add_edge_list(
            edges(),
            eprops=[g.ep[self.time]]
            + ([g.ep["multi"]] if mode.endswith("multi") else []),
        )

        if isinstance(savename, str):
            g.save(savename)
        return g

    def gen_voc_edges(self, docs, vocabindex, sample, eprop=None):
        idx = self.samplify(sample, docs)
        many = len(idx) > 1
        if many:
            print("Docs: {} to {}".format(idx.min(), idx.max()))
        for di in idx:
            if many:
                print("\rProcessing doc: {:<42}".format(di), end="")
            words = {w for s in docs[di] for w in s}
            for first, second in combinations(words, 2):
                yield (vocabindex[first], vocabindex[second]) + (
                    (self.data.loc[di, eprop],) if eprop else ()
                )
        if many:
            print()

    def from_corpus_to_voc(
        self, use_context=False, use_eweight=False, sample=None, savename=False
    ):
        """
        Builds a graph of words.

        In its unipartite version, words connect to words present in the same
        document, forming an undirected graph.

        In the bipartite version, words connect to context nodes in which
        theyŕe found, which in turn connect back to words that compose it.

        Optionally represents the multigraph with edge weights.
        """
        docs = self.data[self.column]
        vocab = {w for d in docs for s in d for w in s}
        print("Vocab size: {}".format(len(vocab)))
        vocabindex = dict((w, n) for n, w in enumerate(vocab))

        g = gt.Graph(directed=use_context)
        if use_context:
            # type: 0=> document, 1=>word, 2=<context
            g.vp["type"] = g.new_vertex_property("int")
        g.vp["name"] = g.new_vertex_property("string")
        g.ep[self.time] = g.new_edge_property("int")
        if use_eweight:
            g.ep["multi"] = g.new_edge_property("int")
        g.add_vertex(len(vocab))
        for w, vi in vocabindex.items():
            if use_context:
                g.vp["type"][vi] = 1
            g.vp["name"][vi] = w
        g.add_edge_list(
            self.gen_voc_edges(docs, vocabindex, sample, eprop=self.time),
            eprops=[g.ep[self.time]]
            if not use_eweight
            else [g.ep[self.time], g.ep["multi"]],
        )

        if isinstance(savename, str):
            g.save(savename)
        return g

    def load_scores(self, name, calc=True):
        scores = pandas.DataFrame()
        name = path.basename(path.normpath(name))
        if name.endswith(self.nbext):
            name = name[: -len(self.nbext)]
        for nbname in os.listdir(self.graphs_path):
            if not (nbname.startswith(name) and nbname.endswith(self.nbext)):
                continue

            print("Loading scores for {}".format(nbname))
            sname = nbname[: -len(self.nbext)] + self.sext
            fullsname = path.join(self.analysis_dir, sname)
            groupname = nbname[: -len(self.nbext)].split("-")[-1]
            if groupname.isdigit():
                groupname = int(groupname)

            if path.exists(fullsname):
                with open(fullsname, "br") as f:
                    scores[groupname] = pickle.load(f)
                print("Loaded previously saved scores: {}".format(sname))
                continue
            if not calc:
                continue

            with open(path.join(self.graphs_path, nbname), "br") as f:
                state = pickle.load(f)
            docs = self.data[self.column]
            vocabindex = dict((state.g.vp["name"][v], v) for v in state.g.vertices())
            for di in docs.index:
                print("\rProcessing doc: {:<42}".format(di), end="")
                edges = list(self.gen_voc_edges(docs, vocabindex, [di]))
                scores.loc[di, groupname] = state.get_edges_prob(missing=edges)
            print()
            with open(fullsname, "bw") as f:
                pickle.dump(scores[groupname], f)

        return scores

    def draw_blockmodel_state(self, g, state, savename=False):
        bs = state.get_bs()

        members = dict()
        for i, j in enumerate(bs[0]):
            j = bs[1][j]
            members.setdefault(j, []).append(i)

        vpmap = g.vp["count"] if "count" in g.vp else g.degree_property_map("total")

        g.vp["fname"] = g.new_vertex_property("string")
        for l in members.values():
            visible = sorted(l, key=lambda x: vpmap[x])[:3]
            v_labeled = sorted(
                l, key=lambda x: g.vertex(x, use_index=False).out_degree()
            )[int(len(l) / 2)]
            g.vp["fname"][v_labeled] = ", ".join([g.vp["name"][vi] for vi in visible])
            print(" ".join([g.vp["name"][vi] for vi in visible]))

        draw_kwargs = dict(
            vertex_text=g.vp["fname"],
            vertex_text_position="centered",
            fit_view=0.5,
            vertex_font_size=18,
            subsample_edges=1,
            # layout='radial',
            # hide=1
        )
        if savename:
            state.draw(output=savename, **draw_kwargs)
        else:
            state.draw(**draw_kwargs)

    def blocks_to_csv(
        self, savename, join=["year", "journal", "title", "authors", "affiliations"]
    ):
        """
        savename: file to save to, relative to self.analysis_dir
        blockstate_to_dataframe, or dataframe returned by said method
        """
        df = self.blocks
        # df = df.rename(columns=lambda x: 'L'+str(x) if type(x) is int else x)
        if join:
            dfj = self.data[join]
            df = df.join(dfj)
        df["_index"] = df.index
        df = df.sort_values(["type", "_index"])
        del df["_index"]
        if "affiliations" in df:
            df.affiliations = df.affiliations.apply(
                lambda x: x if len(repr(x)) < 32000 else x[0]
            )
        df.to_csv(self.analysis_dir / savename)

    ######################
    # Blockstate methods #
    ######################

    def calc_nested_blockstate_mcmc(self, name_args=[]):
        for irun in count():
            fname = naming.gen(
                "blockstate",
                [("step", "aneq")] + name_args + [("run", irun)],
                self.suffix_nbs,
            )
            try:
                (self.graph_dir / fname).mkdir(exist_ok=False)
                print("Reserving name: {}".format(fname))
                break
            except OSError:
                pass

        fpath = self.graph_dir / fname / fname
        state_args = {}
        if "type" in self.graph.vp:
            state_args["pclabel"] = self.graph.vp["type"]
            print('Vertex property "type" found, using it as pclabel')

        ns = gt.NestedBlockState(self.graph, state_args=state_args)
        gt.mcmc_anneal(ns)
        gt.mcmc_equilibrate(ns, mcmc_args={"beta": numpy.inf})

        # bs = self.step_nested_blockstate(ns, runs)
        # ns = ns.copy(bs=bs)

        self.store_blockstate(fpath=fpath, state=ns)
        print("Saved state: {}".format(fname))
        self.loaded["blockstate"] = fname
        return fname

    def step_nested_blockstate(self, ns, runs=10):
        """
        Executes a `steps` steps, `runs` runs optimization of a blockstate.

        A run is a regular MCMC equilibration of a state, keeping track of the
        lowest entropy state discovered.
        A step consists of `runs` runs, all starting from the same state, and
        returns the lowest entropy state over all runs.
        The first step starts from `ns`, subsequent steps start from the state
        returned by the previous one.
        The best state overall gets returned.

        Parameters
        ----------
        ns: gt.NestedBlockState
        runs: int
        steps: int

        Returns
        -------
        bs: list of numpy.ndarray
            The blockstate of lowest entropy over all discovered.
        """

        def step(start_bs, sruns, count):
            def cb_run(ns):
                # for efficiency do not consider variations from non continuity
                cur_ent = ns.entropy()
                if cur_ent < best_ent[-1]:
                    best_bs[-1] = [b.copy() for b in ns.get_bs()]
                    best_ent[-1] = cur_ent
                return None

            best_bs, best_ent = [], []
            for _ in tqdm(range(sruns), desc="Step #{}".format(count)):
                nsc = ns.copy(bs=[b.copy() for b in start_bs])
                best_bs.append([b.copy() for b in nsc.get_bs()])
                best_ent.append(nsc.entropy())
                gt.mcmc_equilibrate(nsc, callback=cb_run)
                best_bs[-1] = self.continuous_map_nested_blockstate(
                    best_bs[-1], io_is_bs=True
                )
                best_ent[-1] = nsc.copy(bs=best_bs[-1]).entropy()
            bestest_bs, bestest_ent = sorted(
                zip(best_bs, best_ent), key=lambda x: x[1]
            )[0]
            return bestest_bs, bestest_ent

        bs = [b.copy() for b in ns.get_bs()]
        ent = ns.entropy()
        print("Entropy: {}".format(ent))
        for count in icount():
            sruns = ceil(runs / 2**count)
            bs, ent = step(bs, sruns, count)
            print("Entropy: {}".format(ent))
            if sruns == 1:
                break

        return bs, ent
