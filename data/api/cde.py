from django.core.validators import URLValidator, EmailValidator
from lxml import html
from .generics import ExternalAPI, SearchFormMixin, FieldParserMixin
from .decorators import field

# Constants
MODE_PUBLIC = '1'
MODE_PRIVATE = '3'


class CdeAPI(ExternalAPI):
    base_url = 'http://www.cde.ca.gov/re/sd/'


class CdeSchoolSearchForm(SearchFormMixin, CdeAPI):
    endpoint = 'index.asp'
    form_id = 'search'

    def init_search(self, **field_values):
        # Get and update the form
        self.request_new_form()
        token = {'Cookie': self.form_page.headers.get('set-cookie')}

        # Include all counties in search
        field_defaults = {
            'countyName': [
                i.get('value') if i.get('value') else i.text
                for i in self.form.xpath('//select[@id="county"]/option')
            ][1:]
        }
        field_defaults.update(field_values)

        # Update form with search parameters
        self.update_form(field_defaults)

        # Finally submit the form
        self.request(self.form.action,
                     method='POST',
                     headers=token,
                     data=self.form.form_values())

        return token


class CdeSchoolSearchList(object):
    def __init__(self, **field_values):
        super(CdeSchoolSearchList, self).__init__()
        self._token = CdeSchoolSearchForm().init_search(**field_values)

        # Generate a list of schools from search results
        self.schools = set()
        self._build_school_list()

    def _build_school_list(self):
        page = 1
        while page:
            page = PaginatedCdeSchoolSearchResults(token=self._token,
                                                   page=page)

            for school in page.get_search_results():
                self.schools.add(school)

            page = page.next_page


class PaginatedCdeSchoolSearchResults(CdeAPI):
    endpoint = 'results.asp?nav={page}&items=100'

    def __init__(self, token, page):
        super(PaginatedCdeSchoolSearchResults, self).__init__()
        self._page = page
        self._raw = html.fromstring(
            self.request(headers=token, page=self._page).text
        )

    @property
    def _has_next_page(self):
        next_page_link = self._raw.xpath('//a[text()="Next >>"]')
        return bool(next_page_link)

    @property
    def next_page(self):
        if self._has_next_page:
            return self._page + 1

    def get_search_results(self):
        return self._raw.xpath('//table/tr/td/a/@href')


class CdeSchoolDetail(FieldParserMixin, CdeAPI):
    def __init__(self, endpoint):
        super(CdeSchoolDetail, self).__init__()
        self._raw = html.fromstring(self.request(endpoint=endpoint).text)

    def parse(self):
        table = self._raw.xpath(
            '//table[contains(@class, "table") and '
            'tr/th[contains(@class, "shadow")]]'
        )[0]

        # There are two types of fields:
        # 1. <tr><th class='shadow details-field-label'><b>Field</b></th><td>
        #    Value</td></tr>
        # 2. <tr><td class='shadow'><b>Field</b></td><td>Value</td></tr>

        # Parse fields of type 1.
        self.parsed_object = {
            i.findtext('th/b'): i.find('td')
            for i in table.xpath(
                './tr[th/@class="shadow details-field-label" and td]'
            )
        }

        # Add fields of type 2.
        self.parsed_object.update({
            i.findtext('td/b'): i.find('td').getnext()
            for i in table.xpath('./tr[td/@class="shadow"]')
        })

    @field
    def phone(self):
        return self.parsed_object['Phone Number'].text

    @field
    def name(self):
        return self.parsed_object['School'].text

    @field
    def status(self):
        return self.parsed_object['Status'].text

    @field
    def low_grade(self):
        return self.parsed_object['Low Grade'].text

    @field
    def high_grade(self):
        return self.parsed_object['High Grade'].text

    @field
    def code(self):
        return self.parsed_object['CDS Code'].text.replace(' ', '')

    @field
    def nces_id(self):
        return self.parsed_object['NCES/Federal School ID'].text

    @field
    def county(self):
        return self.parsed_object['County'].text

    @field
    def district(self):
        if 'District' in self.parsed_object:
            return self.parsed_object['District'].findtext('a')
        else:
            return self.parsed_object[
                'Located within the boundaries of this public school district'
            ].text

    @field
    def address(self):
        elem = self.parsed_object['School Address']

        # Remove the link to Yahoo Map if it exists
        map_link = elem.find('a')
        if map_link is not None:
            elem.remove(map_link)

        return ', '.join(elem.itertext())

    @field
    def school_type(self):
        return self.parsed_object['School Type'].text

    @field
    def year_round(self):
        return self.parsed_object['Year Round'].text

    @field
    def charter(self):
        return self.parsed_object['Charter'].text

    @field
    def charter_number(self):
        return self.parsed_object['Charter Number'].text

    @field
    def charter_funding(self):
        return self.parsed_object['Charter Funding Type'].text

    @field
    def open_date(self):
        return self.parsed_object['Open Date'].text

    @field
    def close_date(self):
        return self.parsed_object['Close Date'].text

    @field
    def fax(self):
        return self.parsed_object['Fax Number'].text

    @field(validator=EmailValidator)
    def email(self):
        return self.parsed_object['School Email'].findtext('a')

    @field(validator=URLValidator)
    def website(self):
        elem = self.parsed_object['Web site'].find('a')
        return elem.get('href'), elem.text

    @field
    def administrators(self):
        return '\n'.join(self.parsed_object['Administrator(s)'].itertext())

    @field
    def mailing_address(self):
        return ', '.join(self.parsed_object['Mailing Address'].itertext())

    @field
    def stats(self):
        return self.parsed_object['Statistical Info'].find('a').get('href')
