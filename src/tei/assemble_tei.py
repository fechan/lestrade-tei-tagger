import re
from bs4 import BeautifulSoup
from lxml import etree
from src.utils.license_utils import license_dict
from src.utils.ref_utils import create_initials_ref, create_name_ref, create_ref


# tag_dict = {'PER': 'persName',
#             'LOC': 'placeName',
#             'MISC': 'orgName',
#             'ORG': 'name'}
tag_dict = {
    'Person': 'persName',
    'City': 'settlement',
    'Company': 'orgName',
    'Quantity': 'measure',
    'CurrencyAmount': 'measure',
    'Date': 'date',
    'Location': 'placeName',
    'LocationEntity': 'placeName',
    'River': 'geogName',
    'HistoricalSite': 'placeName',
    'Ship': 'objectName',
    'Artwork': 'objectName',
    'Museum': 'placeName',
    'HistoricalSite': 'placeName',
}

def create_markup_with_entities(annotated_text):
    '''Given some source text and Flair-like annotated text, create TEI markup with
    the entities wrapped in the appropriate tag names
    
    annotated_text: text that we've run through a Flair-like tagger
    '''
    markup = ''
    text = annotated_text['text']
    entities = annotated_text['entities']
    index = 0
    for entity in entities:
        entity_type = entity["type"]
        entity_text = entity["text"]
        entity_id = entity["id"]
        tagname = tag_dict.get(entity['type'], "name")
        if entity_text not in ["I’ve", "I’ll", "I", "I’m", "I've", "I'll", "I'm", "I,", "Today", "today"]: # Mathematica thinks instances of "today" refers to runtime
            markup += text[index:entity['start_pos']]
            # The following generates a "ref" attribute based on entity text
            # I'm pretty sure the output is best used for the "key" attribute
            # and since some of the entities have Wolfram Language entity interpretations,
            # it's probably better to use their canonical names as keys when possible.
            #
            # if e['type'] == 'PER':
            #     ref = create_name_ref(entity_text)
            # else:
            #     ref = create_ref(entity_text)
            if ('interpretation' in entity and 
                    type(entity['interpretation']) is not str and
                    entity['interpretation'].head.name in ['Quantity', 'DateObject', 'GeoPosition']):
                interpretation_type = entity['interpretation'].head.name
                if interpretation_type == 'Quantity':
                    quantity = entity['interpretation'].args[0]
                    unit = entity['interpretation'].args[1]
                    markup += f'<{tagname} type="{entity_type}" quantity="{quantity}" unit="{unit}">{entity_text}</{tagname}>'
                elif interpretation_type == 'DateObject':
                    date_tuple = entity['interpretation'].args[0]
                    when = ""
                    if len(date_tuple) == 3:
                        year, month, day = date_tuple
                        when = f'{year}-{month}-{day}'
                    elif len(date_tuple) == 2:
                        year, month = date_tuple
                        when = f'{year}-{month}'
                    elif len(date_tuple) == 1:
                        year = date_tuple[0]
                        when = f'{year}'
                    markup += f'<{tagname} type="{entity_type}" when="{when}">{entity_text}</{tagname}>'
                elif interpretation_type == 'GeoPosition':
                    latitude, longitude = entity['interpretation'].args[0]
                    markup_lines = [
                        f'<place>',
                        f'   <placeName>{entity_text}</placeName>',
                        f'   <location><geo decls="#ITRF00">{latitude}, {longitude}</geo></location>', # Mathematica uses ITRF00 datum by default
                        f'</place>',
                    ]
                    markup += '\n'.join(markup_lines)
            else:
                if entity_id != None:
                    markup += f'<{tagname} type="{entity_type}" ref="{entity_id}">{entity_text}</{tagname}>'
                else:
                    markup += f'<{tagname} type="{entity_type}">{entity_text}</{tagname}>'
            index = entity['end_pos']
    markup += text[index:]
    markup += ' '
    return markup

