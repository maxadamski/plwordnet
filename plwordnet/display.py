POLARITY_STR = {
    None: 'unknown',
    -2: 'strong negative',
    -1: 'weak negative',
    0: 'neutral',
    +1: 'weak positive',
    +2: 'strong positive',
}


POS_STR = {
    'rzeczownik': 'NOUN',
    'rzeczownik pwn': 'NOUN',
    'przymiotnik': 'ADJ',
    'przymiotnik pwn': 'ADJ',
    'przysłówek': 'ADV',
    'przysłówek pwn': 'ADV',
    'czasownik': 'VERB',
    'czasownik pwn': 'VERB',
}


def lexical_unit_html(lu):
    res = '<style>th, td { text-align: left !important; }</style>'
    res += f'<table width=500><colgroup><col span="1" style="width: 20%;"><col span="1" style="width: 80%"></colgroup>'
    res += f'<thead><tr><th>#{lu.id}</th><td>{lu.pos} {lu.language.upper()} {lu.name} {lu.variant}</td></tr></thead>'
    if lu.rich_description is not None and lu.rich_description.definition:
        res += f'<tr><th>DEFINITION</th><td>{lu.rich_description.definition}</td></tr>'
    elif lu.description:
        res += f'<tr><th>DESCRIPTION</th><td>{lu.description}</td></tr>'
    if lu.synset.definition:
        res += f'<tr><th>SYNSET DEFINITION</th><td>{lu.synset.definition}</td></tr>'
    res += f'<tr><th>DOMAIN</th><td>{lu.domain}</td></tr>'
    in_synset = '<br>'.join(str(x) for x in lu.synset.lexical_units if x != lu)
    if in_synset:
        res += f'<tr><th>SYNONYMS</th><td>{in_synset}</td></tr>'
    if lu.rich_description is not None:
        examples = '<br><br>'.join(lu.rich_description.examples)
        if examples:
            res += f'<tr><th>EXAMPLES</th><td>{examples}</td></tr>'
        links = '<br>'.join(f'<a target="_blank" href="{x}">{x}</a>' for x in lu.rich_description.links)
        if links:
            res += f'<tr><th>LINKS</th><td>{links}</td></tr>'
    if lu.sentiment:
        for sent in lu.sentiment:
            res += '<tr><th>SENTIMENT ANNOTATION</th><td><table>'
            res += f'<tr><th>POLARITY</th><td>{POLARITY_STR[sent.polarity]}</td></tr>'
            res += f'<tr><th>EMOTIONS</th><td>{", ".join(sent.emotions)}</td></tr>'
            res += f'<tr><th>VALUATIONS</th><td>{", ".join(sent.valuations)}</td></tr>'
            res += f'<tr><th>EXAMPLES</th><td>{", ".join(sent.examples)}</td></tr>'
            res += '</table></td></tr>'
    
    res += '</table>'
    return res


def lexical_relations(wn, lu):
    res = ''
    for s, p, o in wn.lexical_relations_where(subject=lu):
        op = '⟷' if p.inverse == p else '→'
        res += f'{p.name} {op} {o}\n'
    for s, p, o in wn.lexical_relations_where(object=lu):
        if p.inverse != p: res += f'{p.name} ← {s}\n'
    return res


def synset_relations(wn, syn):
    res = ''
    for s, p, o in wn.synset_relations_where(subject=syn):
        op = '⟷' if p.inverse == p else '→'
        res += f'{p.name} {op} {o.__str__(max_items=3)}\n'
    for s, p, o in wn.synset_relations_where(object=syn):
        if p.inverse != p: res += f'{p.name} ← {s.__str__(max_items=3)}\n'
    return res

