"""tag_ia_texts.py - Downloads raw text of an Internet Archive book and TEI tags it
"""
import io
import re
from internetarchive import get_files
from ner.flair_ner import NamedEntityRecognizer
from tei.assemble_document import create_document

ia_idents = ["reminiscencesoft00tangrich"]

ner = NamedEntityRecognizer()
for ident in ia_idents:
    files = get_files(ident, glob_pattern="*djvu.txt", formats="txt")
    txt_file = next(files)
    txt_file.download(file_path=f"./txt_files/{ident}.txt")
    with open(f"./tei_files/{ident}.tei", "w") as output_file:
        with open(f"./txt_files/{ident}.txt", "r") as book:
            content = book.read()
        output_file.write(create_document(ner, content))
ner.close()