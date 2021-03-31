# Polish Wordnet Python library

Simple, easy-to-use and reasonably fast library for using the [Słowosieć](http://nlp.pwr.wroc.pl/plwordnet/download/) - a lexico-semantic database of the Polish language.

I created this library, because since version 2.9, Słowosieć cannot be easily loaded into Python (for example with `nltk`), as it is only provided in a custom `plwnxml` format.


## Usage

```python
import plwordnet
wn = plwordnet.load('plwordnet_4_2.xml')
# access data:
# wn.lexical_relations
# wn.lexical_units
# wn.synset_relations
# wn.synsets
# wn.relation_types
# wn.relation_types
```


## Installation

Note: `plwordnet` requires at Python 3.7 or newer.

```
pip install plwordnet
```


## Supported versions

This library should be able to read future versions of Słowosieć without modification, even if more relation types are added. Still, if you use this library with a version of Słowosieć that is not listed below, please consider contributing information if it is supported.

- Słowosieć 4.2 - YES (requires manually correcting the XML file)
	- Simple XML syntax errors
	- Typo in one attribute key
	- Typo in one `id` attribute
- Słowosieć 3.0 - YES

