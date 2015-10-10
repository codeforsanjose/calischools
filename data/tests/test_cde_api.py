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
def cde_school_detail(mock):
    mock.get(CDE_BASE_URL + CDE_SCHOOL_ENDPOINT, text=CDE_SCHOOL_DETAIL_HTML)
    return CdeSchoolDetail(CDE_SCHOOL_ENDPOINT).to_dict()

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
    def test_cde_school_detail(self, cde_school_detail):
        assert isinstance(cde_school_detail, dict)

        code = cde_school_detail.get('code')
        assert code

        assert ENDPOINT_REGEX.match(CDE_SCHOOL_ENDPOINT).group(1) == code

    def test_cde_school_detail_phone(self, cde_school_detail):
        assert cde_school_detail.get('phone') == '(510) 670-6619'

    def test_cde_school_detail_name(self, cde_school_detail):
        assert cde_school_detail.get('name') == 'Alameda County Community'

    def test_cde_school_detail_status(self, cde_school_detail):
        assert cde_school_detail.get('status') == 'Active'

    def test_cde_school_detail_grades(self, cde_school_detail):
        assert cde_school_detail.get('low_grade') == 'K'
        assert cde_school_detail.get('high_grade') == ''

    def test_cde_school_detail_nces_id(self, cde_school_detail):
        assert cde_school_detail.get('nces_id') == '06830'

    def test_cde_school_detail_county(self, cde_school_detail):
        assert cde_school_detail.get('county') == 'Alameda'

    def test_cde_school_detail_district(self, cde_school_detail):
        assert cde_school_detail.get('district') == 'Alameda County Office of Education'

    def test_cde_school_detail_address(self, cde_school_detail):
        assert cde_school_detail.get('address') == '313 West Winton Ave., Hayward, CA 94544-1136'
