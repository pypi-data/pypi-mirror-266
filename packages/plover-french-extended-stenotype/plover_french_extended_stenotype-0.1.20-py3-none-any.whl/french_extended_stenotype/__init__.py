#!/usr/bin/env python
from typing import *
import itertools
import functools

from plover.engine import StenoEngine
from plover.translation import Translator, Stroke, Translation
from plover.formatting import _Context, _Action, _atom_to_action, _translation_to_actions
import os


def transform(last_word):
    if last_word.endswith('ais'):
        return last_word[:-3] + 'ait'
    if last_word.endswith('ait'):
        return last_word[:-3] + 'ai'
    if last_word.endswith('ai'):
        return last_word[:-2] + 'aient'
    if last_word.endswith('aient'):
        return last_word[:-5] + 'ais'
    return None

    
def retro_transform(ctx, cmdline):
    action = ctx.copy_last_action()

    last_word = ctx.last_words(1)[0]
    if transform(last_word)==None: 
         return action
    print("\n\n\nFr Everything myinvoked with: " + repr(action.rtfcre[0]))
#    last_word[-1:]=    'AEUS'
    action.prev_replace = last_word
    action.text = transform(last_word)
    action.word = None
    action.prev_attach = True

    return action
def fr_change_suffixes(*args, **kwargs):
    return retro_transform(*args, **kwargs)
