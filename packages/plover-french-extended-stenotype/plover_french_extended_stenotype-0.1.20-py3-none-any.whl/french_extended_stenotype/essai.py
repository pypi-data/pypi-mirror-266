#!/usr/bin/env python
from typing import *
import itertools
import functools

from plover.engine import StenoEngine
from plover.translation import Translator, Stroke, Translation
from plover.formatting import _Context, _Action, _atom_to_action, _translation_to_actions
import os


def flatten(x: List[List]) -> List:
    return list(itertools.chain.from_iterable(x))


def recursively_get_old_english(stroke: Stroke, t: Translation) -> List[str]:
    if t.strokes[-1] == stroke:
        return flatten(
            [recursively_get_old_english(stroke, subtrans)
             for subtrans in t.replaced]
        )
    else:
        return [t.english or ""]


def fr_everything(translator: Translator, stroke: Stroke, cmdline: str):
    print("\n\n\nFr everything invoked with: " + str(stroke) + ", " + cmdline)
    args = cmdline.split(",")
    all_translations = translator.get_state().translations

    # translations that _will_ be affected
    affected_strokes = all_translations[-1:][-1:]
    print("\n\n\nFr everything invoked with: " + str(affected_strokes) )
#    affected_strokes = flatten([x.strokes for x in affected_translations])

    resulting_translation = affected_strokes[-1:] + 'AEUS'
    my_trans = Translation(affected_strokes + [stroke], resulting_translation)


    translator.translate_translation(my_trans)
