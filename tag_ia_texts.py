"""tag_ia_texts.py - Downloads raw text of an Internet Archive book and TEI tags it
"""
import io
import re
import json
from internetarchive import get_files
from src.ner.flair_ner import NamedEntityRecognizer
from src.tei.assemble_document import create_document

ia_idents = ["reminiscencesoft00tangrich"]

with open('settings.json', 'r') as f:
    settings = json.load(f)

ner = NamedEntityRecognizer(
    settings['wolfram_kernel_path'],
    settings['content_types_precedence_order'],
    settings['minimum_confidence'],
)
for ident in ia_idents:
    files = get_files(ident, glob_pattern="*djvu.txt", formats="txt")
    txt_file = next(files)
    txt_file.download(file_path=f"./txt_files/{ident}.txt")
    with open(f"./tei_files/{ident}.tei", "w") as output_file:
        with open(f"./txt_files/{ident}.txt", "r") as book:
            content = book.read()
        output_file.write(create_document(ner, content))
ner.close()