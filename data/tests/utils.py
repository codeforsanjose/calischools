import os
import json

MODULE_DIR = os.path.dirname(__file__)
FIXTURES_DIR = os.path.join(MODULE_DIR, 'test_fixtures')

def fixture(file_path, base_dir=FIXTURES_DIR):
    full_path = os.path.join(base_dir, file_path)
    return open(full_path, 'rU').read()

def json_fixture(file_path, base_dir=FIXTURES_DIR):
    return json.loads(fixture(file_path, base_dir))
