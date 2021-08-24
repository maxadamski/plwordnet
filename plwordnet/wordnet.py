import lzma, gzip, bz2
import pickle
import gc
import re
import csv
import xml.etree.ElementTree as etree

from dataclasses import dataclass
from collections import defaultdict
from typing import List, Set, Optional


TEXT_ERRORS = re.compile(r'(brak danych|AOds|2A|\n)(; )?')

POS_MAPPING = {
    "rzeczownik": "NOUN",
    "przymiotnik": "ADJ",
    "przysłówek": "ADV",
    "czasownik": "VERB",
}

POLARITY_MAPPING = {
    '- s': -2,
    '- m': -1,
    'amb': 0,
    '+ m': 1,
    '+ s': 2,
}


@dataclass
class RelationType:
    id: int
    parent: Optional[int]
    inverse: Optional[int]
    name: str
    type: str
    description: str
    shortcut: str
    display: str
    pos: List[str]
    autoreverse: bool

    def format(self, subject, object, short=False):
        if short or not self.display:
            return f'{subject} {self.shortcut} {object}'
        elif '<x#>' in self.display and '<y#>' in self.display:
            return self.display.replace('<x#>', str(subject)).replace('<y#>', str(object))
        else:
            return f'{subject} {self.display} {object}'


@dataclass
class EmotionalAnnotation:
    __slots__ = 'polarity emotions valuations examples'.split()
    polarity: int
    emotions: List[str]
    valuations: List[str]
    examples: List[str]


@dataclass
class Synset:
    __slots__ = 'id lexical_units split definition description abstract'.split()
    id: int
    lexical_units: list
    split: int
    definition: str
    description: str
    abstract: bool
    #workstate: str

    def __str__(self):
        return '{' + ' '.join(str(x) for x in self.lexical_units) + '}'


@dataclass
class LexicalUnit:
    __slots__ = 'id synset name pos language domain description variant tag_count sentiment'.split()
    id: int
    synset: Synset
    name: str
    pos: str # NOTE: all LUs in a synset are the same part of speech
    language: str
    domain: str
    description: str
    variant: int
    tag_count: int
    sentiment: List[EmotionalAnnotation]
    #workstate: str

    def __str__(self):
        return f'{self.name}.{self.variant}'


