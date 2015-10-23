import pytest
import requests_mock
import re

from data.api.cde import (
    MODE_PUBLIC,
    MODE_PRIVATE,
    CdeSchoolSearchForm,
    CdeSchoolSearchList,
    PaginatedCdeSchoolSearchResults,
    CdeSchoolDetail
)
from .test_constants import *

# Regex patterns
ENDPOINT_REGEX = re.compile(r'details\.asp\?cds\=(\d{14})&public=[Y|N]')

@pytest.fixture
def search_form():
    return CdeSchoolSearchForm()

@pytest.fixture
def search_session_token(search_form):
    return search_form.init_search(mode=MODE_PUBLIC)

@pytest.fixture
def search_results_page(search_session_token):
    return PaginatedCdeSchoolSearchResults(token=search_session_token, page=1)

@pytest.fixture
@requests_mock.Mocker()
def public_school_detail(mock):
    mock.get(
        CDE_BASE_URL + CDE_PUBLIC_SCHOOL_ENDPOINT,
        text=CDE_PUBLIC_SCHOOL_DETAIL_HTML
    )
    return CdeSchoolDetail(CDE_PUBLIC_SCHOOL_ENDPOINT).to_dict()

@pytest.fixture
@requests_mock.Mocker()
def private_school_detail(mock):
    mock.get(
        CDE_BASE_URL + CDE_PRIVATE_SCHOOL_ENDPOINT,
        text=CDE_PRIVATE_SCHOOL_DETAIL_HTML
    )
    return CdeSchoolDetail(CDE_PRIVATE_SCHOOL_ENDPOINT).to_dict()

def test_cde_school_search_form(search_form):
    search_form.request_new_form()
    assert search_form.form

def test_cde_school_search_form_token(search_session_token):
    assert search_session_token.get('Cookie')

def test_cde_school_search_results_page(search_results_page):
    results = search_results_page.get_search_results()
    assert len(results) > 1
    assert all(ENDPOINT_REGEX.match(i) for i in results)
    assert search_results_page.next_page

def test_cde_school_search_list():
    school_list = CdeSchoolSearchList(mode=MODE_PRIVATE).schools
    assert len(school_list) > 1


class TestCdeSchoolDetail:
    def test_public_school_detail(self, public_school_detail):
        assert isinstance(public_school_detail, dict)

        code = public_school_detail.get('code')
        assert code

        assert ENDPOINT_REGEX.match(CDE_PUBLIC_SCHOOL_ENDPOINT).group(1) == code

    def test_public_school_detail_phone(self, public_school_detail):
        assert public_school_detail.get('phone') == '(510) 686-4131'

    def test_public_school_detail_name(self, public_school_detail):
        assert public_school_detail.get('name') == 'Community School for Creative Education'

    def test_public_school_detail_status(self, public_school_detail):
        assert public_school_detail.get('status') == 'Active'

    def test_public_school_detail_grades(self, public_school_detail):
        assert public_school_detail.get('low_grade') == 'K'
        assert public_school_detail.get('high_grade') == '8'

    def test_public_school_detail_nces_id(self, public_school_detail):
        assert public_school_detail.get('nces_id') == '12844'

    def test_public_school_detail_county(self, public_school_detail):
        assert public_school_detail.get('county') == 'Alameda'

    def test_public_school_detail_district(self, public_school_detail):
        assert public_school_detail.get('district') == 'Alameda County Office of Education'

    def test_public_school_detail_address(self, public_school_detail):
        assert public_school_detail.get('address') == '2111 International Blvd., Oakland, CA 94606-4903'

    def test_public_school_detail_school_type(self, public_school_detail):
        assert public_school_detail.get('school_type') == 'Elementary Schools (Public)'

    def test_public_school_detail_year_round(self, public_school_detail):
        assert public_school_detail.get('year_round') == 'No'

    def test_public_school_detail_charter(self, public_school_detail):
        assert public_school_detail.get('charter') == 'Yes'

    def test_public_school_detail_charter_number(self, public_school_detail):
        assert public_school_detail.get('charter_number') == '1284'

    def test_public_school_detail_charter_funding(self, public_school_detail):
        assert public_school_detail.get('charter_funding') == 'Directly funded'

    def test_public_school_detail_open_date(self, public_school_detail):
        assert public_school_detail.get('open_date') == '2011-08-22'

    def test_public_school_detail_close_date(self, public_school_detail):
        assert public_school_detail.get('close_date') == ''

    def test_public_school_detail_fax(self, public_school_detail):
        assert public_school_detail.get('fax') == ''

    def test_public_school_detail_email(self, public_school_detail):
        assert public_school_detail.get('email') == 'info@communityschoolforcreativeeducation.org'

    def test_public_school_detail_website(self, public_school_detail):
        assert public_school_detail.get('website') == 'http://www.communityschoolforcreativeeducation.org'

    def test_public_school_detail_administrators(self, public_school_detail):
        assert public_school_detail.get('administrators') == 'Kathryn Wilson\nPrincipal\n(510) 686-4131\nkathrynw@communityschoolforcreativeeducation.org'

    def test_public_school_detail_mailing_address(self, public_school_detail):
        assert public_school_detail.get('mailing_address') == '2111 International Blvd., Oakland, CA 94606-4903'

    def test_public_school_detail_stats(self, public_school_detail):
        assert public_school_detail.get('stats') == 'http://data1.cde.ca.gov/dataquest/DQReports.asp?CDSType=S&CDSCode=01100170123968'

    def test_private_school_detail_district(self, private_school_detail):
        assert private_school_detail.get('district') == 'Davis Joint Unified'

    def test_private_school_detail_close_date(self, private_school_detail):
        assert private_school_detail.get('close_date') == '2008-11-10'
