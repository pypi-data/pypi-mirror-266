# -*- coding=utf-8 -*-
r"""

"""
import io
import typing as t
from os import PathLike
from ..structures import Caption
from ..util import format_ts_dot as format_ts


def write_subviewer(captions: t.Iterable[Caption], filename: t.Union[str, PathLike, t.TextIO]) -> None:
    r"""
    writes as SubViewer 2.0
    https://wiki.videolan.org/SubViewer/
    """
    stream = io.StringIO()

    for i, caption in enumerate(captions):
        if i != 0:
            stream.write("\r\n")

        stream.write(f"{format_ts(caption.start)},{format_ts(caption.end)}\r\n")
        text = caption.text.replace('\n', '[br]')
        stream.write(f"{text}\r\n")

    if isinstance(filename, (str, PathLike)):
        with open(filename, 'w') as file:
            file.write(stream.getvalue())
    else:
        filename.write(stream.getvalue())