class Wordnet:
    def __init__(self):
        self.lexical_units = {}
        self.synsets = {}
        self.relation_types = {}
        self.synset_relations = []
        self.lexical_relations = []
        self.sentiment_count = 0

        self.lexical_relations_s = defaultdict(set)
        self.lexical_relations_o = defaultdict(set)
        self.lexical_relations_p = defaultdict(set)
        self.synset_relations_s = defaultdict(set)
        self.synset_relations_o = defaultdict(set)
        self.synset_relations_p = defaultdict(set)
        self.lexical_units_by_name = defaultdict(list)
        self.relation_by_name = dict()

    def load(self, file, sentiment_file=None, *, clean=True):
        assert hasattr(file, 'read'), 'Argument `file` must be an opened PLWN .xml file'
        sentiment = defaultdict(list)

        if sentiment_file is not None:
            assert hasattr(sentiment_file, 'read'), 'Argument `sentiment_file must be an opened .csv file'
            rows = csv.reader(sentiment_file, delimiter=',', quotechar='"')
            head = next(rows)
            assert len(head) == 9, f'Expected sentiment annotation CSV to have 9 colums, but got {len(head)}'
            for lemma, variant, pos, charged, emotions, valuations, polarity, example1, example2 in rows:
                polarity = POLARITY_MAPPING.get(polarity, None)
                emotions = emotions.strip(';').split(';') if emotions != 'NULL' else []
                valuations = valuations.strip(';').split(';') if valuations != 'NULL' else []
                examples = []
                if example1 and example1 != 'NULL': examples.append(example1)
                if example2 and example2 != 'NULL': examples.append(example2)
                if not polarity and not emotions and not valuations and not examples: continue
                self.sentiment_count += 1
                sentiment[(lemma, int(variant))].append(EmotionalAnnotation(
                    polarity=polarity, emotions=emotions, valuations=valuations, examples=examples))

        root = etree.parse(file).getroot()

        for e in root.iter('synsetrelations'):
            a = e.attrib
            self.synset_relations.append((int(a['parent']), int(a['relation']), int(a['child'])))

        for e in root.iter('lexicalrelations'):
            a = e.attrib
            self.lexical_relations.append((int(a['parent']), int(a['relation']), int(a['child'])))

        for e in root.iter('relationtypes'):
            a = dict(e.attrib)
            id, name = int(a['id']), a['name']
            parent = int(a['parent']) if 'parent' in a else None
            inverse = int(a['reverse']) if 'reverse' in a else None
            self.relation_types[id] = self.relation_by_name[name] = RelationType(
                id=id, parent=parent, name=name, type=a['type'], pos=a['posstr'].split(','),
                description=a['description'], shortcut=a['shortcut'], display=a['display'],
                autoreverse=bool(a['autoreverse']), inverse=inverse)

        for e in root.iter('lexical-unit'):
            a = dict(e.attrib)
            id, variant, name, pos, lang = int(a['id']), int(a['variant']), a['name'], a['pos'], 'pl'
            if pos.endswith(' pwn'): pos, lang = pos[:-4], 'en'
            self.lexical_units[id] = LexicalUnit(
                id=id, synset=None, name=name, variant=variant, tag_count=int(a['tagcount']),
                pos=POS_MAPPING[pos], language=lang, domain=a['domain'], description=a['desc'],
                sentiment=sentiment[(name, variant)])

        for e in root.iter('synset'):
            a = dict(e.attrib)
            id = int(a['id'])
            self.synsets[id] = Synset(
                id=id, split=int(a['split']), abstract=a['abstract'] == 'true',
                definition=a.get('definition', ''), description=a.get('desc', ''),
                lexical_units=[self.lexical_units[int(x.text)] for x in e.findall('unit-id')])

        del root
        gc.collect()

        for i, x in enumerate(self.synset_relations):
            s, p, o = x
            self.synset_relations_s[s].add(i)
            self.synset_relations_o[o].add(i)
            self.synset_relations_p[p].add(i)

        for i, x in enumerate(self.lexical_relations):
            s, p, o = x
            self.lexical_relations_s[s].add(i)
            self.lexical_relations_o[o].add(i)
            self.lexical_relations_p[p].add(i)

        for synset in self.synsets.values():
            for lu in synset.lexical_units:
                self.lexical_units[lu.id].synset = synset

        for lu in self.lexical_units.values():
            self.lexical_units_by_name[lu.name].append(lu.id)

        if clean:
            self.clean()

    def clean(self):
        # remove most common bad text values
        # remove synsets with no lexical units
        for x in self.lexical_units.values():
            x.description = _cleanstr(x.description)
        empty_synsets = []
        for x in self.synsets.values():
            x.description = _cleanstr(x.description)
            x.definition = _cleanstr(x.definition)
            if not x.lexical_units:
                empty_synsets.append(x.id)
        for id in empty_synsets:
            del self.synsets[id]

    def lexical_relations_where(self, *, subject=None, predicate=None, object=None):
        if subject is None and predicate is None and object is None:
            raise Exception('must specify at least subject, predicate or object')
        found = None
        if predicate is not None:
            assert isinstance(predicate, (int, RelationType)), 'Argument `predicate` must be an int or a RelationType'
            id = predicate.id if isinstance(predicate, RelationType) else predicate
            found = _intersection(found, self.lexical_relations_p[id])
        if subject is not None:
            assert isinstance(subject, (int, LexicalUnit)), 'Argument `subject` must be an int or a LexicalUnit'
            id = subject.id if isinstance(subject, LexicalUnit) else subject
            found = _intersection(found, self.lexical_relations_s[id])
        if object is not None:
            assert isinstance(object, (int, LexicalUnit)), 'Argument `object` must be an int or a LexicalUnit'
            id = object.id if isinstance(object, LexicalUnit) else object
            found = _intersection(found, self.lexical_relations_o[id])
        results = []
        for id in found:
            s, p, o = self.lexical_relations[id]
            results.append((self.lexical_units[s], self.relation_types[p], self.lexical_units[o]))
        return results


    def synset_relations_where(self, *, subject=None, predicate=None, object=None):
        if subject is None and predicate is None and object is None:
            raise Exception('must specify at least subject, predicate or object')
        found = None
        if predicate is not None:
            assert isinstance(predicate, (int, RelationType)), 'Argument `predicate` must be an int or a RelationType'
            id = predicate.id if isinstance(predicate, RelationType) else predicate
            found = _intersection(found, self.synset_relations_p[id])
        if subject is not None:
            assert isinstance(subject, (int, Synset)), 'Argument `subject` must be an int or a Synset'
            id = subject.id if isinstance(subject, Synset) else subject
            found = _intersection(found, self.synset_relations_s[id])
        if object is not None:
            assert isinstance(object, (int, Synset)), 'Argument `object` must be an int or a Synset'
            id = object.id if isinstance(object, Synset) else object
            found = _intersection(found, self.synset_relations_o[id])
        results = []
        for id in found:
            s, p, o = self.synset_relations[id]
            results.append((self.synsets[s], self.relation_types[p], self.synsets[o]))
        return results

    def lemmas(self, x: str):
        return [self.lexical_units[id] for id in self.lexical_units_by_name[x]]

    def dump(self, dst):
        if not isinstance(dst, str):
            pickle.dump(self, dst)
        with open(dst, 'wb') as f:
            pickle.dump(self, f)

    def __repr__(self):
        props = 'lexical_units synsets relation_types synset_relations lexical_relations'.split()
        res = 'PlWordnet'
        for name in props:
            disp = name.replace('_', ' ')
            prop = getattr(self, name)
            res += f'\n  {disp}: {len(prop)}'
        res += f'\n  emotional annotations: {self.sentiment_count}'
        return res

    __str__ = __repr__


def load(wordnet_src, sentiment_src=None):
    wn_file = wordnet_src
    if isinstance(wn_file, str):
        wn_file, wordnet_src = _smartopen(wn_file, 'rb')

    if wordnet_src.endswith('.pkl'):
        if sentiment_src is not None:
            print('INFO: ignoring sentiment file, because loading from .pkl')
        wn = pickle.load(wn_file)
        wn_file.close()
        return wn

    sent_file = sentiment_src
    if isinstance(sentiment_src, str):
        sent_file, _ = _smartopen(sent_file, 'rt')

    wn = Wordnet()
    wn.load(wn_file, sent_file)
    wn_file.close()
    if sent_file is not None: sent_file.close()
    return wn


def _smartopen(src, mode):
    if src.endswith('.xz'):
        file = lzma.open(src, mode)
        src = src[:-3]
    elif src.endswith('.gz'):
        file = gzip.open(src, mode)
        src = src[:-3]
    elif src.endswith('.bz2'):
        file = bz2.open(src, mode)
        src = src[:-4]
    else:
        file = open(src, mode)
    return file, src


def _cleanstr(x):
    return re.sub(TEXT_ERRORS, '', x).strip()


def _intersection(x, y):
    if x is None: return y
    if y is None: return x
    return x.intersection(y)

