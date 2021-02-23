from bs4 import BeautifulSoup
from wolframclient.language import wl, wlexpr
import wikidata.client
import copy

template_file = open('tei_index_templates/siteindex.tei', 'r')
template = template_file.read()
template_file.close()

wiki_pids = {
    'birth': 'P569',
    'birthplace': 'P19',
    'death': 'P570',
    'deathplace': 'P20',
    'occupation': 'P106',
    'country': 'P17',
    'coordinates': 'P625',
    'sex': 'P21'
}

class IndexAssembler:
    def __init__(self, wl_session):
        """Initialize the IndexAssembler
        wl_session -- an active Wolfram kernel session
        """
        self.session = wl_session
        self.wikiclient = wikidata.client.Client()

    def create_index(self, seen_entities, title, author, sponsor, authority, licence):
        """Generate a TEI index out of the seen_entities of a NamedEntityRecognizer"""
        soup = BeautifulSoup(template, 'xml')
        soup.find('title').append(title)
        soup.find('author').append(author)
        soup.find('sponsor').append(sponsor)
        soup.find('authority').append(authority)
        soup.find('licence').append(licence)

        for mathematica_urn, entity_data in seen_entities.items():
            xml_id, interpretation = entity_data
            wikidata_id = self.session.evaluate(wl.WikidataData(interpretation, 'WikidataID'))[0][1]
            wikientity = self.wikiclient.get(wikidata_id, load=True)
            entity_type = interpretation[0]
            if entity_type == 'Person':
                person = self.get_person_tag(mathematica_urn, xml_id, wikientity)
                soup.find('listPerson', attrs={'type': 'Person'}).append(person)
        return str(soup.prettify())

    def wikiprop(self, wikientity, prop):
        """Get the value of the property specified by the property name for the given Wikidata
        entity. Property names and associated Wikidata PIDs are defined in the wiki_pids
        constant.

        wikientity -- Wikidata entity
        prop -- property name
        """
        return wikientity.get(self.wikiclient.get(wiki_pids[prop]))

    def date_wikiprop(self, wikientity, prop):
        prop = wiki_pids[prop]
        value = wikientity.attributes['claims'][prop][0]['mainsnak']['datavalue']['value']
        date = value['time'].split("T")[0]
        precision = value['precision']
        bc = date.startswith("-")
        if date.startswith("-") or date.startswith("+"):
            date = date[1:]
        if precision >= 11:
            return date
        else:
            date_string = ""
            year, month, day = date.split("-")
            if precision == 10:
                date_string = f"{year}-{month}"
            elif precision <= 9:
                date_string = f"{year}"

            if bc:
                return f"-{date_string}"
            else:
                return date_string

    def read_template(self, path, tag_name):
        """Get a BeautifulSoup of a TEI index template. You have to specify the name of the tag you
        want as well.

        path -- file path of template
        tag_name -- name of the tag the template is for
        """
        tei_file = open(path, 'r')
        tei_template = tei_file.read()
        tei_file.close()

        soup = BeautifulSoup(tei_template, 'xml')
        soup = soup.find(tag_name) # we have to do this otherwise BS inserts an XML declaration
        return copy.copy(soup)

    def get_person_tag(self, mathematica_urn, xml_id, wikientity):
        name = str(wikientity.label)
        short_desc = str(wikientity.description)
        sex = str(self.wikiprop(wikientity, 'sex').label)[0]
        birth = self.date_wikiprop(wikientity, 'birth')
        birthplace = str(self.wikiprop(wikientity, 'birthplace').label)
        death = self.date_wikiprop(wikientity, 'death')
        deathplace = str(self.wikiprop(wikientity, 'deathplace').label)
        occupation = self.wikiprop(wikientity, 'occupation')
        occupation_name = str(occupation.label)
        occupation_desc = str(occupation.description)

        person = self.read_template('tei_index_templates/person.tei', 'person')
        person.attrs = {'xml:id': xml_id, 'sex': sex, 'ref': mathematica_urn}

        person.find('persName').append(name)
        person.find('desc', type='shortDescription').append(short_desc)

        birth_tag = person.find('birth')
        birth_tag.attrs = {'when': birth}
        birth_tag.find('placeName').append(birthplace)

        death_tag = person.find('death')
        death_tag.attrs = {'when': death}
        death_tag.find('placeName').append(deathplace)

        person.find('occupation').attrs = {'type': occupation_name}
        person.find('occupation').append(occupation_desc)

        return person
