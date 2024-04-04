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


import pickle
import json
import gzip
import lzma
import pandas
from pathlib import Path
from itertools import chain
from tempfile import NamedTemporaryFile


################
# I/O utilities #
################


class ioio:
    compressors = {
        None: {
            "module": None,
            "pandas_arg": None,
        },
        ".gz": {
            "module": gzip,
            "pandas_arg": "gzip",
        },
        ".gzip": {
            "module": gzip,
            "pandas_arg": "gzip",
        },
        ".xz": {
            "module": lzma,
            "pandas_arg": "xz",
        },
        ".lzma": {
            "module": lzma,
            "pandas_arg": "xz",
        },
        ".bz2": {
            "module": None,
            "pandas_arg": "bz2",
        },
        ".zip": {
            "module": None,
            "pandas_arg": "zip",
        },
    }
    formatters = {
        "pickle": {
            "module": pickle,
            "rmode": "rb",
            "wmode": "wb",
            "rmethod": "read_pickle",
            "wmethod": "to_pickle",
            "r_extra_args": {},
            "w_extra_args": {},
        },
        "json": {
            "module": json,
            "rmode": "rt",
            "wmode": "wt",
            "rmethod": "read_json",
            "wmethod": "to_json",
            "r_extra_args": {"orient": "split", "convert_dates": False},
            "w_extra_args": {"orient": "split", "date_format": "iso"},
        },
        "hdf5": {
            "module": None,
            "rmode": "rb",
            "wmode": "wb",
            "rmethod": "read_hdf",
            "wmethod": "to_hdf",
            "r_extra_args": {"key": "singleton"},
            "w_extra_args": {"key": "singleton"},
        },
    }

    @classmethod
    def uncompressed_suffix(cls, fpath):
        try:
            return next(x for x in reversed(fpath.suffixes) if x not in cls.compressors)
        except StopIteration:
            return None

    @classmethod
    def get_format(cls, fpath, fmt=None):
        cmp = fpath.suffix if fpath.suffix in cls.compressors else None
        suffix = cls.uncompressed_suffix(fpath)
        suffix = None if suffix is None else suffix[1:]
        if fmt is None:
            fmt = suffix if suffix in cls.formatters else "json"
        else:
            if fmt in cls.formatters:
                if suffix is not None and fmt != suffix:
                    print(f"Warning: format {fmt} differs from path suffix {suffix}!")
            else:
                raise ValueError(f"Invalid format: {fmt}")
        return fmt, cmp

    @classmethod
    def load(cls, fpath, fmt=None, formatter_args={}):
        """
        Reads an object from the disk, decompressing xz and gzip files.

        Parameters
        ----------
        fpath: string
            Path to load from.
        fmt: string
            One of 'pickle' or 'json'.
            If `None`, tries to guess from extension, defaulting to 'json'.
        formatter_args: dict
            Parameters passed to reading function.

        Returns
        -------
        The object read
        """
        fpath = Path(fpath)
        fmt, cmp = cls.get_format(fpath, fmt)
        compressor = cls.compressors[cmp]["module"]
        formatter = cls.formatters[fmt]["module"]
        mode = cls.formatters[fmt]["rmode"]

        if cmp is not None and compressor is None:
            raise ValueError(f"Usupported compression: {cmp}")

        if cmp is not None and compressor is not None:
            with compressor.open(fpath, mode) as f:
                return formatter.load(f, **formatter_args)

        for fopen in lzma.open, gzip.open, open:
            try:
                with fopen(fpath, mode) as f:
                    return formatter.load(f, **formatter_args)
            except (lzma.LZMAError, gzip.BadGzipFile):
                pass

    @classmethod
    def store(cls, obj, fpath, fmt=None, formatter_args={}):
        """
        Stores an object to the disk.

        Output is compressed if file suffix is '.xz' or '.gz'

        Parameters
        ----------
        obj: object
            The object to be stored.
        fpath: string
            Path to save to.
        fmt: string
            One of 'pickle' or 'json'.
            If `None`, tries to guess from extension, defaulting to 'json'.
        formatter_args: dict
            Parameters passed to writing function.
        """
        fpath = Path(fpath)
        fmt, cmp = cls.get_format(fpath, fmt)
        compressor = cls.compressors[cmp]["module"]
        formatter = cls.formatters[fmt]["module"]
        mode = cls.formatters[fmt]["wmode"]

        if cmp is not None and compressor is None:
            raise ValueError(f"Usupported compression: {cmp}")

        fopen = compressor.open if compressor else open
        fpath.parent.mkdir(parents=True, exist_ok=True)
        with fopen(fpath, mode) as f:
            formatter.dump(obj, f, **formatter_args)

    @classmethod
    def load_pandas(cls, fpath, fmt=None, formatter_args={}, doc_as_tuple=False):
        """
        Reads a pandas object from the disk, decompressing if needed.

        Parameters
        ----------
        fpath: string
            Path to load from.
        fmt: string
            One of 'pickle' or 'json'.
            If `None`, tries to guess from extension, defaulting to 'json'.
        formatter_args: dict
            Parameters passed to reading function.
        doc_as_tuple: bool
            If fmt="json", convert anything doc-like (list[list[str]]) to tuples.

        Returns
        -------
        A pandas object, usually a Series or Dataframe
        """
        fpath = Path(fpath)
        if not fpath.exists():
            raise FileNotFoundError(fpath)
        fmt, cmp = cls.get_format(fpath)
        compression = cls.compressors[cmp]["pandas_arg"]
        method = cls.formatters[fmt]["rmethod"]
        extra_args = cls.formatters[fmt]["r_extra_args"]

        # compression in `to_hdf` seems useless, we might have used lzma on top
        if fmt == "hdf5":
            with NamedTemporaryFile() as tf:
                for fopen in lzma.open, open:
                    try:
                        with fopen(fpath, "rb") as f:
                            tf.write(f.read())
                    except lzma.LZMAError:
                        pass
                return getattr(pandas, method)(tf.name, **formatter_args)

        if compression:
            df = getattr(pandas, method)(
                fpath,
                **dict(
                    chain(
                        extra_args.items(),
                        formatter_args.items(),
                        [("compression", compression)],
                    )
                ),
            )

        else:
            for compression in "xz", "gzip", None:
                try:
                    df = getattr(pandas, method)(
                        fpath,
                        **dict(
                            chain(
                                extra_args.items(),
                                formatter_args.items(),
                                [("compression", compression)],
                            )
                        ),
                    )
                    break
                except (lzma.LZMAError, gzip.BadGzipFile):
                    pass

        # json doesn't handle tuples, so we must find and convert our tokens
        if fmt == "json" and doc_as_tuple:
            df = df.transform(
                lambda x: x.map(lambda y: tuple(map(tuple, y)), na_action="ignore")
                if all(
                    type(y) is list
                    and all(
                        type(z) is list and all(type(w) is str for w in z) for z in y
                    )
                    for y in x.loc[x.notna()]
                )
                else x
            )
        return df

    @classmethod
    def store_pandas(cls, obj, fpath, fmt=None, formatter_args={}):
        """
        Stores a pandas object to the disk.

        Parameters
        ----------
        obj: object
            The object to be stored.
        fpath: string
            Path to save to.
        fmt: string
            One of 'pickle' or 'json'.
            If `None`, tries to guess from extension, defaulting to 'json'.
        formatter_args: dict
            Parameters passed to writing function.
        """
        fpath = Path(fpath)
        fmt, cmp = cls.get_format(fpath)
        compression = cls.compressors[cmp]["pandas_arg"]
        method = cls.formatters[fmt]["wmethod"]
        extra_args = cls.formatters[fmt]["w_extra_args"]

        method_args = dict(
            chain(
                extra_args.items(),
                formatter_args.items(),
                [("compression", compression)] if fmt != "hdf5" else [],
            )
        )
        fpath.parent.mkdir(exist_ok=True)
        getattr(obj, method)(fpath, **method_args)

        # compression in `to_hdf` seems useless, so we apply it afterwards
        if fmt == "hdf5" and cls.compressors[cmp]["module"] is not None:
            with open(fpath, "rb") as f:
                data = f.read()
            with cls.compressors[cmp]["module"].open(fpath, "wb") as f:
                f.write(data)
