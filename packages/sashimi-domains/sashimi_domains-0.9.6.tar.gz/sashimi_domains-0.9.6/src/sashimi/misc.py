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

from hashlib import sha256
import importlib
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_IMPORT_TRIED = set()

#################
# Import helper #
#################


_IMPORT_MESSAGES = {
    "graph_tool": (
        "Failed to import `graph_tool`,"
        " graph models and network visualisations will be unavailable."
        " See <https://graph-tool.skewed.de/> for installation instructions."
    ),
    "gensim": (
        "Failed to import `gensim`, producing n-grams and word vectors"
        " (deprecated) will be unavailable"
    ),
    "spacy": "Failed to import `spacy`: tokenization will be unavailable.",
}


def _try_import(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        package_name = module_name.split(".")[0]
        global _IMPORT_TRIED
        if package_name not in _IMPORT_TRIED:
            logger.warning(_IMPORT_MESSAGES[package_name])
            _IMPORT_TRIED.add(package_name)


#####################
# Property helpers  #
#####################


def _fset_dir(property_name):
    property_name = f"_{property_name}"

    def fset(self, val):
        val = Path(val)
        val.mkdir(exist_ok=True)
        setattr(self, property_name, val)

    return fset


def makep(p, fget=True, fset=True, fdel=True, doc=None):
    p = f"_{p}"
    if fget is True:
        fget = lambda self: getattr(self, p)
    if fset is True:
        fset = lambda self, v: setattr(self, p, v)
    if fdel is True:
        fdel = lambda self: delattr(self, p)
    return property(fget, fset, fdel, doc)


def makep_fromdict(d, p, fget=True, fset=True, fdel=True, doc=None):
    if fget is True:
        fget = lambda self: getattr(self, d).__getitem__(p)
    if fset is True:
        fset = lambda self, v: getattr(self, d).__setitem__(p, v)
    if fdel is True:
        fdel = lambda self: getattr(self, d).__delitem__(p)
    return property(fget, fset, fdel, doc)


def property_getfuncdir(func):
    def g(self):
        val = func(self)
        os.makedirs(val, exist_ok=True)
        return val

    return property(g)


def checkp(self, p):
    try:
        getattr(self, p)
    except AttributeError:
        return False
    return True


def clearattrs(obj, names):
    for name in names:
        try:
            delattr(obj, name)
        except AttributeError:
            pass


###############
# Stable hash #
###############


def get_hash(x, length=7):
    return sha256(json.dumps(list(x)).encode()).hexdigest()[:length]


################
# lxml helpers #
################


def display_html_in_browser(el, title="Corporalogister"):
    from tempfile import NamedTemporaryFile
    import webbrowser
    from lxml import html
    from lxml.builder import build

    doc = build.HTML(build.HEAD(build.TITLE(title)))
    doc.append(build.BODY(el))
    with NamedTemporaryFile() as f:
        f.write(html.tostring(doc))
        f.flush()
        webbrowser.open(f.name)
        input("Hold until the browser gets a chance to load the file!")
