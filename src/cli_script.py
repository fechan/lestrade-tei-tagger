from ner.flair_ner import tagger
from tei.assemble_document import create_document

print(create_document('''page 1 Paris. December 1st, 1889.

Sailed from New York, Saturday November 16th on S.S. Bourgogne, and
arrived at Havre Nov. 24th at noon.  A dull and uneventful voyage - and
a most disagreeable landing in a heavy storm of wind and rain, in a tug,
with no protection but that our umbrellas and wraps gave us.  Came to
our old quarters at Hotel Chatham.

Shepheards Hotel Cairo - Egypt.  Dec. 12. 1889.'''))
tagger.close()