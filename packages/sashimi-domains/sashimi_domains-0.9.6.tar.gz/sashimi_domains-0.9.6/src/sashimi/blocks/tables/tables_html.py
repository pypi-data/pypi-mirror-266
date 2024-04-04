from pathlib import Path
import re

from bokeh.resources import INLINE as bokeh_INLINE

import colorcet

import lxml.html as html
import lxml.html.builder as E

TABLES_CSS = Path(__file__).parent / "tables.css"


def html_output(body_elements, outfile):
    outfile = Path(outfile)
    outfile.write_bytes(html.tostring(html_build(body_elements)))
    # html_build(report).getroottree().write(outfile, method='html')
    return outfile


def html_build(body_elements):
    head = E.HEAD(
        E.META(charset="utf-8"),
        E.BASE(target="_blank"),
        E.TITLE("Sashimi block report"),
        E.STYLE(TABLES_CSS.read_text()),
    )
    body = E.BODY(*body_elements)
    if body.xpath("//div[@data-root-id]"):
        head.extend(html.fragments_fromstring(bokeh_INLINE.render()))

    return E.HTML(head, body)


def html_domain_documents_table(data, labels, code_terms_map=None):
    format_marks = make_format_marks(code_terms_map)
    tr = E.TR()
    if "venues" in data:
        tr.append(E.TH("Venue"))
    tr.append(E.TH("Title"))
    tr.append(E.TH("Abstract"))
    if "code_terms" in data:
        tr.append(E.TH("Code terms"))
    table = E.TABLE(
        E.THEAD(tr),
        tbody := E.TBODY(),
    )
    for idx in data["examples"].index:
        tr = E.TR()
        if "venues" in data:
            tr.append(E.TD(data["venues"].loc[idx]))
        tr.append(
            E.TD(html.fragment_fromstring(data["titles"].loc[idx], create_parent="p"))
        )
        tr.append(
            E.TD(
                *[
                    y
                    for x in data["abstracts"].loc[idx]
                    for y in (*format_marks(x), E.HR)
                ][:-1],
                CLASS="abstracts",
            )
        )
        if "code_terms" in data:
            tr.append(
                E.TD(format_code_terms(data["code_terms"].loc[idx]), CLASS="code_terms")
            )
        tbody.append(tr)
    return E.DIV(table)


def html_xblock_yblocks_table(data, xbtype, labels):
    yb_key = "common" if "common" in data else "specific"
    table = E.TABLE(
        E.THEAD(
            E.TR(
                E.TH(
                    data["id"],
                    E.BR,
                    E.BR,
                    E.SMALL(f"({pow(2, data[yb_key]['ent'][1]):.2})", CLASS="tstats"),
                )
            )
        )
    )
    tbody = E.TBODY()
    table.append(tbody)
    tbody.append(
        E.TR(
            E.TD(
                E.DIV(
                    *format_xblock_yblocks_elements(data[yb_key], labels),
                    CLASS="single_yblocks",
                )
            )
        )
    )
    if "plot" in data:
        tbody.append(
            E.TR(
                E.TD(
                    E.DIV(
                        *map(html.fragment_fromstring, data["plot"]),
                        CLASS="single_yblocks",
                    )
                )
            )
        )
    return E.DIV(table)


