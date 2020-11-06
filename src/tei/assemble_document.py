import re
from ner.flair_ner import tag_entities, tagger
from tei.assemble_tei import create_header, create_xml, create_body

def create_document(text, **kwargs):
    title = kwargs.get('title', '')
    author = kwargs.get('author', '')
    editor = kwargs.get('editor', '')
    publisher = kwargs.get('publisher', '')
    publisher_address = kwargs.get('publisher_address', '')
    publication_date = kwargs.get('publisher_date', '')
    license_desc = kwargs.get('license_desc', '')
    project_description = kwargs.get('project_description', '')
    source_description = kwargs.get('source_description', '')

    project_description = re.sub('\n|\t\r|\r\n', ' ', project_description)
    project_description = re.sub(' +', ' ', project_description)
    if project_description != '':
        project_description = tag_entities(project_description)

    source_description = re.sub('\n|\t\r|\r\n', ' ', source_description)
    source_description = re.sub(' +', ' ', source_description)
    if source_description != '':
        source_description = tag_entities(source_description
                                          )
    # Create header
    tei_header = create_header(title, author, editor, publisher, publisher_address,
                               publication_date, license_desc, project_description, source_description)

    # Create body
    text = text
    text = re.sub('\r', '', text)
    #text = re.sub('\n|\t\r|\r\n', ' ', text)
    #text = re.sub(' +', ' ', text)

    flair_output = tag_entities(text)
    tei_body = create_body(flair_output)

    # Assemble document
    tei_document = create_xml(tei_header, tei_body).decode('unicode-escape')
    return tei_document