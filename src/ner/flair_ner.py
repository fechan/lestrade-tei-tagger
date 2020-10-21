from .wlflairshim import SequenceTagger
import logging
from nltk import download
from nltk.tokenize import sent_tokenize

download('punkt')

tagger = SequenceTagger("/opt/Mathematica/SystemFiles/Kernel/Binaries/Linux-x86-64/WolframKernel")
logging.info('Loaded tagger')

wolfram_content_types = [
    'Person',
    'City',
    'Company',
    'Quantity',
    'CurrencyAmount',
    'Date',
    'Location',
    'River',
    'HistoricalSite',
    'Ship',
    'Artwork',
    'Museum',
    'HistoricalSite',
]

def tag_entities(text):
    sentences = sent_tokenize(text)
    output = []
    for s in sentences:
        output.append(tagger.predict(s, entity_types=wolfram_content_types))
    return output

