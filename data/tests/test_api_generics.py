import pytest
import requests
import requests_mock

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
                elem.get('id'): elem.text
                for elem in html.fromstring(text).xpath('//li/span/p')
            }

        @field
        def name(self):
            return self.parsed_object['Name']

        @field
        def email(self):
            return self.parsed_object['E-mail']

    form_text = """
    <li><span>
        <p id="Name">John Doe</p>
        <p id="E-mail">test@test.com</p>
    </span></li>
    """
    mock_detail = MockDetail()

    @requests_mock.Mocker()
    def test_mock_detail(self, mock):
        mock.get('http://test.com/detail', text=self.form_text)
        assert self.mock_detail.is_valid

        fields = self.mock_detail.to_dict()
        assert fields.get('name') == 'John Doe'
        assert fields.get('email') == 'test@test.com'
