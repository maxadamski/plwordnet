from lxml import etree
from dataclasses import dataclass
from typing import List, Optional


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


@dataclass
class Synset:
    id: int
    lexical_units: List[int]
    split: int
    definition: str
    description: str
    abstract: bool
    #workstate: str


@dataclass
class LexicalUnit:
    id: int
    name: str
    pos: str
    domain: str
    description: str
    variant: int
    tag_count: int
    #workstate: str

    
class Wordnet:
    def __init__(self):
        self.lexical_units = {}
        self.synsets = {}
        self.relation_types = {}
        self.synset_relations = []
        self.lexical_relations = []
        
        self.lexical_relations_s = {}
        self.lexical_relations_o = {}
        self.synset_relations_s = {}
        self.synset_relations_o = {}

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
                id=id, parent=parent, type=a['type'], name=a['name'],
                description=a['description'], shortcut=a['shortcut'], display=a['display'],
                pos=a['posstr'].split(','), reverse=reverse, autoreverse=bool(a['autoreverse']),
            )
            
        for e in root.iter('lexical-unit'):
            a = dict(e.attrib)
            id = int(a['id'])
            self.lexical_units[id] = LexicalUnit(
                id=id, name=a['name'], pos=a['pos'], domain=a['domain'], description=a['desc'],
                variant=int(a['variant']), tag_count=int(a['tagcount']),
            )
            
        for e in root.iter('synset'):
            a = dict(e.attrib)
            id = int(a['id'])
            self.synsets[id] = Synset(
                id=id, split=int(a['split']), abstract=bool(a['abstract']),
                definition=a.get('definition', ''), description=a.get('desc', ''),
                lexical_units=[x.text for x in e.findall('unit-id')],
            )
            
        del tree

    def index(self):
        for i, x in enumerate(self.synset_relations):
            s, _, o = x
            if s not in self.synset_relations_s: self.synset_relations_s[s] = []
            if o not in self.synset_relations_o: self.synset_relations_o[o] = []
            self.synset_relations_s[s].append(i)
            self.synset_relations_o[o].append(i)
            
        for i, x in enumerate(self.lexical_relations):
            s, _, o = x
            if s not in self.lexical_relations_s: self.lexical_relations_s[s] = []
            if o not in self.lexical_relations_o: self.lexical_relations_o[o] = []
            self.lexical_relations_s[s].append(i)
            self.lexical_relations_o[o].append(i)


def load(source, index=True):
    wn = Wordnet() 
    wn.load(source)
    if index:
        wn.index()
    return wn

