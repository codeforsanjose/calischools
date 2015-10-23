from data.api.cde import CdeAPI
from .utils import fixture, json_fixture

CDE_BASE_URL = CdeAPI().base_url
CDE_PUBLIC_SCHOOL_ENDPOINT = 'details.asp?cds=01100170123968&public=Y'
CDE_PRIVATE_SCHOOL_ENDPOINT = 'details.asp?cds=57726787099492&public=N'
CDE_PUBLIC_SCHOOL_DETAIL_HTML = fixture('public_school_detail.html')
CDE_PRIVATE_SCHOOL_DETAIL_HTML = fixture('private_school_detail.html')
CDE_SCHOOL_DETAIL_JSON = json_fixture('school_fixtures.json')
