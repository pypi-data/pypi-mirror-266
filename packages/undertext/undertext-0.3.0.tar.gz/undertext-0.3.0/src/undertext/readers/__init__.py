# -*- coding=utf-8 -*-
r"""

"""
import typing as t
from os import PathLike
from pathlib import Path
from ..structures import Caption
from .microdvd import read_microdvd
from .subrip import read_subrip
from .subviewer import read_subviewer
from .webvtt import read_webvtt


EXT_MAP = dict(
    sbv=read_subviewer,
    srt=read_subrip,
    sub=read_microdvd,
    vtt=read_webvtt,
)
ALIAS_MAP = dict(
    microdvd=read_microdvd,
    subrip=read_subrip,
    subviewer=read_subviewer,
    webvtt=read_webvtt,
)


def loads(fp: t.Union[str, PathLike], fmt: str = None, **kwargs) -> t.List[Caption]:
    r"""
    load the captions from a file

    :param fp: subtitle file to load
    :param fmt: specific format name
    :param kwargs: optional arguments some formats may need
    :return: Caption[]
    """
    fp = Path(fp)

    if fmt is None:
        fmt = fp.suffix[1:]
        reader = EXT_MAP.get(fmt.lower())
    else:
        reader = ALIAS_MAP.get(fmt.lower()) or EXT_MAP.get(fmt.lower())

    if reader is None:
        raise ValueError(f"Unknown format ({fmt!s})")

    return reader(fp, **kwargs)
