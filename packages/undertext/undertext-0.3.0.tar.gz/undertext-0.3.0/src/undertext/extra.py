# -*- coding=utf-8 -*-
r"""

"""
import typing as t
from .structures import Caption
from .util import html_cleanup


__all__ = ['clean_captions']


def clean_captions(captions: t.Iterable[Caption]) -> t.List[Caption]:
    r"""
    removed html tags from captions
    """
    return [
        caption.with_text(html_cleanup(caption.text))
        for caption in captions
    ]
