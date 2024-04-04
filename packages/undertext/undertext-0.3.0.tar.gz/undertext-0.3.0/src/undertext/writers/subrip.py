# -*- coding=utf-8 -*-
r"""

"""
import io
import typing as t
from os import PathLike
from ..structures import Caption
from ..util import format_ts_comma as format_ts


def write_subrip(captions: t.Iterable[Caption], filename: t.Union[str, PathLike, t.TextIO]) -> None:
    stream = io.StringIO()

    for i, caption in enumerate(captions):
        if i != 0:
            stream.write("\r\n")

        stream.write(f"{i+1}\r\n")
        stream.write(f"{format_ts(caption.start)} --> {format_ts(caption.end)}\r\n")
        for line in caption.lines:
            stream.write(f"{line}\r\n")

    if isinstance(filename, (str, PathLike)):
        with open(filename, 'w') as file:
            file.write(stream.getvalue())
    else:
        filename.write(stream.getvalue())
