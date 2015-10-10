import requests

from lxml import html
from .errors import APIError


class ExternalAPI(object):
    base_url = None
    endpoint = None

    def get_base_url(self):
        assert self.base_url is not None, (
            '%r should either include a `base_url` attribute, '
            'or override the `get_base_url()` method.'
            % self.__class__.__name__
        )

        return self.base_url

    def get_endpoint(self):
        assert self.endpoint is not None, (
            '%r should either include a `endpoint` attribute, '
            'or override the `get_endpoint()` method.'
            % self.__class__.__name__
        )

        return self.endpoint

    def api_call(self, endpoint=None, **kwargs):
        return (
            self.get_base_url() +
            (endpoint or self.get_endpoint()).format(**kwargs)
        )

    def request(self,
                url=None,
                method='GET',
                params=None,
                data=None,
                headers=None,
                **kwargs):
        url = url or self.api_call(**kwargs)
        response = requests.request(method,
                                    url,
                                    params=params,
                                    data=data,
                                    headers=headers)
        if response.status_code != requests.codes.ok:
            raise APIError(
                'ERROR: <{status} {message}> while accessing URL: '
                '<Requested: {requested_url}, Final: {final_url}>'.format(
                    status=response.status_code,
                    message=response.reason,
                    requested_url=url,
                    final_url=response.url
                )
            )

        return response


class SearchFormMixin(object):
    form_id = None

    form_page = None
    form = None

    def _get_form_by_id(self):
        assert self.form_page is not None, 'Non-existent or invalid form page.'
        forms_in_page = html.fromstring(self.form_page.text).forms
        for form in forms_in_page:
            if form.get('id') == self.get_form_id():
                return form

    def get_form_id(self):
        assert self.form_id is not None, (
            '%r should either include a `form_id` attribute, '
            'or override the `get_form_id()` method.'
            % self.__class__.__name__
        )

        return self.form_id

    def request_new_form(self):
        self.form_page = self.request()
        self.form = self._get_form_by_id()

    def update_form(self, field_values):
        # Update form action
        self.form.action = self.api_call(self.form.action)

        # Update form fields
        self.form.fields.update(field_values)


class FieldParserMixin(object):
    parsed_object = None

    def _get_fields(self):
        for i in dir(self):
            attr = getattr(self, i)
            if hasattr(attr, '__field__'):
                yield i, attr()

    def parse(self):
        raise NotImplementedError(
            '%r should override the `parse()` method.'
            % self.__class__.__name__
        )

    @property
    def is_valid(self):
        if self.parsed_object is None:
            self.parse()

        return bool(self.parsed_object)

    def to_dict(self):
        if self.is_valid:
            return dict(self._get_fields())
