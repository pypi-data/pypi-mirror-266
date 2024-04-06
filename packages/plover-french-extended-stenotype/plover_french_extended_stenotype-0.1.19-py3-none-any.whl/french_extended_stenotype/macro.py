#!/usr/bin/env python
from typing import *
import itertools
import functools
from plover.oslayer.config import PLATFORM
import json
from plover.engine import StenoEngine
from plover.formatting import RetroFormatter
from plover.translation import Translator, Stroke, Translation
from plover.formatting import _Context, _Action, _atom_to_action, _translation_to_actions
import os


def flatten(x: List[List]) -> List:
    return list(itertools.chain.from_iterable(x))


def fr_suffixes(translator: Translator, stroke: Stroke, args: str) -> None:
    '''
    :param translator: The active Plover translator that is executing the macro.
    :param stroke: The current stroke (what invoked this macro).
    :param args: The optional arguments specified to the macro as a comma-delimited string.
                 Piece 1: The number of previous translations to repeat. Default is 1.
    '''

    # Get the current state
    translations = translator.get_state().translations
    if not translations:
        return


    num_to_repeat = 1

    # Output the new translations

    all_translations = translator.get_state().translations
    affected_translation_cnt = len(list(
        itertools.takewhile(
            lambda x: x.strokes[-1] == stroke,
            reversed(all_translations)
        )
    ))

    # translations that _will_ be affected
    affected_translations = all_translations[-(affected_translation_cnt + 1):]
    #affected_translations = all_translations[-1:] 
    flatten_strokes = flatten([x.strokes for x in affected_translations])
    affected_strokes = [x.strokes for x in translations[-num_to_repeat:]]

    print("\n\n\nFr Everything translation stroke: ")
    print(flatten_strokes)
    formatter = RetroFormatter(translations)
    last_words = formatter.last_words(num_to_repeat)
    print("\n\n\nFr Last word: " + repr(last_words))


    __location__ = os.path.realpath( os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f =open(os.path.join(__location__, 'dup.json') )
    data = json.load(f)

    str_stroke=[]
    for strokess in affected_strokes:
        for stroke in strokess:
            print("\n\n\nFr Last word: " + repr(stroke.rtfcre))
            str_stroke.append(stroke.rtfcre)


    stroketofind='/'.join(str_stroke)
    print("\n\n\nFr stroke to find: " + repr(stroketofind))
    print("\n\n\nFr affected translation: " + repr(affected_translations))
    
    print("\n\n\nFr affected strokes: " + repr(affected_strokes))

    if (stroketofind not in data):
        return None

    next = False
    for word in data[stroketofind] :
        if next:
            my_trans = Translation(affected_strokes[0], word)
            my_trans.replaced = affected_translations
            return translator.translate_translation(my_trans)

        if word==last_words[0]:
            next=True
    my_trans = Translation(affected_strokes[0], data[stroketofind][0])
    my_trans.replaced = affected_translations
    translator.translate_translation(my_trans)

