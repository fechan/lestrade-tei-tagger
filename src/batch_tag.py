"""batch_tag.py - Tags all of the raw text files in the txt_files directory, tags them, and puts
them in the tei_files directory with the same name, but with ".tei" added to the end

txt_files directory should be in your current working directory.
"""
import os
from ner.flair_ner import NamedEntityRecognizer
from tei.assemble_document import create_document

ner = NamedEntityRecognizer()
filenames = next(os.walk("txt_files"))[2]
for filename in filenames:
    print("Now tagging", filename)
    with open(f"./tei_files/{filename}.tei", "w") as output_file:
        with open(f"./txt_files/{filename}", "r") as book:
            content = book.read()
        output_file.write(create_document(ner, content))
print("All files in txt_files directory tagged.")
print(ner.get_seen_entities())
ner.close()