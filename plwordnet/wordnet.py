import lzma, gzip, bz2
import pickle
import gc
import re
import csv
import xml.etree.ElementTree as etree

from dataclasses import dataclass
from collections import defaultdict
from typing import List, Set, Optional

from . import display as show
from .display import POS_STR


TEXT_ERRORS = re.compile(r'(brak danych|AOds|2A|\n)(; )?')


POLARITY_MAPPING = {
    '- s': -2, # negatywny silny
    '- m': -1, # negatywny mały
    'amb': 0, # ambiwalentny
    '+ m': 1, # pozytywny mały
    '+ s': 2, # pozytywny silny
}


@dataclass
class RelationType:
    id: int
    name: str
    type: str
    description: str
    shortcut: str
    display: str
    autoreverse: bool
    pos: List[str]
    parent: Optional['RelationType']
    inverse: Optional['RelationType']

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
class Description:
    __slots__ = 'qualifier definition examples links unparsed from_synset'.split()
    qualifier: str
    definition: str
    examples: list
    links: list
    unparsed: str
    from_synset: bool


@dataclass
class Synset:
    __slots__ = 'id lexical_units split definition description abstract'.split()
    id: int
    definition: str
    split: int
    abstract: bool
    description: str
    lexical_units: List['LexicalUnit']
    #workstate: str

    def __str__(self, max_items=None):
        lus = self.lexical_units
        rest = ''
        if max_items is not None:
            lus = lus[:max_items]
            if max_items < len(self.lexical_units):
                rest = ' ...'
        return '{' + ' '.join(str(x) for x in lus) + rest + '}'


@dataclass
class LexicalUnit:
    __slots__ = 'id synset name pos_pl pos language domain description rich_description variant tag_count sentiment'.split()
    id: int
    name: str
    variant: int
    pos_pl: str # NOTE: all LUs in a synset are the same part of speech
    pos: str
    language: str
    domain: str
    tag_count: int
    description: str
    rich_description: Optional[Description]
    sentiment: List[EmotionalAnnotation]
    synset: Synset
    #workstate: str

    def __str__(self):
        return f'{self.name}.{self.variant}'

    def _repr_html_(self):
        return show.lexical_unit_html(self)


