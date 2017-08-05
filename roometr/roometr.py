import requests

from . import exceptions

TIMEOUT = 3
API_HOST = 'https://roometr.com/api/v1/'


class Roometr:

    def __init__(self, auth_key: str, developer: str, api_host=API_HOST):
        self._last_checked_developer = None

        self.api_host = api_host
        self.developer = developer
        self.headers = {
            'Authorization': 'Token %s' % auth_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _format_url(self, endpoint):
        """
        Append the API host
        """
        return (self.api_host + '/%s/' % endpoint).replace('//', '/').replace(':/', '://')

    def post(self, url: str, data: str, expected_status_code=202):
        r = requests.post(self._format_url(url), data=data, headers=self.headers, timeout=TIMEOUT)
        self._check_response(r, expected_status_code)

        return r.json()

    def get(self, url):
        r = requests.get(self._format_url(url), headers=self.headers, timeout=TIMEOUT)
        self._check_response(r, 200)

        return r.json()

    def _check_response(self, response, expected_status_code):
        if response.status_code == 404:
            raise exceptions.Roometr404Exception()

        if response.status_code == 403:
            raise exceptions.Roometr403Exception()

        if response.status_code != expected_status_code:
            raise exceptions.RoometrBadServerResponseException('Got response code %d, expected %d' % (response.status_code, expected_status_code))

    def check_developer(self):
        if self._last_checked_developer == self.developer:
            return True

        try:
            self.get('developers/%s/' % self.developer)
        except exceptions.Roometr404Exception:
            raise exceptions.RoometrDeveloperNotFound('Bad developer id — rumetr server does not know it. Is it correct?')

        self._last_checked_developer = self.developer
        return True
