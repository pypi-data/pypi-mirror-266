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

import numpy, os, pandas
import lxml.html as html, lxml.html.builder as build
from collections import OrderedDict
from matplotlib import pyplot as plt, colors as colors
from scipy.special import logsumexp

from .w2v_score import score_words, score_sentence, score_word_pair
from .misc import display_html_in_browser


class Scorology:
    """
    Analysis based on document scores provided by a model.
    Usually operate without modifying core data.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scores = pandas.DataFrame()

    def clear_scores(self):
        self.scores = pandas.DataFrame()

    def get_mode(self, mode):
        """
        Useful transformation and normalizations to apply to scores
        """
        # fix() makes values proportional to total ensemble probability,
        # allowing for more meaningful comparisons between models
        nanlogsumexp = lambda x: logsumexp(x[x.notnull()])
        fix = lambda x: x.sub(x.apply(nanlogsumexp))
        if mode == "raw":
            trans = lambda x: x
            norm = lambda x: x
        elif mode == "rank":
            trans = lambda x: fix(x).rank()
            norm = lambda x: x.div(x.max())
        elif mode == "score":
            trans = lambda x: fix(x)
            norm = lambda x: x
        elif mode == "prob":
            trans = lambda x: fix(x).apply(numpy.exp)
            norm = lambda x: x
        return dict(name=mode, trans=trans, norm=norm)

    def get_scores(
        self,
        balance="nobalance",
        balanceby=None,
        noselfby=None,
        normalize=True,
        mode="score",
    ):
        if self.scores.empty:
            raise Exception("No scores loaded!")
        scores = self.scores
        if noselfby:

            def removeself(x):
                s = x.copy()
                where = x.name == self.data[noselfby]
                s[where] = numpy.nan
                return s

            scores = scores.apply(removeself)
        if balance != "nobalance":
            if balanceby:
                locs = pandas.DataFrame().index
                sdata = self.shuffled_data()
                for group, gdata in self.balance_groups(
                    sdata.groupby(balanceby), balance
                ):
                    locs = locs.append(gdata.index)
                scores = scores.loc[
                    locs
                ]  # May duplicate index values, will clean below
            else:
                raise Exception('Balanced scoring requires "balanceby"')
        scores = scores.loc[~scores.index.duplicated()]  # Clean duplicates
        print("get_scores(): len scores is {}".format(len(scores)))
        mode = self.get_mode(mode)
        scores = mode["norm"](mode["trans"](scores))
        return scores

    def get_scoremax(
        self,
        balance="nobalance",
        balanceby=None,
        noselfby=None,
        style=None,
        mode="score",
    ):
        scores = self.get_scores(
            balance=balance, balanceby=balanceby, noselfby=noselfby, mode=mode
        )
        cols = list(scores.columns)
        cols = list(reversed(cols))  # For idxmax to break ties towards later groups
        # numpy.random.shuffle(cols) # Check influence of idxmax taking 1st max idx found
        scores = scores[cols]
        scoremax = scores.idxmax(axis=1)

        if style and style["name"] == "diff":
            scoremax = scoremax - self.data.loc[scoremax.index, "year"]
            if "limit" in style:

                def limit_range(x, limit=style["limit"]):
                    if x < -limit:
                        return -limit
                    elif x > +limit:
                        return +limit
                    else:
                        return x

                scoremax = scoremax.apply(limit_range)
        print("Len scoremax is {}".format(len(scoremax)))
        return scoremax

    def get_scoreorder(
        self, balance="nobalance", balanceby=None, noselfby=None, mode="score"
    ):
        scores = self.get_scores(
            balance=balance, balanceby=balanceby, noselfby=noselfby, mode=mode
        )
        scoresorted = scores.apply(
            lambda x: x.sort_values(ascending=False).index, axis=1
        )
        return scoresorted

    def plot_scores(
        self,
        groupby=None,
        balance="nobalance",
        noself=False,
        yscale="linear",
        mode="score",
    ):
        yscale = {"value": yscale} if type(yscale) is str else yscale
        scores = self.get_scores(
            balance=balance,
            balanceby=groupby,
            noselfby=(groupby if noself else None),
            mode=mode,
        )
        scores[groupby] = self.data[groupby]
        # Each subplot is a model crossed with the corpus for each group
        numfigrows = int(numpy.ceil(len(scores.columns) / 3))
        axs = scores.boxplot(
            by=groupby,
            layout=(numfigrows, 3),
            whis=[5, 95],
            showmeans=1,
            rot=90,
            figsize=(17, 17),
        )
        for ax in axs:
            for a in ax:
                a.set_yscale(**yscale)
        axs[0][0].get_figure().texts[0].set_text("Models by data")
        plt.savefig(
            os.path.join(
                self.analysis_dir,
                "{}-models_by_data-{}-{}.pdf".format(mode, balance, yscale["value"]),
            )
        )
        plt.close()
        del scores[groupby]
        # Each subplot is the corpus for that group crossed with each of the models
        grouped_data = self.data.groupby((lambda x: 0) if groupby is None else groupby)
        plt.figure(figsize=(17, 17))
        for i, (group, idxs) in enumerate(grouped_data.groups.items()):
            plt.subplot(int(numpy.ceil(len(grouped_data) / 3)), 3, i + 1)
            scores.loc[idxs]
            ax = scores.loc[idxs].boxplot(whis=[5, 95], showmeans=1, return_type="axes")
            ax.set_title(str(group))
            ax.set_xticklabels([x.get_text()[-2:] for x in ax.get_xticklabels()])
            ax.set_yscale(**yscale)
        plt.tight_layout()
        plt.suptitle("Data by models")
        plt.savefig(
            os.path.join(
                self.analysis_dir,
                "{}-data_by_models-{}-{}.pdf".format(mode, balance, yscale["value"]),
            )
        )
        plt.close()

    def plot_rankmax(
        self,
        groupby=None,
        balance="nobalance",
        noself=False,
        scale="linear",
        style=None,
        mode="score",
    ):
        rankmax = self.get_scoremax(
            balance=balance,
            balanceby=groupby,
            noselfby=(groupby if noself else None),
            style=style,
            mode=mode,
        )
        maxbygroup = OrderedDict()
        grouped_data = self.data.groupby((lambda x: 0) if groupby is None else groupby)
        for group, idxs in grouped_data.groups.items():
            grankmax = rankmax.loc[idxs]
            maxbygroup[group] = grankmax.groupby(grankmax).count()
        maxbygroup = pandas.DataFrame(maxbygroup).fillna(0).apply(lambda s: s / s.sum())
        plt.figure(figsize=(10, 7))
        norm = colors.LogNorm if scale == "log" else colors.Normalize
        plt.pcolormesh(maxbygroup.as_matrix(), cmap="OrRd", norm=norm())
        plt.yticks(numpy.arange(0.5, len(maxbygroup.index), 1), maxbygroup.index)
        plt.xticks(
            numpy.arange(0.5, len(maxbygroup.columns), 1),
            maxbygroup.columns,
            rotation=45,
        )
        plt.xlabel("data")
        plt.ylabel("model")
        plt.xlim(xmax=len(maxbygroup.columns))
        plt.ylim(ymax=len(maxbygroup.index))
        plt.colorbar()
        plt.savefig(
            os.path.join(
                self.analysis_dir,
                "{}max-{}-{}-{}-{}.pdf".format(
                    mode,
                    groupby if groupby else "nogroup",
                    balance,
                    "noself" if noself else "self",
                    scale,
                ),
            )
        )
        plt.close()

    def plot_rankmax_all(self, groupby=None):
        for balance in ("randomsample", "randomfill", "antidemisample", "nobalance"):
            for noself in (True, False):
                for scale in ("log", "linear"):
                    self.plot_rankmax(groupby, balance, noself, scale)

    def plot_profile(
        self,
        sample,
        groupby=None,
        balance="nobalance",
        noself=None,
        scale=None,
        mode="score",
        savefig=None,
    ):
        scores = self.get_scores(
            balance=balance,
            balanceby=groupby,
            noselfby=(groupby if noself else None),
            mode=mode,
        )
        index = self.samplify(sample, scores)
        for i in index:
            print(i, "\n", self.data.loc[i], "\n\n")
            plot_ext = dict(label=self.data.loc[i, groupby])
            if noself:
                marks = {
                    scores.columns[1]: [1],
                    scores.columns[-2]: [len(scores.columns) - 1],
                }.setdefault(self.data.loc[i, groupby], [])
                plot_ext.update(marker="o", markevery=marks)
            plt.plot(scores.columns, scores.loc[i], **plot_ext)
            if (
                str(type(self)) == "<class 'sashimi.vector_models.VectorModels'>"
                and len(index) == 1
                and False
            ):
                plot_ext["label"] = "pp-{}".format(plot_ext["label"])
                sentence = self.data.loc[i, self.column][0]
                mode = self.get_mode(mode)
                plt.plot(
                    list(self.embeddings),
                    mode["norm"](
                        mode["trans"](
                            pandas.DataFrame(
                                dict(
                                    scores=[
                                        (
                                            score_sentence(self.embeddings[k], sentence)
                                            / len(sentence)
                                            if not noself or k != self.data[groupby][i]
                                            else numpy.nan
                                        )
                                        for k in self.embeddings
                                    ]
                                )
                            )
                        )
                    ),
                    **plot_ext
                )
        if len(index) > 1:
            plt.plot(
                scores.columns,
                scores.loc[index].mean(),
                label="mean",
                color="red",
                linewidth=2,
            )
        if scale == "log":
            plt.yscale("log")
        #        plt.ylim([0.0,0.0035])
        plt.legend()
        plt.xlabel("model")
        if mode == "prob":
            plt.ylabel("likelihood (e^score)")
        elif mode == "score":
            plt.ylabel("log-likelihood (score)")
        if savefig:
            plt.savefig(savefig, format="svg")
        else:
            plt.show()
            input("Enter to close plot!")
        plt.close()

    def plot_wordpair_score_matrix(
        self, words, name="", scale="linear", upper=False, diagonal=True
    ):
        function = lambda m: lambda x, y: numpy.exp(score_word_pair(m, x, y))
        functions = OrderedDict(
            (mname, function(model)) for mname, model in self.embeddings.items()
        )
        return self.plot_wordpair_matrix(
            words,
            functions,
            funcname="prob",
            name=name,
            scale=scale,
            upper=upper,
            diagonal=diagonal,
        )

    def plot_wordpair_score_profile(self, words, name=""):
        function = lambda m: lambda x, y: numpy.exp(score_word_pair(m, x, y))
        functions = OrderedDict(
            (mname, function(model)) for mname, model in self.embeddings.items()
        )
        return self.plot_wordpair_profile(words, functions, funcname="prob", name=name)

    def annotate_sentences(self, sample, measures=["variance", "mean", "str"]):
        index = self.samplify(sample, self.data)
        print("Index is {}".format(list(index)))
        annotated = pandas.DataFrame(index=index, columns=measures, dtype=object)
        sentences = self.data.loc[index, self.column].apply(lambda x: sum(x, ()))
        for i in index:
            sent_scores = pandas.DataFrame(
                dict(
                    (name, score_words(model, sentences[i]))
                    for name, model in self.embeddings.items()
                )
            )
            sent_scores.loc[:, self.data.year[i]] = numpy.nan
            lenabs = len(
                [
                    w
                    for w in sentences[i]
                    if w in list(self.embeddings.values())[0].wv.vocab
                ]
            )
            sent_probs = sent_scores.div(lenabs).apply(numpy.exp)
            if "variance" in measures:  # relative variance
                annotated["variance"].set_value(
                    i, sent_probs.std(axis=1).div(sent_probs.mean(axis=1))
                )
            if "mean" in measures:
                annotated["mean"].set_value(i, sent_probs.mean(axis=1))
            if "str" in measures:
                annotated["str"].set_value(i, sent_probs.apply(str, axis=1))
        return {"sentences": sentences, "notes": annotated}

    def publish_annotations(
        self, sentences, notes, title="Annotated sentences", savename=None
    ):
        from matplotlib import colors, cm, colorbar
        import io
        from base64 import b64encode

        div0 = build.DIV()
        if title:
            div0.append(build.H1(title))
        for i in sentences.index:
            div1 = build.DIV(style="clear:both; padding:1em")

            with io.BytesIO() as bimg:
                self.plot_profile(
                    [i], groupby="year", noself=True, savefig=bimg, mode="prob"
                )
                img_p = build.IMG(
                    style="float:right;",
                    src="data:image/svg+xml;base64,"
                    + b64encode(bimg.getvalue()).decode(),
                )

            trunc = lambda x: x if len(x) <= 200 else x[:200] + " ..."
            d_id = self.data[self._labels["id"]][i]
            d_title = self.data[self._labels["title"]][i]
            d_venue = self.data[self._labels["venue"]][i]
            d_authors = self.data[self._labels["authors"]][i]
            d_authors = d_authors if type(d_authors) is tuple else [str(d_authors)]
            d_authors = trunc(", ".join(d_authors))
            d_affilia = self.data[self._labels["affiliations"]][i]
            d_affilia = d_affilia if type(d_affilia) is tuple else [str(d_affilia)]
            d_affilia = "({})".format(trunc("; ".join(d_affilia)))
            h2 = build.H2(
                build.A(
                    str(d_id),
                    href="https://www.ncbi.nlm.nih.gov/pubmed/{}".format(d_id),
                    style="text-decoration:none; color:#000099",
                )
            )
            p_m = build.P(
                build.EM(d_title),
                build.BR(),
                build.SPAN(d_authors),
                build.BR(),
                build.SPAN(d_affilia),
                build.BR(),
                build.EM(d_venue),
            )

            p_a = build.P()
            m_color, m_size, m_title = "variance", "mean", "str"
            note0, note1, note2 = (
                notes.loc[i, m_color],
                notes.loc[i, m_size],
                notes.loc[i, m_title],
            )
            norm0 = colors.Normalize()
            normed0 = norm0(note0[note0.notnull()])
            cseq = pandas.Series(index=note0.index, dtype=object)
            cseq.loc[note0.notnull()] = list(cm.coolwarm(normed0))
            norm1 = colors.Normalize()
            normed1 = norm1(note1[note1.notnull()])
            for word, clr, fs, n0, n1, n2 in zip(
                sentences[i], cseq, normed1, note0, note1, note2
            ):
                if type(clr) is float and numpy.isnan(clr):
                    style = "font-size: small"
                else:
                    style = "color: {};".format(colors.rgb2hex(clr))
                    style += "font-size: {}em;".format(1 + fs)
                s = build.SPAN(
                    word, style=style, title="Var: {}\nMean: {}\n{}".format(n0, n1, n2)
                )
                s.tail = " "
                p_a.append(s)
            p_a[-1].tail = ""

            with io.BytesIO() as bimg:
                fig = plt.figure(figsize=(1, 6))
                ax = fig.add_axes([0, 0.1, 0.3, 0.8])
                cb = colorbar.ColorbarBase(
                    ax, cmap=cm.coolwarm, norm=norm0, orientation="vertical"
                )
                cb.set_label("word-level {}".format(m_color))
                plt.savefig(bimg, format="svg")
                img_c = build.IMG(
                    style="float:right; margin-left:1em",
                    src="data:image/svg+xml;base64,"
                    + b64encode(bimg.getvalue()).decode(),
                )
                plt.close()

            div1.extend((img_p, img_c, h2, p_m, p_a))
            div0.append(div1)
        if savename:
            doc = build.HTML(build.HEAD(build.TITLE(title)))
            doc.append(build.BODY(div0))
            with open(os.path.join(self.analysis_dir, savename), "wb") as f:
                f.write(html.tostring(doc))
        else:
            display_html_in_browser(div0, title=title)
