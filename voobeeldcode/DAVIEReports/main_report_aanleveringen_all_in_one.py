filters = {
    # "statusSubstatusCombinaties":
    #     [{"status": "IN_OPMAAK", "substatus": None},
    #      {"status": "DATA_AANGEVRAAGD", "substatus": "BESCHIKBAAR"},
    #      {"status": "DATA_AANGELEVERD", "substatus": "GOEDGEKEURD"}],
    # "creatieDatumVan": "2024-04-26",
    "verbergElisaAanleveringen": True
}

awv_acm_cookie = '603959beece74e59aa330a7ccd260095'
voId = '5f072415-c0f2-4259-af91-05d65c15286a'  # zie https://apps.mow.vlaanderen.be/eminfra/admin/gebruikers


import csv
import abc
from enum import Enum
from requests import Response, Session


class Environment(Enum):
    PRD = 'prd',
    DEV = 'dev',
    TEI = 'tei',
    AIM = 'aim'


class AuthType(Enum):
    JWT = 'JWT',
    CERT = 'cert',
    COOKIE = 'cookie'


class AbstractRequester(Session, metaclass=abc.ABCMeta):
    def __init__(self, first_part_url: str = ''):
        super().__init__()
        self.first_part_url = first_part_url

    @abc.abstractmethod
    def get(self, url: str = '', **kwargs) -> Response:
        return super().get(url=self.first_part_url + url, **kwargs)

    @abc.abstractmethod
    def post(self, url: str = '', **kwargs) -> Response:
        return super().post(url=self.first_part_url + url, **kwargs)

    @abc.abstractmethod
    def put(self, url: str = '', **kwargs) -> Response:
        return super().put(url=self.first_part_url + url, **kwargs)

    @abc.abstractmethod
    def patch(self, url: str = '', **kwargs) -> Response:
        return super().patch(url=self.first_part_url + url, **kwargs)

    @abc.abstractmethod
    def delete(self, url: str = '', **kwargs) -> Response:
        return super().delete(url=self.first_part_url + url, **kwargs)


class RequesterFactory:
    first_part_url_dict = {
        Environment.PRD: 'https://services.apps.mow.vlaanderen.be/',
        Environment.TEI: 'https://services.apps-tei.mow.vlaanderen.be/',
        Environment.DEV: 'https://services.apps-dev.mow.vlaanderen.be/',
        Environment.AIM: 'https://services-aim.apps-dev.mow.vlaanderen.be/'
    }

    @classmethod
    def create_requester(cls, auth_type: AuthType, env: Environment, settings: dict = None, **kwargs
                         ) -> AbstractRequester:

        try:
            first_part_url = cls.first_part_url_dict[env]
        except KeyError as exc:
            raise ValueError(f"Invalid environment: {env}") from exc

        if auth_type == AuthType.COOKIE:
            return CookieRequester(cookie=kwargs['cookie'], first_part_url=first_part_url.replace('services.',
                                                                                                  ''))
        else:
            raise ValueError(f"Invalid authentication type: {auth_type}")


class DavieCoreClient:
    def __init__(self, requester: AbstractRequester):
        self.requester = requester
        self.requester.first_part_url += 'davie-aanlevering/api/'

    def aanlevering_by_id(self, id: str) -> dict:
        url = f'aanleveringen/{id}'
        response = self.requester.get(url=url)
        return response.json()

    def zoek_aanleveringen(self, filter_dict: dict) -> [dict]:
        _from = 0
        size = 100
        if filter_dict.get('sortBy') is None:
            filter_dict['sortBy'] = {"property": "creatieDatum", "order": "desc"}

        while True:
            url = f'aanleveringen/zoek?from={_from}&size={size}'
            response = self.requester.post(url=url, json=filter_dict)

            print(f'fetched up to {size} results from {url}')

            result_dict = response.json()
            yield from result_dict['data']

            if result_dict['links'].get('next') is None:
                break

            _from += size

    def historiek_by_aanlevering_id(self, id) -> [dict]:
        url = f'aanleveringen/{id}/historiek'
        response = self.requester.get(url=url)
        return response.json()


class TakenClient:
    def __init__(self, requester: AbstractRequester):
        self.requester = requester
        self.requester.first_part_url += 'takenservice/rest/awv-internal/taak/'

    def get_niet_afgesloten(self) -> [dict]:
        filter_dict = {"ascending": False, "statussen": ["BEZIG", "IN_WACHT", "UIT_TE_VOEREN"], "page": 0,
                       "pageSize": 1000, "voId": "6c2b7c0a-11a9-443a-a96b-a1bec249c629",
                       "typeKeys": ["aanlevering", "verificatie"], "metadata": [], "sortFieldNames": []}
        url = 'zoek'
        total = -1
        counted = 0
        while total == -1 or counted < total:
            response = self.requester.post(url=url, json=filter_dict)

            result_dict = response.json()
            total = result_dict['total']
            counted += filter_dict['pageSize']
            yield from result_dict['items']

            filter_dict['page'] += 1


