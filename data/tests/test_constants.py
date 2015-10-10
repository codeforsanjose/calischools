from data.api.cde import CdeAPI
from .utils import fixture, json_fixture

CDE_BASE_URL = CdeAPI().base_url
CDE_SCHOOL_ENDPOINT = 'details.asp?cds=01100170130419&public=Y'
CDE_SCHOOL_DETAIL_HTML = fixture('school_detail.html')
CDE_SCHOOL_DETAIL_JSON = json_fixture('school_fixtures.json')
