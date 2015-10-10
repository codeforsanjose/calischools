import os

from django.conf import settings

def pytest_configure():
    settings.configure(
        INSTALLED_APPS = ('schools',),
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(os.path.dirname(__file__),
                                     'test.sqlite3'),
                'TEST_NAME': os.path.join(os.path.dirname(__file__),
                                          'test.sqlite3')
            }
        }
    )