class CookieRequester(AbstractRequester):
    def __init__(self, cookie: str = '', first_part_url: str = ''):
        super().__init__(first_part_url=first_part_url)
        self.cookie = cookie
        self.headers.update({'Cookie': f'acm-awv={cookie}'})

    def get(self, url: str = '', **kwargs) -> Response:
        return super().get(url=url, **kwargs)

    def post(self, url: str = '', **kwargs) -> Response:
        return super().post(url=url, **kwargs)

    def put(self, url: str = '', **kwargs) -> Response:
        return super().put(url=url, **kwargs)

    def patch(self, url: str = '', **kwargs) -> Response:
        return super().patch(url=url, **kwargs)

    def delete(self, url: str = '', **kwargs) -> Response:
        return super().delete(url=url, **kwargs)


if __name__ == '__main__':
    requester_davie = RequesterFactory.create_requester(
        cookie=awv_acm_cookie, auth_type=AuthType.COOKIE, env=Environment.PRD)
    davie_client = DavieCoreClient(requester=requester_davie)
    requester_taken = RequesterFactory.create_requester(
        cookie=awv_acm_cookie, auth_type=AuthType.COOKIE, env=Environment.PRD)

    taken_client = TakenClient(requester=requester_taken)
    taken_dict = {taak['identificatieLabel']: taak for taak in taken_client.get_niet_afgesloten()}

    with open('aanleveringen_rapport.csv', 'w', newline='') as csvfile:
        headers = ['aanleveringnummer', 'type', 'status', 'substatus', 'aanmaakDatum', 'aanvrager', 'referentie',
                   'onderneming', 'id', 'dossierNummer', 'besteknummer', 'dienstbevelnummer', 'opmaakDatum',
                   'aangebodenDatum', 'goedgekeurdDatum', 'verificatieDringend', 'verificatieToegekendAan',
                   'verificatieStatus', 'isStudie', 'ondernemingsnummer', 'vervalOfEinddatum', 'afgekeurdDatum',
                   'geannuleerdDatum', 'vervallenDatum', 'omschrijving']
        writer = csv.DictWriter(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL, fieldnames=headers)
        writer.writeheader()

        for aanlevering in davie_client.zoek_aanleveringen(filter_dict=filters):
            aanlevering_dict = aanlevering['aanlevering']
            aanlevering_dict['onderneming'] = aanlevering_dict['ondernemingInfo']['naam']
            aanlevering_dict['ondernemingsnummer'] = aanlevering_dict['ondernemingInfo']['ondernemingsnummer']
            del aanlevering_dict['ondernemingInfo']
            aanlevering_dict['aanmaakDatum'] = aanlevering_dict['aanmaakDatum'].split('T')[0]

            aanlevering_historiek = davie_client.historiek_by_aanlevering_id(id=aanlevering_dict['id'])
            aanlevering_dict['opmaakDatum'] = next(
                (x['tijdstip'] for x in aanlevering_historiek if x['status'] == 'IN_OPMAAK'), None)
            aanlevering_dict['aangebodenDatum'] = next(
                (x['tijdstip'] for x in aanlevering_historiek
                 if x['status'] == 'DATA_AANGELEVERD' and x['substatus'] == 'AANGEBODEN'), None)
            aanlevering_dict['goedgekeurdDatum'] = next(
                (x['tijdstip'] for x in aanlevering_historiek
                 if x['status'] == 'DATA_AANGELEVERD' and x['substatus'] == 'GOEDGEKEURD'), None)
            aanlevering_dict['afgekeurdDatum'] = next(
                (x['tijdstip'] for x in aanlevering_historiek
                 if x['status'] == 'DATA_AANGELEVERD' and x['substatus'] == 'AFGEKEURD'), None)
            aanlevering_dict['geannuleerdDatum'] = next(
                (x['tijdstip'] for x in aanlevering_historiek if x['status'] == 'GEANNULEERD'), None)
            aanlevering_dict['vervallenDatum'] = next(
                (x['tijdstip'] for x in aanlevering_historiek if x['status'] == 'VERVALLEN'), None)

            del aanlevering_dict['id']
            del aanlevering_dict['opmaakDatum']

            taak_details = taken_dict.get(aanlevering_dict['aanleveringnummer'])
            if taak_details is not None:
                aanlevering_dict['verificatieToegekendAan'] = taak_details['toegekendAanNaam']
                aanlevering_dict['verificatieStatus'] = taak_details['status']

            writer.writerow(aanlevering_dict)
