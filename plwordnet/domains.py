from dataclasses import dataclass
from collections import defaultdict
from typing import List, Set, Optional


_domains = [
    {
        "id": "bhp",
        "pos": "NOUN",
        "name_en": "the highest in the hierarchy",
        "name_pl": "bez hiperonimu",
        "description_pl": "najwyższe w hierarchii",
    },
    {
        "id": "cech",
        "pos": "NOUN",
        "name_en": "attribute",
        "name_pl": "cecha",
        "description_pl": "cechy ludzi i zwierząt",
    },
    {
        "id": "cel",
        "pos": "NOUN",
        "name_en": "motive",
        "name_pl": "cel",
        "description_pl": "cel działania",
    },
    {
        "id": "czas",
        "pos": "NOUN",
        "name_en": "time",
        "name_pl": "czas",
        "description_pl": "czas i stosunki czasowe",
    },
    {
        "id": "czc",
        "pos": "NOUN",
        "name_en": "body",
        "name_pl": "część ciała",
        "description_pl": "części ciała",
    },
    {
        "id": "czuj",
        "pos": "NOUN",
        "name_en": "emotion",
        "name_pl": "emocje",
        "description_pl": "uczucia, odczucia i emocje",
    },
    {
        "id": "czy",
        "pos": "NOUN",
        "name_en": "act",
        "name_pl": "czynność",
        "description_pl": "czynności (nazwy)",
    },
    {
        "id": "grp",
        "pos": "NOUN",
        "name_en": "group",
        "name_pl": "grupa",
        "description_pl": "grupy ludzi i rzeczy",
    },
    {
        "id": "il",
        "pos": "NOUN",
        "name_en": "quantity",
        "name_pl": "ilość",
        "description_pl": "ilość, liczebność, jednoski miary",
    },
    {
        "id": "jedz",
        "pos": "NOUN",
        "name_en": "food",
        "name_pl": "jedzenie",
        "description_pl": "jedzenie",
    },
    {
        "id": "ksz",
        "pos": "NOUN",
        "name_en": "shape",
        "name_pl": "kształt",
        "description_pl": "kształty",
    },
    {
        "id": "msc",
        "pos": "NOUN",
        "name_en": "location",
        "name_pl": "miejsce",
        "description_pl": "miejsca i umiejscowienie",
    },
    {
        "id": "os",
        "pos": "NOUN",
        "name_en": "person",
        "name_pl": "osoba",
        "description_pl": "ludzie",
    },
    {
        "id": "por",
        "pos": "NOUN",
        "name_en": "communication",
        "name_pl": "porozumiewanie się",
        "description_pl": "związane z porozumiewaniem się",
    },
    {
        "id": "pos",
        "pos": "NOUN",
        "name_en": "possession",
        "name_pl": "posiadanie",
        "description_pl": "posiadanie i jego zmiana",
    },
    {
        "id": "prc",
        "pos": "NOUN",
        "name_en": "process",
        "name_pl": "proces",
        "description_pl": "procesy naturalne",
    },
    {
        "id": "rsl",
        "pos": "NOUN",
        "name_en": "plant",
        "name_pl": "roślina",
        "description_pl": "nazwy roślin",
    },
    {
        "id": "rz",
        "pos": "NOUN",
        "name_en": "natural object",
        "name_pl": "obiekt naturalny",
        "description_pl": "obiekty naturalne",
    },
    {
        "id": "sbst",
        "pos": "NOUN",
        "name_en": "substance",
        "name_pl": "substancja",
        "description_pl": "substancje",
    },
    {
        "id": "st",
        "pos": "NOUN",
        "name_en": "state",
        "name_pl": "stan",
        "description_pl": "sytuacje statyczne (stany)",
    },
    {
        "id": "sys",
        "pos": "NOUN",
        "name_en": "classification",
        "name_pl": "systematyka",
        "description_pl": "systematyka, klasyfikacja",
    },
    {
        "id": "umy",
        "pos": "NOUN",
        "name_en": "cognition",
        "name_pl": "myślenie",
        "description_pl": "związane z myśleniem",
    },
    {
        "id": "wytw",
        "pos": "NOUN",
        "name_en": "artefact",
        "name_pl": "wytwór",
        "description_pl": "wytwory ludzkie (nazwy)",
    },
    {
        "id": "zdarz",
        "pos": "NOUN",
        "name_en": "event",
        "name_pl": "zdarzenie",
        "description_pl": "zdarzenia",
    },
    {
        "id": "zj",
        "pos": "NOUN",
        "name_en": "natural phenomenon",
        "name_pl": "zjawisko naturalne",
        "description_pl": "zjawiska naturalne",
    },
    {
        "id": "zw",
        "pos": "NOUN",
        "name_en": "animal",
        "name_pl": "zwierzę",
        "description_pl": "zwierzęta",
    },
    {
        "id": "cczuj",
        "pos": "VERB",
        "name_en": "emotion",
        "name_pl": "odczuwanie",
        "description_pl": "czasowniki wyrażające uczucia",
    },
    {
        "id": "cjedz",
        "pos": "VERB",
        "name_en": "consumption",
        "name_pl": "jedzenie",
        "description_pl": "czasowniki jedzenia",
    },
    {
        "id": "cpor",
        "pos": "VERB",
        "name_en": "communication",
        "name_pl": "porozumiewanie się",
        "description_pl": "czasowniki mówienia, śpiewania itp.",
    },
    {
        "id": "cpos",
        "pos": "VERB",
        "name_en": "possession",
        "name_pl": "posiadanie",
        "description_pl": "czasowniki posiadania i zmiany posiadania",
    },
    {
        "id": "cst",
        "pos": "VERB",
        "name_en": "state",
        "name_pl": "stan",
        "description_pl": "czasowniki stanowe",
    },
    {
        "id": "cumy",
        "pos": "VERB",
        "name_en": "cognition",
        "name_pl": "myślenie",
        "description_pl": "czasowniki myślenia (szeroko rozumianego)",
    },
    {
        "id": "cwyt",
        "pos": "VERB",
        "name_en": "creation",
        "name_pl": "wytwarzanie",
        "description_pl": "czasowniki oznacz. wytwarzanie czegoś",
    },
    {
        "id": "dtk",
        "pos": "VERB",
        "name_en": "contact",
        "name_pl": "kontakt fizyczny",
        "description_pl": "czasowniki oznacz. kontakt fizyczny (dotykanie, uderzenie, rycie itp.)",
    },
    {
        "id": "hig",
        "pos": "VERB",
        "name_en": "body",
        "name_pl": "higiena",
        "description_pl": "pielęgnacja ciała",
    },
    {
        "id": "pog",
        "pos": "VERB",
        "name_en": "weather",
        "name_pl": "pogoda",
        "description_pl": "czasowniki oznacz. zjawiska pogodowe",
    },
    {
        "id": "pst",
        "pos": "VERB",
        "name_en": "perception",
        "name_pl": "postrzeganie",
        "description_pl": "czasowniki postrzegania (percepcji)",
    },
    {
        "id": "ruch",
        "pos": "VERB",
        "name_en": "motion",
        "name_pl": "ruch",
        "description_pl": "czasowniki ruchu",
    },
    {
        "id": "sp",
        "pos": "VERB",
        "name_en": "social",
        "name_pl": "życie społeczne",
        "description_pl": "czasowniki oznacz. wydarzenie i działania społeczne i polityczne",
    },
    {
        "id": "wal",
        "pos": "VERB",
        "name_en": "competition",
        "name_pl": "rywalizacja",
        "description_pl": "czasowniki rywalizacji fizycznej",
    },
    {
        "id": "zmn",
        "pos": "VERB",
        "name_en": "change",
        "name_pl": "zmiana",
        "description_pl": "zmiana wielkości, temperatury, natężenia, itp.",
    },
    {
        "id": "grad",
        "pos": "ADJ",
        "name_en": "deadjectival",
        "name_pl": "przymiotnik odprzymiotnikowy (grad)",
        "description_pl": "przymiotniki odprzymiotnikowe (natężenie cechy)",
    },
    {
        "id": "jak",
        "pos": "ADJ",
        "name_en": "quality",
        "name_pl": "przymiotnik jakościowy (jak)",
        "description_pl": "przymiotniki jakościowe",
    },
    {
        "id": "odcz",
        "pos": "ADJ",
        "name_en": "deverbal",
        "name_pl": "przymiotnik odczasownikowy (odcz)",
        "description_pl": "przymiotniki odczasownikowe",
    },
    {
        "id": "rel",
        "pos": "ADJ",
        "name_en": "relation",
        "name_pl": "przymiotnik relacyjny (rel)",
        "description_pl": "przymiotniki relacyjne (rzeczownikowe)",
    },
    {
        "id": "zwz",
        "pos": "NOUN",
        "name_en": "relation",
        "name_pl": "relacja",
        "description_pl": "związek miedzy ludźmi, rzeczami lub ideami",
    },
    {
        "id": "cdystr",
        "pos": "VERB",
        "name_en": "distributive verb",
        "name_pl": "czasownki dystrybutywne",
        "description_pl": "czasownki dystrybutywne",
    },
    {
        "id": "caku",
        "pos": "VERB",
        "name_en": "accumulative verb",
        "name_pl": "czasowniki akumulatywne",
        "description_pl": "czasowniki akumulatywne",
    },
    {
        "id": "cper",
        "pos": "VERB",
        "name_en": "perdurative verb",
        "name_pl": "czasowniki perduratywne",
        "description_pl": "czasowniki perduratywne",
    },
    {
        "id": "cdel",
        "pos": "VERB",
        "name_en": "delimitative verb",
        "name_pl": "czasowniki delimitatywne",
        "description_pl": "czasowniki delimitatywne",
    },
    {
        "id": "mat",
        "pos": "ADJ",
        "name_en": "material adjective",
        "name_pl": "przymiotniki materiałowe",
        "description_pl": "przymiotniki materiałowe",
    },
    {
        "id": "adj",
        "pos": "ADJ",
        "name_en": "adjective",
        "name_pl": "PWN: przymiotnik",
        "description_pl": "PWN: all adjective clusters",
    },
    {
        "id": "adv",
        "pos": "ADV",
        "name_en": "adverb",
        "name_pl": "PWN: przysłówek",
        "description_pl": "PWN: all adverbs",
    },
]


@dataclass
class Domain:
    id: str
    pos: str
    name_pl: str
    name_en: str
    description_pl: str

    def __str__(self):
        return f"{self.id} ({self.pos}) — {self.name_en}"

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
