from dataclasses import dataclass
from collections import defaultdict
from typing import List, Set, Optional


_domains = [
    {
        "id": "bhp",
        "pos": "NOUN",
        "title_en": "the highest in the hierarchy",
        "title_pl": "bez hiperonimu",
        "description_pl": "najwyższe w hierarchii",
        "description_en": None,
    },
    {
        "id": "cech",
        "pos": "NOUN",
        "title_en": "attribute",
        "title_pl": "cecha",
        "description_pl": "cechy ludzi i zwierząt",
        "description_en": None,
    },
    {
        "id": "cel",
        "pos": "NOUN",
        "title_en": "motive",
        "title_pl": "cel",
        "description_pl": "cel działania",
        "description_en": None,
    },
    {
        "id": "czas",
        "pos": "NOUN",
        "title_en": "time",
        "title_pl": "czas",
        "description_pl": "czas i stosunki czasowe",
        "description_en": None,
    },
    {
        "id": "czc",
        "pos": "NOUN",
        "title_en": "body",
        "title_pl": "część ciała",
        "description_pl": "części ciała",
        "description_en": None,
    },
    {
        "id": "czuj",
        "pos": "NOUN",
        "title_en": "emotion",
        "title_pl": "emocje",
        "description_pl": "uczucia, odczucia i emocje",
        "description_en": None,
    },
    {
        "id": "czy",
        "pos": "NOUN",
        "title_en": "act",
        "title_pl": "czynność",
        "description_pl": "czynności (nazwy)",
        "description_en": None,
    },
    {
        "id": "grp",
        "pos": "NOUN",
        "title_en": "group",
        "title_pl": "grupa",
        "description_pl": "grupy ludzi i rzeczy",
        "description_en": None,
    },
    {
        "id": "il",
        "pos": "NOUN",
        "title_en": "quantity",
        "title_pl": "ilość",
        "description_pl": "ilość, liczebność, jednoski miary",
        "description_en": None,
    },
    {
        "id": "jedz",
        "pos": "NOUN",
        "title_en": "food",
        "title_pl": "jedzenie",
        "description_pl": "jedzenie",
        "description_en": None,
    },
    {
        "id": "ksz",
        "pos": "NOUN",
        "title_en": "shape",
        "title_pl": "kształt",
        "description_pl": "kształty",
        "description_en": None,
    },
    {
        "id": "msc",
        "pos": "NOUN",
        "title_en": "location",
        "title_pl": "miejsce",
        "description_pl": "miejsca i umiejscowienie",
        "description_en": None,
    },
    {
        "id": "os",
        "pos": "NOUN",
        "title_en": "person",
        "title_pl": "osoba",
        "description_pl": "ludzie",
        "description_en": None,
    },
    {
        "id": "por",
        "pos": "NOUN",
        "title_en": "communication",
        "title_pl": "porozumiewanie się",
        "description_pl": "związane z porozumiewaniem się",
        "description_en": None,
    },
    {
        "id": "pos",
        "pos": "NOUN",
        "title_en": "possession",
        "title_pl": "posiadanie",
        "description_pl": "posiadanie i jego zmiana",
        "description_en": None,
    },
    {
        "id": "prc",
        "pos": "NOUN",
        "title_en": "process",
        "title_pl": "proces",
        "description_pl": "procesy naturalne",
        "description_en": None,
    },
    {
        "id": "rsl",
        "pos": "NOUN",
        "title_en": "plant",
        "title_pl": "roślina",
        "description_pl": "nazwy roślin",
        "description_en": None,
    },
    {
        "id": "rz",
        "pos": "NOUN",
        "title_en": "natural object",
        "title_pl": "obiekt naturalny",
        "description_pl": "obiekty naturalne",
        "description_en": None,
    },
    {
        "id": "sbst",
        "pos": "NOUN",
        "title_en": "substance",
        "title_pl": "substancja",
        "description_pl": "substancje",
        "description_en": None,
    },
    {
        "id": "st",
        "pos": "NOUN",
        "title_en": "state",
        "title_pl": "stan",
        "description_pl": "sytuacje statyczne (stany)",
        "description_en": None,
    },
    {
        "id": "sys",
        "pos": "NOUN",
        "title_en": "classification",
        "title_pl": "systematyka",
        "description_pl": "systematyka, klasyfikacja",
        "description_en": None,
    },
    {
        "id": "umy",
        "pos": "NOUN",
        "title_en": "cognition",
        "title_pl": "myślenie",
        "description_pl": "związane z myśleniem",
        "description_en": None,
    },
    {
        "id": "wytw",
        "pos": "NOUN",
        "title_en": "artefact",
        "title_pl": "wytwór",
        "description_pl": "wytwory ludzkie (nazwy)",
        "description_en": None,
    },
    {
        "id": "zdarz",
        "pos": "NOUN",
        "title_en": "event",
        "title_pl": "zdarzenie",
        "description_pl": "zdarzenia",
        "description_en": None,
    },
    {
        "id": "zj",
        "pos": "NOUN",
        "title_en": "natural phenomenon",
        "title_pl": "zjawisko naturalne",
        "description_pl": "zjawiska naturalne",
        "description_en": None,
    },
    {
        "id": "zw",
        "pos": "NOUN",
        "title_en": "animal",
        "title_pl": "zwierzę",
        "description_pl": "zwierzęta",
        "description_en": None,
    },
    {
        "id": "cczuj",
        "pos": "VERB",
        "title_en": "emotion",
        "title_pl": "odczuwanie",
        "description_pl": "czasowniki wyrażające uczucia",
        "description_en": None,
    },
    {
        "id": "cjedz",
        "pos": "VERB",
        "title_en": "consumption",
        "title_pl": "jedzenie",
        "description_pl": "czasowniki jedzenia",
        "description_en": None,
    },
    {
        "id": "cpor",
        "pos": "VERB",
        "title_en": "communication",
        "title_pl": "porozumiewanie się",
        "description_pl": "czasowniki mówienia, śpiewania itp.",
        "description_en": None,
    },
    {
        "id": "cpos",
        "pos": "VERB",
        "title_en": "possession",
        "title_pl": "posiadanie",
        "description_pl": "czasowniki posiadania i zmiany posiadania",
        "description_en": None,
    },
    {
        "id": "cst",
        "pos": "VERB",
        "title_en": "state",
        "title_pl": "stan",
        "description_pl": "czasowniki stanowe",
        "description_en": None,
    },
    {
        "id": "cumy",
        "pos": "VERB",
        "title_en": "cognition",
        "title_pl": "myślenie",
        "description_pl": "czasowniki myślenia (szeroko rozumianego)",
        "description_en": None,
    },
    {
        "id": "cwyt",
        "pos": "VERB",
        "title_en": "creation",
        "title_pl": "wytwarzanie",
        "description_pl": "czasowniki oznacz. wytwarzanie czegoś",
        "description_en": None,
    },
    {
        "id": "dtk",
        "pos": "VERB",
        "title_en": "contact",
        "title_pl": "kontakt fizyczny",
        "description_pl": "czasowniki oznacz. kontakt fizyczny (dotykanie, uderzenie, rycie itp.)",
        "description_en": None,
    },
    {
        "id": "hig",
        "pos": "VERB",
        "title_en": "body",
        "title_pl": "higiena",
        "description_pl": "pielęgnacja ciała",
        "description_en": None,
    },
    {
        "id": "pog",
        "pos": "VERB",
        "title_en": "weather",
        "title_pl": "pogoda",
        "description_pl": "czasowniki oznacz. zjawiska pogodowe",
        "description_en": None,
    },
    {
        "id": "pst",
        "pos": "VERB",
        "title_en": "perception",
        "title_pl": "postrzeganie",
        "description_pl": "czasowniki postrzegania (percepcji)",
        "description_en": None,
    },
    {
        "id": "ruch",
        "pos": "VERB",
        "title_en": "motion",
        "title_pl": "ruch",
        "description_pl": "czasowniki ruchu",
        "description_en": None,
    },
    {
        "id": "sp",
        "pos": "VERB",
        "title_en": "social",
        "title_pl": "życie społeczne",
        "description_pl": "czasowniki oznacz. wydarzenie i działania społeczne i polityczne",
        "description_en": None,
    },
    {
        "id": "wal",
        "pos": "VERB",
        "title_en": "competition",
        "title_pl": "rywalizacja",
        "description_pl": "czasowniki rywalizacji fizycznej",
        "description_en": None,
    },
    {
        "id": "zmn",
        "pos": "VERB",
        "title_en": "change",
        "title_pl": "zmiana",
        "description_pl": "zmiana wielkości, temperatury, natężenia, itp.",
        "description_en": None,
    },
    {
        "id": "grad",
        "pos": "ADJ",
        "title_en": "deadjectival",
        "title_pl": "przymiotnik odprzymiotnikowy (grad)",
        "description_pl": "przymiotniki odprzymiotnikowe (natężenie cechy)",
        "description_en": None,
    },
    {
        "id": "jak",
        "pos": "ADJ",
        "title_en": "quality",
        "title_pl": "przymiotnik jakościowy (jak)",
        "description_pl": "przymiotniki jakościowe",
        "description_en": None,
    },
    {
        "id": "odcz",
        "pos": "ADJ",
        "title_en": "deverbal",
        "title_pl": "przymiotnik odczasownikowy (odcz)",
        "description_pl": "przymiotniki odczasownikowe",
        "description_en": None,
    },
    {
        "id": "rel",
        "pos": "ADJ",
        "title_en": "relation",
        "title_pl": "przymiotnik relacyjny (rel)",
        "description_pl": "przymiotniki relacyjne (rzeczownikowe)",
        "description_en": None,
    },
    {
        "id": "zwz",
        "pos": "NOUN",
        "title_en": None,
        "title_pl": "relacja",
        "description_pl": "związek miedzy ludźmi, rzeczami lub ideami",
        "description_en": "relation",
    },
    {
        "id": "cdystr",
        "pos": "VERB",
        "title_en": None,
        "title_pl": None,
        "description_pl": "czasownki dystrybutywne",
        "description_en": "distributive verb",
    },
    {
        "id": "caku",
        "pos": "VERB",
        "title_en": None,
        "title_pl": None,
        "description_pl": "czasowniki akumulatywne",
        "description_en": "accumulative verb",
    },
    {
        "id": "cper",
        "pos": "VERB",
        "title_en": None,
        "title_pl": None,
        "description_pl": "czasowniki perduratywne",
        "description_en": "perdurative verb",
    },
    {
        "id": "cdel",
        "pos": "VERB",
        "title_en": None,
        "title_pl": None,
        "description_pl": "czasowniki delimitatywne",
        "description_en": "delimitative verb",
    },
    {
        "id": "mat",
        "pos": "ADJ",
        "title_en": None,
        "title_pl": None,
        "description_pl": "przymiotniki materiałowe",
        "description_en": "material adjective",
    },
    {
        "id": "adj",
        "pos": "ADJ",
        "title_en": None,
        "title_pl": None,
        "description_pl": "PWN: all adjective clusters",
        "description_en": "PWN: all adjective clusters",
    },
    {
        "id": "adv",
        "pos": "ADV",
        "title_en": None,
        "title_pl": None,
        "description_pl": "PWN: all adverbs",
        "description_en": "PWN: all adverbs",
    },
]


@dataclass
class Domain:
    id: str
    pos: str
    title_pl: Optional[str]
    title_en: Optional[str]
    description_pl: Optional[str]
    description_en: Optional[str]

    def __str__(self):
        return f"{self.id} ({self.pos}) — {self.title_en or self.description_en}"

    def __eq__(self, other):
        if type(other) == Domain:
            return self.id == other.id
        elif type(other) == str:
            return self.id == other
        else:
            raise TypeError(f"Cannot compare {type(other)} to <Domain>")


class DomainsDict:
    def __init__(self):
        self._domains = {}
        self.domains_by_pos = defaultdict(list)

        for d in _domains:
            domain = Domain(**d)
            self._domains[domain.id] = domain
            self.domains_by_pos[domain.pos].append(domain)

    def __getitem__(self, _id):
        return self._domains[_id]


DOMAINS = DomainsDict()


__all__ = (DomainsDict, DOMAINS, Domain)
