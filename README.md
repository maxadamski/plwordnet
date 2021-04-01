# Polish Wordnet Python library

Simple, easy-to-use and reasonably fast library for using the [Słowosieć](http://nlp.pwr.wroc.pl/plwordnet/download/) (also known as PlWordNet) - a lexico-semantic database of the Polish language. PlWordNet can also be browsed [here](http://plwordnet.pwr.wroc.pl/wordnet/).

I created this library, because since version 2.9, PlWordNet cannot be easily loaded into Python (for example with `nltk`), as it is only provided in a custom `plwnxml` format.


## Usage

Load wordnet from an XML file (this will take about 20 seconds), and print basic statistics.

```python
import plwordnet
wn = plwordnet.load('plwordnet_4_2.xml')
print(wn)
```

Expected output:

```
PlWordnet
  lexical units: 513410
  synsets: 353586
  relation types: 306
  synset relations: 1477849
  lexical relations: 393137
```

Find lexical units with name `leśny` and print all relations, where where that unit is in the subject/parent position.

```python
for lu in wn.lemmas('leśny'):
    for s, p, o in wn.lexical_relations_where(subject=lu):
        print(p.format(s, o))
```

Expected output:

```
leśny.2 tworzy kolokację z polana.1
leśny.2 jest synonimem mpar. do las.1
leśny.3 przypomina las.1
leśny.4 jest derywatem od las.1
leśny.5 jest derywatem od las.1
leśny.6 przypomina las.1
```

Print all relation types and their ids:

```python
for id, rel in wn.relation_types.items():
    print(id, rel.name)
```

Expected output:

```
10 hiponimia
11 hiperonimia
12 antonimia
13 konwersja
...
```


## Installation

Note: `plwordnet` requires at Python 3.7 or newer.

```
pip install plwordnet
```


## Version support

This library should be able to read future versions of PlWordNet without modification, even if more relation types are added. Still, if you use this library with a version of PlWordNet that is not listed below, please consider contributing information if it is supported.

- [x] PlWordNet 4.2
- [x] PlWordNet 4.0
- [x] PlWordNet 3.2
- [x] PlWordNet 3.0
- [x] PlWordNet 2.3
- [x] PlWordNet 2.2
- [x] PlWordNet 2.1


## Documentation

See `plwordnet/wordnet.py` for `RelationType`, `Synset` and `LexicalUnit` class definitions.

### Package functions

- `load(source)`: Reads PlWordNet, where `src` is a path to the wordnet XML file, or a path to the pickled wordnet object. Passed paths can point to files compressed with gzip or lzma.

### `Wordnet` instance properties

- `lexical_relations`: List of (subject, predicate, object) triples
- `synset_relations`: List of (subject, predicate, object) triples
- `relation_types`: Mapping from relation type id to object
- `lexical_units`: Mapping from lexical unit id to unit object
- `synsets`: Mapping from synset id to object
- `(lexical|synset)_relations_(s|o|p)`: Mapping from id of subject/object/predicate to a set of matching lexical unit/synset relation ids
- `lexical_units_by_name`: Mapping from lexical unit name to a set of matching lexical unit ids

### `Wordnet` methods

- `lemmas(value)`: Returns a list of `LexicalUnit`, where the name is equal to `value`
- `lexical_relations_where(subject, predicate, object)`: Returns lexical relation triples, with matching subject or/and predicate or/and object. Subject, predicate and object arguments can be integer ids or `LexicalUnit` and `RelationType` objects.
- `synset_relations_where(subject, predicate, object)`: Returns synset relation triples, with matching subject or/and predicate or/and object. Subject, predicate and object arguments can be integer ids or `Synset` and `RelationType` objects.
- `dump(dst)`: Pickles the `Wordnet` object to opened file `dst` or to a new file with path `dst`.

### `RelationType` methods

- `format(x, y, short=False)`: Substitutes `x` and `y` into the `RelationType` display format `display`. If `short`, `x` and `y` are separated by the short relation name `shortcut`.

