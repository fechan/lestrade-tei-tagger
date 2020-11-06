"""tag_ia_texts.py - Downloads raw text of an Internet Archive book and TEI tags it
"""
import internetarchive as ia
import re
from ner.flair_ner import tag_entities, tagger
from tei.assemble_tei import create_header, create_xml, create_body

ia_idents = ["reminiscencesoft00tangrich"]

for ident in ia_idents:
    files = ia.get_files(ident, glob_pattern="*djvu.txt", formats="txt")
    txt_file = next(files)
    txt_file.download()