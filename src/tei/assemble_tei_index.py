from bs4 import BeautifulSoup
from wolframclient.language import wl, wlexpr

template_file = open('siteindex_template.tei', 'r')
template = template_file.read()
template_file.close()

class IndexAssembler:
    def __init__(self, wl_session):
        """Initialize the IndexAssembler
        wl_session -- an active Wolfram kernel session
        """
        self.session = wl_session

    def create_index(self, seen_entities):
        """Generate a TEI index out of the seen_entities of a NamedEntityRecognizer"""
        soup = BeautifulSoup(template, 'xml')
        for mathematica_urn, entity_data in seen_entities.items():
            xml_id, interpretation = entity_data
            entity_type = interpretation[0]
            if entity_type == 'Company':
                org = self.get_company_tag(soup, mathematica_urn, xml_id, interpretation)
                soup.find('listOrg', attrs={'type': 'Company'}).append(org)
            elif entity_type == 'People':
                person = self.get_person_tag(soup, mathematica_urn, xml_id, interpretation)
                soup.find('listPerson', attrs={'type': 'People'}).append(person)
        return str(soup.prettify())

    def get_company_tag(self, soup, mathematica_urn, xml_id, interpretation):
        """Generate a TEI tag for a company

        Looks like:
        <org xml:id="VARIABLE companyId">
            <orgName>VARIABLE Company name</orgName>
            <note>VARIABLE Notable information about the company</note>
        </org>
        """
        org = soup.new_tag('org', attrs={
            'xml:id': xml_id,
            'ref': mathematica_urn
        })
                
        orgName = soup.new_tag('orgName')
        name = self.session.evaluate(wl.System.EntityValue(interpretation, "Name"))
        orgName.append(name)
        org.append(orgName)

        note = soup.new_tag('note')
        industry = self.session.evaluate(wl.System.EntityValue(interpretation, "Industry"))
        founded = self.session.evaluate(wl.System.DateString(wl.System.EntityValue(interpretation, "FoundingDate")))
        status = self.session.evaluate(wl.System.EntityValue(interpretation, "Status")).lower()
        note.append(f"{industry} company founded in {founded}. Currently {status}.")
        org.append(note)

        return org