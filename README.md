# Polish Wordnet Python library

Simple, easy-to-use and reasonably fast library for using the [Słowosieć](http://nlp.pwr.wroc.pl/plwordnet/download/) - a lexico-semantic database of the Polish language.

I created this library, because since version 2.9, Słowosieć cannot be easily loaded into Python (for example with `nltk`), as it is only provided in a custom `plwnxml` format.


## Usage

Load wordnet from an `XML` file (this will take about 20 seconds), and print basic statistics.

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

This library should be able to read future versions of Słowosieć without modification, even if more relation types are added. Still, if you use this library with a version of Słowosieć that is not listed below, please consider contributing information if it is supported.

- Słowosieć 4.2 - YES (requires manually correcting the XML file)
	- Simple XML syntax errors
	- Typo in one attribute key
	- Typo in one `id` attribute
- Słowosieć 3.2 - YES
- Słowosieć 3.0 - YES


## Documentation

See `plwordnet/wordnet.py` for `RelationType`, `Synset` and `LexicalUnit` class definitions.

### `Wordnet` instance properties

- `lexical_relations`: list of (subject, predicate, object) triples
- `synset_relations`: list of (subject, predicate, object) triples
- `relation_types`: mapping from relation type id to object
- `lexical_units`: mapping from lexical unit id to unit object
- `synsets`: mapping from synset id to object
- `(lexical|synset)_relations_(s|o|p)`: mapping from id of subject/object/predicate to a set of matching lexical unit/synset relation ids
- `lexical_units_by_name`: mapping from lexical unit name to a set of matching lexical unit ids

### `Wordnet` methods

- `lemmas(value)`: returns a list of `LexicalUnit`, where the name is equal to `value`
- `load(source)`: reads and indexes Wordnet, where `source` is a path to the wordnet XML file, or a file object opened in binary mode (useful for loading compressed XML files)
- `lexical_relations_where(subject, predicate, object)`: returns lexical relation triples, with matching subject or/and predicate or/and object. Subject, predicate and object arguments can be integer ids or `LexicalUnit` and `RelationType` objects.
- `synset_relations_where(subject, predicate, object)`: returns synset relation triples, with matching subject or/and predicate or/and object. Subject, predicate and object arguments can be integer ids or `Synset` and `RelationType` objects.

### `RelationType` methods

- `format(x, y, short=False)`: substitutes `x` and `y` into the `RelationType` display format `display`. If `short`, `x` and `y` are separated by the short relation name `shortcut`.

