from lxml import etree
from dataclasses import dataclass
from collections import defaultdict
from typing import List, Set, Optional


@dataclass
class RelationType:
    id: int
    parent: Optional[int]
    name: str
    type: str
    description: str
    shortcut: str
    display: str
    pos: List[str]
    reverse: Optional[int]
    autoreverse: bool

    def format(self, x, y, short=False):
        if short or not self.display:
            return f'{x} {self.shortcut} {y}'
        else:
            return self.display.replace('<x#>', str(x)).replace('<y#>', str(y))


@dataclass
class Synset:
    id: int
    lexical_unit_ids: Set[int]
    lexical_units: list
    split: int
    definition: str
    description: str
    abstract: bool
    #workstate: str

    def __str__(self):
        lemmas = ' '.join(str(x) for x in self.lexical_units)
        return '{#'+str(self.id)+' : '+lemmas+'}'


@dataclass
class LexicalUnit:
    id: int
    synset_id: Optional[int]
    synset: list
    name: str
    pos: str
    domain: str
    description: str
    variant: int
    tag_count: int
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

        self.lexical_relations_s = defaultdict(set)
        self.lexical_relations_o = defaultdict(set)
        self.lexical_relations_p = defaultdict(set)
        self.synset_relations_s = defaultdict(set)
        self.synset_relations_o = defaultdict(set)
        self.synset_relations_p = defaultdict(set)
        self.lexical_units_by_name = defaultdict(set)

    def load(self, source):
        tree = etree.parse(source)
        root = tree.getroot()

        for e in root.iter('synsetrelations'):
            a = e.attrib
            self.synset_relations.append((int(a['parent']), int(a['relation']), int(a['child'])))

        for e in root.iter('lexicalrelations'):
            a = e.attrib
            self.lexical_relations.append((int(a['parent']), int(a['relation']), int(a['child'])))

        for e in root.iter('relationtypes'):
            a = dict(e.attrib)
            id = int(a['id'])
            parent = int(a['parent']) if 'parent' in a else None
            reverse = int(a['reverse']) if 'reverse' in a else None
            self.relation_types[id] = RelationType(
                id=id, parent=parent, type=a['type'], name=a['name'], pos=a['posstr'].split(','),
                description=a['description'], shortcut=a['shortcut'], display=a['display'],
                autoreverse=bool(a['autoreverse']), reverse=reverse)

        for e in root.iter('lexical-unit'):
            a = dict(e.attrib)
            id = int(a['id'])
            self.lexical_units[id] = LexicalUnit(
                id=id, synset_id=None, synset=None, variant=int(a['variant']), tag_count=int(a['tagcount']),
                name=a['name'], pos=a['pos'], domain=a['domain'], description=a['desc'])

        for e in root.iter('synset'):
            a = dict(e.attrib)
            id = int(a['id'])
            self.synsets[id] = Synset(
                id=id, split=int(a['split']), abstract=bool(a['abstract']),
                definition=a.get('definition', ''), description=a.get('desc', ''),
                lexical_unit_ids=[int(x.text) for x in e.findall('unit-id')],
                lexical_units=[])

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
            for unit_id in synset.lexical_unit_ids:
                self.lexical_units[unit_id].synset_id = synset.id
                self.lexical_units[unit_id].synset = synset

        for unit in self.lexical_units.values():
            self.lexical_units_by_name[unit.name].add(unit.id)
            if unit.synset_id is not None:
                self.synsets[unit.synset_id].lexical_units.append(unit)

    def lexical_relations_where(self, *, subject=None, predicate=None, object=None):
        if subject is None and predicate is None and object is None:
            raise Exception('must specify at least subject, predicate or object')
        found = set(range(len(self.lexical_relations)))
        if predicate is not None:
            id = predicate.id if isinstance(predicate, RelationType) else predicate
            found = found.intersection(self.lexical_relations_p[id])
        if subject is not None:
            id = subject.id if isinstance(subject, LexicalUnit) else subject
            found = found.intersection(self.lexical_relations_s[id])
        if object is not None:
            id = object.id if isinstance(object, LexicalUnit) else object
            found = found.intersection(self.lexical_relations_o[id])
        results = []
        for id in found:
            s, p, o = self.lexical_relations[id]
            results.append((self.lexical_units[s], self.relation_types[p], self.lexical_units[o]))
        return results

    def synset_relations_where(self, *, subject=None, predicate=None, object=None):
        if subject is None and predicate is None and object is None:
            raise Exception('must specify at least subject, predicate or object')
        found = set(range(len(self.synset_relations)))
        if predicate is not None:
            id = predicate.id if isinstance(predicate, RelationType) else predicate
            found = found.intersection(self.synset_relations_p[id])
        if subject is not None:
            id = subject.id if isinstance(subject, Synset) else subject
            found = found.intersection(self.synset_relations_s[id])
        if object is not None:
            id = object.id if isinstance(object, Synset) else object
            found = found.intersection(self.synset_relations_o[id])
        results = []
        for id in found:
            s, p, o = self.synset_relations[id]
            results.append((self.synsets[s], self.relation_types[p], self.synsets[o]))
        return results

    def lemmas(self, x: str):
        return [self.lexical_units[id] for id in self.lexical_units_by_name[x]]

    def __repr__(self):
        props = 'lexical_units synsets relation_types synset_relations lexical_relations'.split()
        res = 'PlWordnet'
        for name in props:
            disp = name.replace('_', ' ')
            prop = getattr(self, name)
            res += f'\n  {disp}: {len(prop)}'
        return res

    __str__ = __repr__


def load(source):
    wn = Wordnet() 
    wn.load(source)
    return wn

