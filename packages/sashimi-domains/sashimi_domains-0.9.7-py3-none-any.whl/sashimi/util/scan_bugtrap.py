#! /bin/env python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
scan_bugtrap.py: detects typical defects in scanned images

You can use this script from the command line, or as a library.

Command line usage:
./scan_bugtrap.py --help

Python usage:
from scan_bugtrap import scan_bugtrap
help(scan_bugtrap)
"""

import argparse
import sys, imageio as imgio, numpy as np
from scipy import ndimage as ndi
from os import path
from collections import Counter
from itertools import chain
from concurrent.futures import ProcessPoolExecutor

verbose = False


def vprint(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)


def clear_edges(img):
    """Get rid of noise on the borders and middle of the page."""
    img = img.copy()

    cmin, cmax = ndi.extrema(img)[:2]
    cmid = int(np.mean((cmax, cmin)))
    bimg = np.where(img > cmid, False, True)

    bimg = ndi.binary_opening(bimg, structure=[[1, 1, 0]])
    bimg = ndi.binary_closing(bimg, structure=np.ones((43, 43)))
    flabels, fnum = ndi.label(bimg)

    mask = np.zeros(img.shape, dtype=bool)
    img_area = img.shape[0] * img.shape[1]
    for feat, obj in zip(range(1, fnum + 1), ndi.find_objects(flabels)):
        height, width = obj[0].stop - obj[0].start, obj[1].stop - obj[1].start
        obj_area, feat_area = height * width, (flabels[obj] == feat).sum()
        if (
            obj_area > img_area / 128
            and width > img.shape[0] / 16
            and feat_area > obj_area / 2
        ):
            mask[obj] = True

    # imgio.imwrite('debug_labels.png', 10*flabels.astype(np.uint8))
    # imgio.imwrite('debug_mask.png', 20*mask.astype(np.uint8))
    # import pdb; pdb.set_trace()

    mask = ndi.binary_dilation(mask.any(axis=0), structure=[True] * 69)
    for i, val in enumerate(mask):
        if not val:
            img[:, i] = 0

    return img


def get_features(img):
    cmin, cmax = ndi.extrema(img)[:2]
    cmid = int(np.mean((cmax, cmin)))
    flabels, fnum = ndi.label(np.where(img > cmid, 0, 1))
    return flabels, fnum


def get_bugs(flabels, fnum):
    bugs = []
    for feat, obj in zip(range(1, fnum + 1), ndi.find_objects(flabels)):
        if (obj[0].stop - obj[0].start > 7) and (obj[1].stop - obj[1].start < 2):
            bugs.append((feat, obj))

    for feat, obj in bugs:
        vprint("Bug: feature {} at {}".format(feat, obj))
    vprint("{} bugs found".format(len(bugs)))

    return bugs


def get_bugimg(img, flabels, bugs):
    bugimg = np.zeros(img.shape, dtype=img.dtype)
    cmax = ndi.extrema(img)[1]
    for feat, obj in bugs:
        bugimg = np.where(flabels == feat, cmax, bugimg)
    return bugimg


def get_clnimg(img, flabels, bugs):
    img = img.copy()
    cmax = ndi.extrema(img)[1]
    for feat, obj in bugs:
        img = np.where(flabels == feat, cmax, img)
    return img


def is_bugged(bugs, confidence):
    bugged = False

    if not bugs or confidence == 1:
        # if we're very confident we're only detecting bugs
        bugged = bool(bugs)
    else:
        # if any 3 bugs fall within 5 pixes
        hist = Counter(chain(*(range(y[1].start - 2, y[1].stop + 2) for _, y in bugs)))
        bugged = max(hist.values()) > 2

    return bugged


def scan_bugtrap(fpath, clnimg=None, bugimg=None, confidence=0):
    """
    Find scanner bugs and judge an image as buggy based on those.

    Parameters
    ----------
    fpath: str
        The image file to be treated.
    clnimg: str
        If passed, path where to store a "clean" image.
    bugimg: str
        If passed, path where to store an image of bugs found.
    confidence: int
        Change how the image gets judged.

    Returns
    -------
    buggy: bool
        Whether the image is buggy or not.
    bugs: list
        The list of detected bugs.
    """
    img = imgio.imread(fpath)
    img = clear_edges(img)
    flabels, fnum = get_features(img)
    bugs = get_bugs(flabels, fnum)

    if clnimg:
        imgio.imwrite(clnimg, get_clnimg(img, flabels, bugs))
    if bugimg:
        imgio.imwrite(bugimg, get_bugimg(img, flabels, bugs))

    return is_bugged(bugs, confidence), bugs


def scan_bugtrap_parallel(fpaths, clnimgs=None, bugimgs=None, confidence=0):
    """
    Runs `scan_bugtrap` in parallel for a collection of files.

    Parameters are the same as for `scan_bugtrap`, except lists should be
    passed where they appear in plural form.

    Returns
    -------
    b: dict
        A dictionary mapping file paths in `fpaths` to the
        results of `scan_bugtrap`.
    """

    def align(x):
        return [x] * len(fpaths) if x is None else x

    clnimgs, bugimgs = map(align, [clnimgs, bugimgs])
    assert len(fpaths) == len(clnimgs) == len(bugimgs), "Must be of same length."
    b = {}
    with ProcessPoolExecutor() as executor:
        for fpath, clnimg, bugimg in zip(fpaths, clnimgs, bugimgs):
            b[fpath] = executor.submit(scan_bugtrap, fpath, clnimg, bugimg, confidence)
        for fpath in b:
            b[fpath] = b[fpath].result()
    return b


def main():
    parser = argparse.ArgumentParser(
        description="""
        Find scanner bugs and judge an image. The last line printed will be
        'True' in case the image was judged buggy, or 'False' otherwise."""
    )
    parser.add_argument("fpath", metavar="file", help="image to be checked")
    parser.add_argument(
        "--clnimg", metavar="file", default=None, help='store a "clean" image'
    )
    parser.add_argument(
        "--bugimg", metavar="file", default=None, help="store an image of bugs found"
    )
    parser.add_argument(
        "--confidence",
        metavar="C",
        type=int,
        default=0,
        help="change how the image gets judged (default 0)",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="print only the final judgement"
    )
    args = parser.parse_args()

    global verbose
    verbose = not args.quiet

    bugged, _ = scan_bugtrap(args.fpath, args.clnimg, args.bugimg, args.confidence)
    print(bugged)


if __name__ == "__main__":
    main()
