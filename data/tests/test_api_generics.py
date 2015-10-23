import pytest
import requests
import requests_mock

from django.core.validators import URLValidator, EmailValidator
from lxml import html
from data.api.generics import ExternalAPI, SearchFormMixin, FieldParserMixin
from data.api.errors import APIError
from data.api.decorators import field

def test_bad_external_api_base_url():
    class BadAPI(ExternalAPI):
        base_url = 'http://what.the.hell/'
        endpoint = 'is/going/on'

    with pytest.raises(requests.ConnectionError):
        BadAPI().request()

def test_bad_external_api_endpoint():
    class BadAPI(ExternalAPI):
        base_url = 'http://google.com/'
        endpoint = 'some_random_wrong_endpoint'

    with pytest.raises(APIError):
        BadAPI().request()

@requests_mock.Mocker()
def test_mock_api(mock):
    mock.get('http://test.com/test', text='success')

    class MockAPI(ExternalAPI):
        base_url = 'http://test.com/'
        endpoint = 'test'

    return MockAPI().request().text == 'success'


class TestSearchFormMixin:
    class MockAPI(ExternalAPI):
        base_url = 'http://test.com/'
        endpoint = 'form'

    class MockForm(SearchFormMixin, MockAPI):
        form_id = 'email_form'

    form_text = """
    <form id="name_form" action="name_form" method="post">
        <div>
            <label for="name">Name:</label>
            <input type="text" name="name" id="name" />
        </div>
    </form>
    <form id="email_form" action="email_form" method="post">
        <div>
            <label for="email">Email:</label>
            <input type="text" name="email" id="email" />
        </div>
    </form>
    """
    mock_form = MockForm()

    @requests_mock.Mocker()
    def test_mock_form(self, mock):
        mock.get('http://test.com/form', text=self.form_text)
        self.mock_form.request_new_form()
        assert self.mock_form.form
        assert self.mock_form.form.inputs['email'] is not None

        self.mock_form.update_form({'email': 'test@test.com'})
        assert self.mock_form.form.action == 'http://test.com/email_form'
        assert ('email', 'test@test.com') in self.mock_form.form.form_values()


class TestFieldParserMixin:
    class MockAPI(ExternalAPI):
        base_url = 'http://test.com/'
        endpoint = 'detail'

    class MockDetail(FieldParserMixin, MockAPI):
        def parse(self):
            text = self.request().text
            self.parsed_object = {
                elem.findtext('th'): elem.find('td')
                for elem in html.fromstring(text).xpath(
                    '//table/tr[th/@class="field"]'
                )
            }

        @field
        def name(self):
            return self.parsed_object['Name'].text

        @field
        def skills(self):
            elem = self.parsed_object['Skills'].find('p')
            return elem.text, elem.get('id')

        @field(validator=EmailValidator)
        def email(self):
            return self.parsed_object['E-mail'].text

        @field(validator=EmailValidator)
        def bad_email(self):
            return self.parsed_object['Bad E-mail'].text

        @field(validator=URLValidator)
        def website(self):
            return self.parsed_object['Website'].find('a').get('href')

        @field(validator=URLValidator)
        def dirty_website(self):
            elem = self.parsed_object['Dirty Website'].find('a')
            return elem.get('href'), elem.text

        @field(validator=URLValidator)
        def bad_website(self):
            elem = self.parsed_object['Bad Website'].find('a')
            return elem.get('href'), elem.text

    form_text = """
    <table>
        <tr><th class="field">Name</th><td>John Doe</td>
        <tr><th class="field">Skills</th><td><p id="Bowling"></p></td>
        <tr><th class="field">E-mail</th><td>test@test.com</td>
        <tr><th class="field">Bad E-mail</th><td>test.test</td>
        <tr><th class="field">Website</th><td><a href="http://test.com">test.com</a></td>
        <tr><th class="field">Dirty Website</th><td><a href="http://https://test.com">https://test.com</a></td>
        <tr><th class="field">Bad Website</th><td><a href="http://http://https://test.com">http://https://test.com</a></td>
    </table>
    """
    mock_detail = MockDetail()

    @requests_mock.Mocker()
    def test_mock_detail(self, mock):
        mock.get('http://test.com/detail', text=self.form_text)
        assert self.mock_detail.is_valid

        fields = self.mock_detail.to_dict()
        assert fields.get('name') == 'John Doe'
        assert fields.get('skills') == 'Bowling'
        assert fields.get('email') == 'test@test.com'
        assert fields.get('bad_email') == ''
        assert fields.get('website') == 'http://test.com'
        assert fields.get('dirty_website') == 'https://test.com'
        assert fields.get('bad_website') == ''
