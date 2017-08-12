import requests

from . import exceptions

TIMEOUT = 3
API_HOST = 'https://roometr.com/api/v1/'


class Roometr:
    """
    The client for the rumetr.com internal database. Use it to update our data with your scraper.
    """
    def complex_exists(self, complex: str) -> bool:
        """
        Shortcut to check if complex exists in our database.
        """
        try:
            self.check_complex(complex)
        except exceptions.RoometrComplexNotFound:
            return False

        return True

    def house_exists(self, complex: str, house: str) -> bool:
        """
        Shortcut to check if house exists in our database.
        """
        try:
            self.check_house(complex, house)
        except exceptions.RoometrHouseNotFound:
            return False

        return True

    def appt_exists(self, complex: str, house: str, appt: str) -> bool:
        """
        Shortcut to check if appt exists in our database.
        """
        try:
            self.check_appt(complex, house, appt)
        except exceptions.RoometrApptNotFound:
            return False

        return True

    def __init__(self, auth_key: str, developer: str, api_host=API_HOST):
        self._initialize_cache()

        self.api_host = api_host
        self.developer = developer
        self.headers = {
            'Authorization': 'Token %s' % auth_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _initialize_cache(self):
        self._last_checked_developer = None
        self._checked_complexes = set()
        self._checked_houses = set()
        self._checked_appts = set()

    def _format_url(self, endpoint):
        """
        Append the API host
        """
        return (self.api_host + '/%s/' % endpoint).replace('//', '/').replace(':/', '://')

    def post(self, url: str, data: str, expected_status_code=201):
        """
        Do a POST request
        """
        r = requests.post(self._format_url(url), json=data, headers=self.headers, timeout=TIMEOUT)
        self._check_response(r, expected_status_code)

        return r.json()

    def put(self, url: str, data: str, expected_status_code=202):
        """
        Do a PUT request
        """
        r = requests.put(self._format_url(url), json=data, headers=self.headers, timeout=TIMEOUT)
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
            raise exceptions.RoometrBadServerResponseException('Got response code %d, expected %d, error: %s' % (response.status_code, expected_status_code, response.text))

    def check_developer(self) -> bool:
        """
        Check if a given developer exists in the rumetr database
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
        Check if a given complex exists in the rumetr database
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
        Check if given house exists in the rumetr database
        """
        self.check_complex(complex)
        if '%s__%s' % (complex, house) in self._checked_houses:
            return True

        try:
            self.get('developers/{developer}/complexes/{complex}/houses/{house}/'.format(
                developer=self.developer,
                complex=complex,
                house=house,
            ))
        except exceptions.Roometr404Exception:
            raise exceptions.RoometrHouseNotFound('Unknown house (complex is known) — may be you should create one?')

        self._checked_houses.add('%s__%s' % (complex, house))
        return True

    def check_appt(self, complex: str, house: str, appt: str) -> bool:
        """
        Check if given appartment exists in the rumetr database
        """
        self.check_house(complex, house)
        if '%s__%s__%s' % (complex, house, appt) in self._checked_appts:
            return True

        try:
            self.get('developers/{developer}/complexes/{complex}/houses/{house}/appts/{appt}'.format(
                developer=self.developer,
                complex=complex,
                house=house,
                appt=appt,
            ))
        except exceptions.Roometr404Exception:
            raise exceptions.RoometrApptNotFound('Unknown appt (house is known) — may be you should create one?')

        self._checked_appts.add('%s__%s__%s' % (complex, house, appt))
        return True

    def add_complex(self, **kwargs):
        """
        Add a new complex to the rumetr db
        """
        self.check_developer()
        self.post('developers/%s/complexes/' % self.developer, data=kwargs)

    def add_house(self, complex: str, **kwargs):
        """
        Add a new house to the rumetr db
        """
        self.check_complex(complex)
        self.post('developers/{developer}/complexes/{complex}/houses/'.format(developer=self.developer, complex=complex), data=kwargs)

    def add_appt(self, complex: str, house: str, **kwargs):
        """
        Add a new appartment to the rumetr db
        """
        self.check_house(complex, house)
        self.post('developers/{developer}/complexes/{complex}/houses/{house}/appts/'.format(
            developer=self.developer,
            complex=complex,
            house=house,
        ), data=kwargs)

    def update_appt(self, complex: str, house: str, **kwargs):
        """
        Update existing appartment
        """
        self.check_house(complex, house)
        self.put('developers/{developer}/complexes/{complex}/houses/{house}/appts/'.format(
            developer=self.developer,
            complex=complex,
            house=house,
        ), data=kwargs)