class Wordnet:
    def __init__(self):
        self.lexical_units = {}
        self.synsets = {}
        self.relation_types = {}
        self.synset_relations = []
        self.lexical_relations = []
        self.sentiment_count = 0
        self.description_count = 0
        self.description_errors = 0

        self.lexical_relations_s = defaultdict(set)
        self.lexical_relations_o = defaultdict(set)
        self.lexical_relations_p = defaultdict(set)
        self.synset_relations_s = defaultdict(set)
        self.synset_relations_o = defaultdict(set)
        self.synset_relations_p = defaultdict(set)
        self.lexical_units_by_name = defaultdict(list)
        self.relation_by_name = dict()

    def load(self, file, sentiment_file=None, *, clean=True, full_parse=False):
        assert hasattr(file, 'read'), 'Argument `file` must be an opened PLWN .xml file'
        sentiment = defaultdict(list)

        if sentiment_file is not None:
            assert hasattr(sentiment_file, 'read'), 'Argument `sentiment_file must be an opened .csv file'
            rows = csv.reader(sentiment_file, delimiter=',', quotechar='"')
            head = next(rows)
            assert len(head) == 9, f'Expected sentiment annotation CSV to have 9 colums, but got {len(head)}'
            for lemma, variant, pos, charged, emotions, valuations, polarity, example1, example2 in rows:
                polarity = POLARITY_MAPPING.get(polarity, None)
                emotions = emotions.strip(';').split(';') if emotions and emotions != 'NULL' else []
                valuations = valuations.strip(';').split(';') if valuations and valuations != 'NULL' else []
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
                autoreverse=a['autoreverse'] == 'true', inverse=inverse)

        for e in root.iter('lexical-unit'):
            a = dict(e.attrib)
            id, variant, name, pos, lang = int(a['id']), int(a['variant']), a['name'], a['pos'], 'pl'
            if pos.endswith(' pwn'): lang = 'en'
            self.lexical_units[id] = LexicalUnit(
                id=id, synset=None, name=name, variant=variant, tag_count=int(a['tagcount']),
                pos_pl=pos, pos=POS_STR[pos], language=lang, domain=a['domain'], description=a['desc'],
                sentiment=sentiment[(name, variant)], rich_description=None)

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
            self.lexical_units_by_name[lu.name.lower()].append(lu.id)

        for rel in self.relation_types.values():
            if rel.parent is not None:
                rel.parent = self.relation_types[rel.parent]
            if rel.inverse is not None:
                rel.inverse = self.relation_types[rel.inverse]

        # For cases like Instance_Hypernym/Instance_Hyponym
        for rel in self.relation_types.values():
            if rel.inverse is not None and rel.inverse.inverse is None:
                rel.inverse.inverse = rel

        if clean: self.clean()
        if full_parse: self.parse_descriptions()

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

    def parse_descriptions(self):
        for lu in self.lexical_units.values():
            if not lu.description:
                error, descr = _synset_rich_description(lu.synset)
                if descr is None: continue
                descr.from_synset = True
                lu.rich_description = descr
            else:
                error, lu.rich_description = parse_description(lu.description)
                self.description_count += 1
                if not error: continue
                error, descr = _synset_rich_description(lu.synset)
                if error: self.description_errors += 1
                if descr is None or error: continue
                descr.from_synset = True
                lu.rich_description = descr

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

    def show_relations(self, obj):
        res = ''
        if isinstance(obj, LexicalUnit):
            res += 'LEXICAL RELATIONS\n'
            res += show.lexical_relations(self, obj)
            res += '\nSYNSET RELATIONS\n'
            res += show.synset_relations(self, obj.synset)
        if isinstance(obj, Synset):
            res += 'SYNSET RELATIONS\n'
            res += show.synset_relations(self, obj)
        return res

    def find(self, x: str):
        name, variant = x, None
        parts = name.rsplit('.', 1)
        if len(parts) == 2:
            name, variant = parts[0], int(parts[1])
        lus = [self.lexical_units[id] for id in self.lexical_units_by_name[name.lower()]]
        if variant is None:
            return lus
        lus = [lu for lu in lus if lu.variant == variant]
        return lus[0] if lus else None

    def _get_hypernym_relations(self, interlingual=False):
        assert self.relation_by_name, 'You should load the file first'

        hypernym_rels = [
            self.relation_by_name['hiperonimia'],
            self.relation_by_name['egzemplarz'],
            self.relation_by_name['Hypernym'],
            self.relation_by_name['Instance_Hypernym'],
        ]

        interlingual_hypernym_rels = [
            self.relation_by_name['hiperonimia_międzyjęzykowa'],
            self.relation_by_name['Hiper_plWN-PWN'],
            self.relation_by_name['Hiper_PWN-plWN'],
        ]

        if not interlingual:
            return hypernym_rels
        else:
            return hypernym_rels + interlingual_hypernym_rels

    def _get_hyponym_relations(self, interlingual=False):
        return [rel.inverse for rel in self._get_hypernym_relations(interlingual) if rel]

    def hypernyms(self, synset, interlingual=False):
        assert synset is not None
        res = []
        for rel in self._get_hypernym_relations(interlingual):
            for s, _, _ in self.synset_relations_where(predicate=rel, object=synset):
                res.append(s)

        return res

    def hyponyms(self, synset, interlingual=False):
        assert synset is not None
        res = []
        for rel in self._get_hyponym_relations(interlingual):
            for s, _, _ in self.synset_relations_where(predicate=rel, object=synset):
                res.append(s)

        return res

    def hypernym_paths(self, synset, full_search=False, interlingual=False, seen=None):
        # TODO: should we rename full_search to greedy and negate the condition below?
        # None at the end of the path means that we ran into the loop while searching for the hyperonym

        if seen is None:
            seen = [synset.id]
        else:
            seen = seen.copy()
            seen.append(synset.id)

        res = []
        for hypernym in self.hypernyms(synset=synset, interlingual=interlingual):
            if hypernym.id in seen:
                res.append([None])
                continue

            paths = self.hypernym_paths(synset=hypernym, full_search=full_search, interlingual=interlingual, seen=seen)
            for path in paths:
                res.append([hypernym] + path)

            if not paths:
                res.append([hypernym])

            if not full_search:
                break

        return res

    def dump(self, dst):
        if not isinstance(dst, str):
            pickle.dump(self, dst)
        with open(dst, 'wb') as f:
            pickle.dump(self, f)

    def __repr__(self):
        props = 'lexical_units synsets relation_types synset_relations lexical_relations'.split()
        res = 'Słowosieć'
        for name in props:
            disp = name.replace('_', ' ')
            prop = getattr(self, name)
            res += f'\n  {disp}: {len(prop)}'
        res += f'\n  emotional annotations: {self.sentiment_count}'
        res += f'\n  rich descriptions: {self.description_count}'
        if self.description_errors:
            res += f'\n  malformed descriptions: {self.description_errors}'
        return res

    __str__ = __repr__


