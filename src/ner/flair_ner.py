from .wlflairshim import SequenceTagger
import re
import functools
import json
import html

class NamedEntityRecognizer:
    def __init__(self, wolfram_kernel_path, type_precedence, min_confidence):
        """Creates a new named entity recognizer"""
        self.tagger = SequenceTagger(wolfram_kernel_path)
        self.type_precedence = type_precedence
        self.min_confidence = min_confidence
        self.seen_entities = dict() # Looks like {'id': entity}. Each entity has a unique canonical id, which is nice because it also prevents duplicates

    def tag_entities(self, text):
        """Tags entities in plaintext in a format similar to Flair"""
        paragraphs = re.split(r'\n{2,}', text)
        output = []
        for p in paragraphs:
            tagger_output = self.tagger.predict(p, entity_types=self.type_precedence)
            tagger_output['entities'] = [entity for entity in tagger_output['entities'] if entity['confidence'] >= self.min_confidence]
            tagger_output['entities'] = self.remove_entity_overlaps(tagger_output['entities'])
            for entity in tagger_output['entities']:
                entity_id = self.to_xml_id(entity['interpretation'])
                entity['id'] = entity_id
                if entity_id != None: self.seen_entities[entity_id] = entity['interpretation']
            output.append(tagger_output)
        return output

    def get_seen_entities(self):
        """Gets the dictionary of entities tagged so far with this NamedEntityRecognizer"""
        return self.seen_entities

    def close(self):
        """Closes the Wolfram Kernel session"""
        self.tagger.close()

    def to_xml_id(self, interpretation):
        """Turns a Mathematica text content interpreation into a unique ID that can be used as an XML
        attribute value. Returns none if it's not a Mathematica entity.

        interpretation -- Mathematica text content interpretation to turn into and ID
        """
        if type(interpretation) is str or interpretation.head.name != 'Entity': return None
        entity_type = interpretation.args[0]
        canonical_name = interpretation.args[1]
        canonical_name = html.escape(json.dumps(canonical_name, separators=(',', ':')))
        return f"urn:WolframEntity:{entity_type}:{canonical_name}"

    def is_overlapping(self, x1, x2, y1, y2):
        """Determines if two ranges (x1, x2) and (y1, y2) overlap"""
        return x1 <= y2 and y1 <= x2

    def compare_entities(self, e1, e2):
        """Compares two entities by their preference. An entity is more preferred if:
            - its text is longer
            - its entity type comes first in the type precedence
            - its confidence value is higer
        """
        type_precedence = self.type_precedence
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

    def remove_entity_overlaps(self, entities_in):
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
                if entity != other_entity and self.is_overlapping(
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
            entities_out.append(sorted(entities, key=functools.cmp_to_key(self.compare_entities))[-1])
        return sorted(entities_out, key=lambda entity: entity['start_pos'])