
import sys
import json
import re


def retro_transforme(ctx, cmdline, transform):
    action = ctx.copy_last_action()

    num_words = int(cmdline)

    last_words = "".join(ctx.last_words(count = num_words))
    action.prev_replace = last_words
    action.text = transform(last_words)
    action.word = None
    action.prev_attach = True

    return action



def retro_dupper(*args, **kwargs):
    return retro_transform(*args, **kwargs, transform = lambda x: x.upper())
