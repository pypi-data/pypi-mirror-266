# -*- coding=utf-8 -*-
r"""

"""
import typing as t
from os import PathLike
from pathlib import Path
from ..structures import Caption
from .microdvd import write_microdvd
from .subrip import write_subrip
from .subviewer import write_subviewer
from .webvtt import write_webvtt


EXT_MAP = dict(
    sbv=write_subviewer,
    srt=write_subrip,
    sub=write_microdvd,
    vtt=write_webvtt,
)
ALIAS_MAP = dict(
    microdvd=write_microdvd,
    subrip=write_subrip,
    subviewer=write_subviewer,
    webvtt=write_webvtt,
)


def dumps(captions: t.Iterable[Caption], fp: t.Union[str, PathLike], fmt: str = None, **kwargs) -> None:
    r"""
    dumps some captions into a file

    :param captions: captions to dump
    :param fp: subtitle file to dump into
    :param fmt: specific format name
    :param kwargs: optional arguments some formats may need
    """
    fp = Path(fp)

    if fmt is None:
        fmt = fp.suffix[1:]
        writer = EXT_MAP.get(fmt.lower())
    else:
        writer = ALIAS_MAP.get(fmt.lower()) or EXT_MAP.get(fmt.lower())

    if writer is None:
        raise ValueError(f"Unknown format ({fmt!s})")

    return writer(captions, fp, **kwargs)
