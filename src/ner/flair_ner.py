from .wlflairshim import SequenceTagger
import logging
from nltk import download
from nltk.tokenize import sent_tokenize
import functools

download('punkt')

tagger = SequenceTagger("/opt/Mathematica/SystemFiles/Kernel/Binaries/Linux-x86-64/WolframKernel")
logging.info('Loaded tagger')

wolfram_content_types = [ # More specific entity types first
    'Person',
    'Museum',
    'HistoricalSite',
    'City',
    'Country',
    'Company',
    'Artwork',
    'Ship',
    'River',
    'Date',
    'CurrencyAmount',
    'Quantity',
    'Location'
]
type_precedence = wolfram_content_types

def is_overlapping(x1, x2, y1, y2):
    return x1 <= y2 and y1 <= x2

def compare_entities(e1, e2):
    """Compares two entities by their preference. An entity is more preferred if:
        - its text is longer
        - its entity type comes first in the type precedence
        - its confidence value is higer
    """
    if len(e1['text']) > len(e2['text']):
        return 1
    elif len(e1['text']) < len(e2['text']):
        return -1
    elif type_precedence.index(e1['type']) < type_precedence.index(e2['type']):
        return 1
    elif type_precedence.index(e1['type']) > type_precedence.index(e2['type']):
        return -1
    elif e1['confidence'] > e2['confidence']:
        return 1
    elif e1['confidence'] < e2['confidence']:
        return -1
    else:
        return 0

def remove_entity_overlaps(entities_in):
    """Removes overlapping entities from the input list. If 2 or more entities overlap in position,
    only the entity ranked highest by the given comparison function is retained in the output list.

    entities_in: input list of entities
    """
    entities_out = []
    all_overlaps = set()
    for entity in entities_in:
        overlapping_entities = set()
        for other_entity in entities_in:
            if entity != other_entity and is_overlapping(
                entity['start_pos'], entity['end_pos'], other_entity['start_pos'], other_entity['end_pos']):
                #have to turn dicts into tuples since dicts aren't hashable and can't be put in sets
                overlapping_entities.add(tuple(other_entity.items()))
        if len(overlapping_entities) > 0:
            overlapping_entities.add(tuple(entity.items()))
            all_overlaps.add(tuple(sorted(overlapping_entities))) #sorted so insertion order doesn't matter
        else:
            entities_out.append(entity)

    for overlapping_set in all_overlaps:
        entities = [dict(tup) for tup in overlapping_set]
        entities_out.append(sorted(entities, key=functools.cmp_to_key(compare_entities))[-1])
    return sorted(entities_out, key=lambda entity: entity['start_pos'])

def tag_entities(text):
    sentences = sent_tokenize(text)
    output = []
    for s in sentences:
        tagger_output = tagger.predict(s, entity_types=wolfram_content_types)
        tagger_output['entities'] = remove_entity_overlaps(tagger_output['entities'])
        output.append(tagger_output)
    return output