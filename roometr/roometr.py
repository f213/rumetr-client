import requests

from . import exceptions

TIMEOUT = 3
API_HOST = 'https://roometr.com/api/v1/'


class Roometr:
    """
    The client for the rumetr.com internal database. Use it to update our data with your scraper.
    """
    def __init__(self, auth_key: str, developer: str, api_host=API_HOST):
        self._last_checked_developer = None
        self._checked_complexes = set()
        self._checked_houses = set()

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
        """
        Do a POST request
        """
        r = requests.post(self._format_url(url), data=data, headers=self.headers, timeout=TIMEOUT)
        self._check_response(r, expected_status_code)

        return r.json()

    def get(self, url):
        """
        Do a GET request
        """
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

    def check_developer(self) -> bool:
        """
        Check if a given developer exists in the roometr database
        """
        if self._last_checked_developer == self.developer:
            return True

        try:
            self.get('developers/%s/' % self.developer)
        except exceptions.Roometr404Exception:
            raise exceptions.RoometrDeveloperNotFound('Bad developer id — rumetr server does not know it. Is it correct?')

        self._last_checked_developer = self.developer
        return True

    def check_complex(self, complex: str) -> bool:
        """
        Check if a given complex exists in the roometr database
        """
        self.check_developer()
        if complex in self._checked_complexes:
            return True

        try:
            self.get('developers/{developer}/complexes/{complex}/'.format(
                developer=self.developer,
                complex=complex,
            ))
        except exceptions.Roometr404Exception:
            raise exceptions.RoometrComplexNotFound('Unknown complex — maybe you should create one?')

        self._checked_complexes.add(complex)
        return True

    def check_house(self, complex: str, house: str) -> bool:
        """
        Check if given house exists in the roometr database
        """
        self.check_complex(complex)
        if house in self._checked_houses:
            return True

        try:
            self.get('developers/{developer}/complexes/{complex}/houses/{house}/'.format(
                developer=self.developer,
                complex=complex,
                house=house,
            ))
        except exceptions.Roometr404Exception:
            raise exceptions.RoometrHouseNotFound('Unknown house (complex is known) — may be you should create one?')

        self._checked_houses.add(house)
        return True

    def add_complex(self, **kwargs):
        """
        STUB YET! Add a complex to the rumetr db
        """
        self.check_developer()
        self.post('developers/%s/complexes/' % self.developer, data=kwargs)

    def add_house(self, complex: str, **kwargs):
        self.check_complex(complex)
        self.post('developers/{developer}/complexes/{complex}/houses/'.format(developer=self.developer, complex=complex), data=kwargs)
