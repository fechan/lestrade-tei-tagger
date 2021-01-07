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
        self.dateformat = wl.List('Year', '-', 'Month', '-', 'Day')

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
                soup.find('listPerson', attrs={'type': 'Person'}).append(person)
        return str(soup.prettify())

    def get_person_tag(self, soup, mathematica_urn, xml_id, interpretation):
        """"Generate the a TEI index entry for a person

        Looks like:
        <person xml:id="Alice" sex="f">
            <persName>Alice</persName>
            <birth when="1900-01-01">
                <placeName>Cairo, Egypt</placeName>
            </birth>
            <death when="1900-01-01">
                <placeName>Cairo, Egypt</placeName>
            </death>
            <occupation type="actor"/> <!-- multiple of these can exist here -->
            <note>Notable information about Alice</note>
        </person>
        """
        gender = self.session.evaluate(
            wl.EntityValue(
                wl.EntityValue(interpretation, 'Gender'),
                'Name'
            )
        )
        person = soup.new_tag('person', attrs={
            'xml:id': xml_id,
            'ref': mathematica_urn,
            'sex': gender[0]
        })

        persName = soup.new_tag('persName')
        name = self.session.evaluate(wl.EntityValue(interpretation, "Name"))
        persName.append(name)
        person.append(persName)

        birthday = self.session.evaluate(
            wl.DateString(
                wl.EntityValue(interpretation, "BirthDate"),
                self.dateformat
            )
        )
        birth = soup.new_tag('birth', attrs={'when': birthday})
        placeName = soup.new_tag('placeName')
        birthplace = self.session.evaluate(
            wl.CityData(
                wl.EntityValue(interpretation, "BirthPlace"),
                "FullName"
            )
        )
        placeName.append(birthplace)
        birth.append(placeName)
        person.append(birth)

        deathday = self.session.evaluate(
            wl.DateString(
                wl.EntityValue(interpretation, "DeathDate"),
                self.dateformat
            )
        )
        death = soup.new_tag('death', attrs={'when': deathday})
        placeName = soup.new_tag('placeName')
        deathplace = self.session.evaluate(
            wl.CityData(
                wl.EntityValue(interpretation, "DeathPlace"),
                "FullName"
            )
        )
        placeName.append(deathplace)
        death.append(placeName)
        person.append(death)

        occupations = self.session.evaluate(wl.EntityValue(interpretation, "Occupation"))
        for occupation_name in occupations:
            occupation = soup.new_tag("occupation", attrs={'type': occupation_name})
            person.append(occupation)

        note = soup.new_tag('note')
        notable_facts = session.evaluate(
            wl.Map(
                wl.ToString,
                wl.EntityValue(interpretation, "NotableFacts")
            )
        )
        note.append(notable_facts)
        person.append(note)

        return person


    def get_company_tag(self, soup, mathematica_urn, xml_id, interpretation):
        """Generate a TEI index entry for a company.

        Looks like:
        <org xml:id="companyId">
            <orgName>Company name</orgName>
            <note>Notable information about the company</note>
        </org>
        """
        org = soup.new_tag('org', attrs={
            'xml:id': xml_id,
            'ref': mathematica_urn
        })
                
        orgName = soup.new_tag('orgName')
        name = self.session.evaluate(wl.EntityValue(interpretation, "Name"))
        orgName.append(name)
        org.append(orgName)

        note = soup.new_tag('note')
        industry = self.session.evaluate(wl.EntityValue(interpretation, "Industry"))
        founded = self.session.evaluate(wl.DateString(wl.EntityValue(interpretation, "FoundingDate")))
        status = self.session.evaluate(wl.EntityValue(interpretation, "Status")).lower()
        note.append(f"{industry} company founded in {founded}. Currently {status}.")
        org.append(note)

        return org