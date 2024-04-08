from plover.system.english_stenotype import *



KEYS = (
    '#', '^-', '+-',
    'S-', 'T-', 'K-', 'P-', 'W-', 'H-', 'R-',
    'A-', 'O-',
    '*',
    '-E', '-U',
    '-F', '-R', '-P', '-B', '-L', '-G', '-T', '-S', '-D', '-Z',
)

SUFFIX_KEYS = ( '-D',  '-G', '-S','-DZ')

ORTHOGRAPHY_RULES = []
ORTHOGRAPHY_WORDLIST = None
ORTHOGRAPHY_RULES_ALIASES = {}


ORTHOGRAPHY_RULES = [ 
    # frite + é = frité
    (r'^(.+)e \^ (é)$', r'\1é'),
    (r'^(.+)e \^ (ée)$', r'\1ée'),
    # frite + er = friter
    (r'^(.+)e \^ (er)$', r'\1er'),
    # pourrais + s-tu = pourrais-tu
    (r'^(.+)s \^ (s-tu)$', r'\1s-tu'),
    # pense + ais = pensais bouge+ais = bougeais
    (r'^(.+[^g])e \^ (ais)$', r'\1ais'),
    # pense + ait = pensait bouge+ait = bougeait
    (r'^(.+[^g])e \^ (ait)$', r'\1ait'),
    # pense + aient = pensaient bouge+aient = bougeaient
    (r'^(.+[^g])e \^ (aient)$', r'\1aient'),

    (r'^([jc])\'(.+) \^ (nepas)$', r"\1e n'\2 pas"),
    (r'^(.+) \^ (le|la) \^ (nepas)$', r'ne \2 \1 pas'),
    # sache + ant = sachant décourage+ ant = décourageant
    (r'^(.+[^g])e \^ (ant)$', r'\1ant'),
    # brille + ante = brillante décourage+ ante = décourageante
    (r'^(.+[^g])e \^ (ante)$', r'\1ante'),
    (r'^([aoeuéèyè].+) \^ (nepas)$', r"n'\1 pas"),

    (r'^(.+) \^ (nepas)$', r'ne \1 pas'),
    (r'^(.+) \^ (lenepas)$', r'ne le \1 pas'),
    (r'^(.+) \^ (lanepas)$', r'ne la \1 pas'),
    (r'^(.+) \^ (lesnepas)$', r'ne les \1 pas'),
    (r'^j\'(.+) \^ (nemepas)$', r"je ne m'\1 pas"),
    (r'^j\'(.+) \^ (neluipas)$', r"je ne lui \1 pas"),
    (r'^(.+)\s \^ (nemepas)$', r'\1 ne me \2 pas'),
    (r'^(.+) \^ (nemepas)$', r'ne me \1 pas'),
    (r'^(.+)\s \^ (neluipas)$', r'\1 ne lui \2 pas'),
    (r'^(.+) \^ (neluipas)$', r'ne lui \1 pas'),

    (r'^([cj])\'(.+) \^ (neplus)$', r"\1e n'\2 plus"),  
    (r'^c\'(.+) \^ (neplus)$', r"ce n'\1 plus"),
    (r'^([aoeuéèyè].+) \^ (neplus)$', r" n'\1 plus"),
    (r'^(.+)\s \^ (neplus)$', r'\1 ne \2 plus'),
    (r'^(.+) \^ (neplus)$', r'ne \1 plus'),

    (r'^([cj])\'(.+) \^ (nejamais)$', r"\1e n'\2 jamais"),

    (r'^([aoeuéèyè].+) \^ (nejamais)$', r"n'\1 jamais"),
    (r'^(.+) \^ (nejamais)$', r'ne \1 jamais'),
#    (r'^(je|tu) (.+) \^ (ait)$', r'\1 \2s'),

#        (r'^(.*(?:[bcdfghjklmnprstvwxyz]|qu)[aeiou])([bcdfgklmnprtvz]) \^ ([aeiouy].*)$', r'\1\2\2\3'),#    (r'^(le|la) \^ ((?:[aeiouy])(.*))$', r'l\'\2')
]




DICTIONARIES_ROOT = 'asset:french_extended_stenotype:dictionaries'

DEFAULT_DICTIONARIES = (
    'fr_spelling.json',
    'pluvier_dicofr.json',
    'orthofr.json',
    'pluvier_verbs.json'
)
