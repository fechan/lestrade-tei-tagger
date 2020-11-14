from .wlflairshim import SequenceTagger
import re
import functools
import json
import html

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
    'LocationEntity',
    'Location'
]
type_precedence = wolfram_content_types

def to_xml_id(interpretation):
    """Turns a Mathematica text content interpreation into a unique ID that can be used as an XML
    attribute value. Returns none if it's not a Mathematica entity.

    interpretation -- Mathematica text content interpretation to turn into and ID
    """
    if type(interpretation) is str or interpretation.head.name != 'Entity': return None
    entity_type = interpretation.args[0]
    canonical_name = interpretation.args[1]
    canonical_name = html.escape(json.dumps(canonical_name, separators=(',', ':')))
    return f"urn:WolframEntity:{entity_type}:{canonical_name}"

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
    The list is then sorted by the entity's start_pos.

    entities_in -- input list of entities
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

class NamedEntityRecognizer:
    def __init__(self):
        self.tagger = SequenceTagger('/opt/Mathematica/SystemFiles/Kernel/Binaries/Linux-x86-64/WolframKernel')
        self.seen_entities = set()

    def tag_entities(self, text):
        paragraphs = re.split(r'\n{2,}', text)
        output = []
        for p in paragraphs:
            tagger_output = self.tagger.predict(p, entity_types=wolfram_content_types)
            tagger_output['entities'] = remove_entity_overlaps(tagger_output['entities'])
            for entity in tagger_output['entities']:
                entity['id'] = to_xml_id(entity['interpretation'])
                if entity['id'] != None: self.seen_entities.add(entity['id'])
            output.append(tagger_output)
        return output

    def get_seen_entities(self):
        return list(self.seen_entities)

    def close(self):
        self.tagger.close()