def load(wordnet_src, sentiment_src=None, **kwargs):
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
    wn.load(wn_file, sent_file, **kwargs)
    wn_file.close()
    if sent_file is not None: sent_file.close()
    return wn


def _smartopen(src, mode):
    if src.endswith('.xz'):
        file = lzma.open(src, mode)
        src = src[:-3]
    if src.endswith('.bz2'):
        file = bz2.open(src, 'rb')
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


def _synset_rich_description(synset):
    if synset.definition:
        error, descr = parse_description(synset.definition)
        if not error: return error, descr
    if synset.description:
        error, descr = parse_description(synset.description)
        if not error: return error, descr
    return False, None


def parse_description(text):
    res, examples, links, unparsed = dict(), [], [], []
    i, n, error = 0, len(text), False
    while i < n:
        char = text[i]
        if char == '#' and i+2 < n and text[i+2] == 'A':
            # TODO(max): merge emotional annotations
            i += 6
            while i < n and text[i] != '{': i += 1
            while i < n and text[i] != '}': i += 1
            while i < n and text[i] != '[': i += 1
            while i < n and text[i] != ']': i += 1
            while i < n and text[i] == ' ': i += 1
            while i < n and text[i] != '[': i += 1
            while i < n and text[i] != ']': i += 1
            i += 1
        elif char == '<':
            # TODO(max): find out what these tags do
            j = text.find('>', i)
            if j == -1: j = n
            i = j + 1
        elif char == '#' and i+2 < n:
            marker = text[i+2]
            i += 4
            chars = []
            while i < n and text[i] not in '[{#':
                chars.append(text[i])
                i += 1
            res[marker] = ''.join(chars).strip(': ')
        elif char == '[' and text[i:i+3] == '[##':
            i += 5
            j = text.find(']', i)
            if j == -1: j = n
            examples.append(text[i:j].strip(': '))
            i = j + 1
        elif char == '{' and text[i:i+3] == '{##':
            i += 5
            j = text.find('}', i)
            if j == -1: j = n
            links.append(text[i:j].strip())
            i = j + 1
        elif text[i:i+2] == 'NP':
            i += 2
        else:
            unparsed.append(text[i])
            i += 1
            if char != ' ':
                error = True
    return error, Description(qualifier=res.get('K', None), definition=res.get('D', ''),
                       examples=examples, links=links, unparsed=''.join(unparsed),from_synset=False)

