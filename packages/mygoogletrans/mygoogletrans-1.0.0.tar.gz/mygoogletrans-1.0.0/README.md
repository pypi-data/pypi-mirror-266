
A google translate api. To install it: `pip install mygoogletrans`

To use it:

```python

import gtrans
t=gtrans.GoogleTrans()
t.translate("Hello everyone","fr")
#>'Bonjour à tous'


```

Other useful actions

```python

t.translations("Hello","fr")

#> {'Bonjour!': ['Hello!',
#   'Hi!',
#   'Good morning!',
#   'Good afternoon!',
#   'How do you do?',
#   'Hallo!'],
#  'Salut!': ['Hi!', 'Hello!', 'Salute!', 'All the best!', 'Hallo!', 'Hullo!'],
#  'Tiens!': ['Hallo!', 'Hello!', 'Hullo!', 'Why!'],
#  'Allô!': ['Hello!', 'Hullo!', 'Hallo!']}

t.definitions("Hello")

#> {'Word': 'maison',
#  'Definitions': [{'gram_class': 'Substantiv',
#    'definitions': [{'definition': "Bâtiment d'habitation (immeuble, logement, résidence) ; spécialement bâtiment conçu pour un seul ou un petit nombre de foyers (pavillon, villa).",
#      'examples': ('Une maison pauvre, délabrée.',
#       "La façade, les murs, le toit d'une maison.")},
#     {'definition': "Habitation, logement (qu'il s'agisse ou non d'un bâtiment entier).",
#      'synonyms': {'': ['demeure',
#        'domicile',
#        'foyer',
#        'logis',
#        'appartement']},
#      'examples': ('Les clés de la maison.',)},
#     {'definition': "Travail, place (d'un domestique)."},
#     {'labels': ['(+ adjectif ; + de et nom)'],
#      'definition': 'Bâtiment, édifice destiné à un usage spécial.'},
#     {'definition': 'Entreprise commerciale.',
#      'synonyms': {'': ['établissement', 'firme']},
#      'examples': ('La maison mère et ses succursales.',)},
#     {'labels': ['vieux', 'au figuré'],
#      'definition': 'Famille.',
#      'examples': ('Une maison princière.',)},
#     {'labels': ['au figuré', 'Histoire'],
#      'definition': 'Ensemble des personnes employées au service des grands personnages.',
#      'examples': ('La maison du roi.',)},
#     {'labels': ['au figuré'],
# ...
#      'examples': ('Une engueulade maison.',)},
#     {'labels': ['en apposition (invariable)'],
#      'definition': 'Particulier à une entreprise.',
#      'examples': ("L'esprit maison.",)}]},
#   {'definitions': [{'examples': ('Les traditions de la maison.',)}]}]}


```
