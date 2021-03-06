"""batch_tag.py - Tags all of the raw text files in the txt_files directory, tags them, and puts
them in the tei_files directory with the same name, but with ".tei" added to the end

txt_files directory should be in your current working directory.
"""
import os
import json
from src.ner.flair_ner import NamedEntityRecognizer
from src.tei.assemble_document import create_document
from src.tei.assemble_tei_index import IndexAssembler

with open('settings.json', 'r') as f:
    settings = json.load(f)

ner = NamedEntityRecognizer(
    settings['wolfram_kernel_path'],
    settings['content_types_precedence_order'],
    settings['minimum_confidence'],
    settings['generate_tei_index'],
    settings['tei_index_name']
)
filenames = next(os.walk("txt_files"))[2]
for filename in filenames:
    print("Now tagging", filename)
    with open(f"./tei_files/{filename}.tei", "w") as output_file:
        with open(f"./txt_files/{filename}", "r") as book:
            content = book.read()
        output_file.write(create_document(ner, content, title=filename))
print("All files in txt_files directory tagged.")
if settings['generate_tei_index'] == True:
    with open(f"./tei_files/{settings['tei_index_name']}.tei", 'w') as output_file:
        print("Creating TEI index")
        assembler = IndexAssembler(ner.tagger.session)
        output_file.write(assembler.create_index(
            ner.get_seen_entities(),
            settings['tei_index_title'],
            settings['tei_index_author'],
            settings['tei_index_sponsor'],
            settings['tei_index_authority'],
            settings['tei_index_licence'],
            settings['tei_index_ref_type']
        ))
ner.close()