def create_header(title='', author='', editor='', publisher='', publisher_address='',
                  publication_date='', license_desc='', project_description='', source_description=''):
    soup = BeautifulSoup()
    soup.append(soup.new_tag('teiHeader'))
    soup.find('teiHeader').append(soup.new_tag('fileDesc'))
    soup.find('fileDesc').append(soup.new_tag('titleStmt'))
    if title != '':
        soup.find('titleStmt').append(soup.new_tag('title'))
        soup.title.string = title
    if author != '':
        soup.find('titleStmt').append(soup.new_tag('author'))
        soup.author.append(soup.new_tag('persName'))
        soup.author.persName.string = author
        soup.author.persName['ref'] = create_name_ref(author)
    if editor != '':
        soup.find('titleStmt').append(soup.new_tag('editor'))
        soup.editor.append(soup.new_tag('persName'))
        soup.editor.persName.string = editor
        soup.editor.persName['ref'] = create_initials_ref(editor)
    if publisher != '':
        soup.fileDesc.append(soup.new_tag('publicationStmt'))
        soup.publicationStmt.append(soup.new_tag('publisher'))
        soup.publisher.append(soup.new_tag('orgName'))
        soup.publisher.orgName.string = publisher
        soup.publisher.orgName['ref'] = create_ref(publisher)
        if publisher_address != '':
            soup.publicationStmt.append(soup.new_tag('address'))
            soup.publicationStmt.address.append(soup.new_tag('addrLine'))
            soup.publicationStmt.address.addrLine.string = publisher_address
        if license_desc != '':
            soup.publicationStmt.append(soup.new_tag('availability'))
            soup.availability.append(soup.new_tag('licence'))
            soup.licence['target'] = license_dict[license_desc]['target']
            soup.licence.string = license_dict[license_desc]['text']
        if publication_date != '':
            soup.publicationStmt.append(soup.new_tag('date'))
            soup.publicationStmt.date.string = publication_date
    if source_description != '':
        soup.fileDesc.append(soup.new_tag('sourceDesc'))
        soup.sourceDesc.append(soup.new_tag('p'))
        markup = create_markup_with_entities(source_description)
        markup = markup[0:-1]
        soup.sourceDesc.p.string = markup
    if project_description != '':
        soup.fileDesc.append(soup.new_tag('encodingStmt'))
        soup.encodingStmt.append(soup.new_tag('projectDesc'))
        soup.projectDesc.append(soup.new_tag('p'))
        markup = create_markup_with_entities(project_description)
        markup = markup[0:-1]
        soup.projectDesc.p.string = markup
    return soup


def create_body(flair_output):
    soup = BeautifulSoup()
    soup.append(soup.new_tag('text'))
    soup.find('text').append(soup.new_tag('body'))
    soup.body.append(soup.new_tag('div'))
    for paragraph in flair_output:
        paragraph_tag = soup.new_tag('p')
        markup = create_markup_with_entities(paragraph)
        markup = markup[0:-1]
        paragraph_tag.string = markup
        soup.div.append(paragraph_tag)
    return soup


def create_xml(header, body):
    soup = BeautifulSoup()
    soup.append(soup.new_tag('TEI', xmlns="http://www.tei-c.org/ns/1.0"))
    soup.TEI.append(header)
    soup.TEI.append(body)
    root = etree.fromstring(str(soup))
    xml_str = etree.tostring(root, pretty_print=True).decode()
    xml_str = re.sub('&lt;', '<', xml_str)
    xml_str = re.sub('&gt;', '>', xml_str)
    xml_str = re.sub('&amp;', '&', xml_str)
    xml_str = re.sub('&#163;', '£', xml_str)
    xml_str = re.sub('&#8220;', '"', xml_str)
    xml_str = re.sub('&#8221;', '"', xml_str)
    xml_str = re.sub('&#8217;', "'", xml_str)
    xml_str = re.sub(' Nile.', ' <placeName ref="Nile">Nile</placeName>.', xml_str)

    return xml_str.encode('utf-8')


if __name__ == '__main__':
    flair_output = [{'text': 'Hello, my name is Audrey.', 'labels': [], 'entities': [{'text': 'Audrey.', 'start_pos': 18, 'end_pos': 25, 'type': 'PER', 'confidence': 0.9849573373794556}]},
                    {'text': 'I love New York.', 'labels': [], 'entities': [
                        {'text': 'New York.', 'start_pos': 7, 'end_pos': 16, 'type': 'LOC',
                         'confidence': 0.9960977137088776}]}
                    ]
    header = create_header('Title', 'Author', 'Editor')
    body = create_body(flair_output)
    print(create_xml(header, body))