def html_multi_xblocks_yblocks_table(data, xbtype, labels, plots=False):
    levels = sorted(set(x[0] for x in data))
    deep = levels != [1]
    ln_label = f"L{levels[-1]}{xbtype[0].upper()}" if len(levels) == 1 else "ID"
    l1_label = f"L1{xbtype[0].upper()}"
    columns = (
        ["Plot", ln_label, "Common", "Plot", l1_label, "Specific", "Elements"]
        if deep and plots
        else [ln_label, "Common", l1_label, "Specific", "Elements"]
        if deep and not plots
        else ["Plot", l1_label, "Specific", "Elements"]
        if not deep and plots
        else [l1_label, "Specific", "Elements"]
    )
    table = E.TABLE(E.THEAD(E.TR(*(E.TH(str(key)) for key in columns))))
    tbody = E.TBODY()
    table.append(tbody)
    for _, d_data in data.items():
        drow = E.TR()
        if deep:
            if plots:
                drow.append(E.TD(*map(html.fragment_fromstring, d_data["plot"])))
            drow.extend(
                (
                    E.TD(
                        d_data["id"],
                        E.BR,
                        E.BR,
                        E.SMALL(
                            f"({pow(2, d_data['common']['ent'][1]):.2})", CLASS="tstats"
                        ),
                        rowspan=str(len(d_data[l1_label])),
                        CLASS="label",
                    ),
                    E.TD(
                        *format_xblock_yblocks_elements(d_data["common"], labels),
                        CLASS="yblocks",
                        rowspan=str(len(d_data[l1_label])),
                    ),
                )
            )
        for _, sd_data in d_data[l1_label].items():
            tbody.append(drow)
            if plots:
                drow.append(E.TD(*map(html.fragment_fromstring, sd_data["plot"])))
            drow.extend(
                (
                    E.TD(
                        sd_data["id"],
                        E.BR,
                        E.BR,
                        E.SMALL(
                            f"({pow(2, sd_data['specific']['ent'][1]):.2})",
                            CLASS="tstats",
                        ),
                        CLASS="label",
                    ),
                    E.TD(
                        *format_xblock_yblocks_elements(sd_data["specific"], labels),
                        CLASS="yblocks",
                    ),
                    E.TD(format_elements(sd_data["elements"]), CLASS="elements"),
                )
            )
            drow = E.TR()
    return E.DIV(table)


def format_xblock_yblocks_elements(xblock_yblocks_elements, labels):
    formatted = []
    ylevel = xblock_yblocks_elements["levels"][1]
    for yb, yb_info in xblock_yblocks_elements["blocks"].items():
        formatted.extend(
            (
                labels(ylevel, yb),
                E.SMALL(
                    f' ({yb_info["ent"] / xblock_yblocks_elements["ent"][1]:.0%})',
                    CLASS="tstats",
                ),
                ": ",
            )
        )
        for el, el_ent in yb_info["elements"]:
            formatted.extend(
                (
                    f"{el}",
                    E.SMALL(f' ({el_ent / yb_info["ent_el"]:.0%})', CLASS="tstats"),
                )
            )
            formatted.append(", ")
        formatted.pop()
        formatted.append(E.BR())
        formatted.append(E.BR())
    if formatted:
        formatted.pop()

    return formatted


def format_elements(elements):
    return E.UL(*(html.fragment_fromstring(x, create_parent="li") for x in elements))


def format_code_terms(code_terms):
    return E.UL(
        *(
            html.fragment_fromstring(
                f'<span style="font-size:0;opacity:0">code:</span>{x}',
                create_parent="li",
            )
            for x in code_terms
        )
    )


def make_format_marks(code_terms_map):
    if code_terms_map is None:
        return lambda x: x

    def split_rx(rex):
        return re.compile(r"(?i)\b(" + rex + r")\b")

    code_terms_rx = {k: split_rx(v) for k, v in code_terms_map.items()}
    code_terms_color = {
        k: colorcet.glasbey_dark[i] for i, k in enumerate(code_terms_map)
    }
    all_code_terms_rx = split_rx(r"|".join(code_terms_map.values()))

    def get_color(text):
        for term, term_rx in code_terms_rx.items():
            if term_rx.match(text):
                return code_terms_color[term]
        raise ValueError("Text did not match a term.")

    def format_marks(text):
        parts = all_code_terms_rx.split(text)
        return [
            E.SPAN(x, STYLE=f"color: white; background-color: {get_color(x)}")
            if i % 2
            else x
            for i, x in enumerate(parts)
        ]

    return format_marks
