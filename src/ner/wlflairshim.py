from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wl, wlexpr

class SequenceTagger:
    def __init__(self, wl_kernel=None):
        """Initialize the SentenceTagger
        wl_kernel -- location of Wolfram kernel
        """
        self.session = WolframLanguageSession() if wl_kernel == None else WolframLanguageSession(wl_kernel)

    def close(self):
        """Stop the Wolfram Kernel associated with this tagger"""
        self.session.stop()

    def predict(self, text: str, **kwargs) -> dict:
        """Get text entities in text
        text -- text to get entities from
        
        Keyword arguments:
        entity_types -- list of entity types to include
        """
        forms = wl.System.Automatic
        if "entity_types" in kwargs:
            forms = wl.System.List(*kwargs["entity_types"])
        expr = wl.System.TextContents(text, forms, wl.System.All)
        response = self.session.evaluate(expr)
        entities = []
        for entity in response[0]:
            entities.append({
                "text": entity["String"],
                "start_pos": entity["Position"][0] - 1,
                "end_pos": entity["Position"][1],
                "type": entity["Type"],
                "confidence": entity["Probability"]
            })
        return {
            "text": text,
            "entities": entities
        }