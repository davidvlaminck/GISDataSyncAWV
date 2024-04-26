import abc
import csv
from enum import Enum

from requests import Session, Response

filters = {
    "besteknummer": "VWT/EW/2020/024",
    #   "aanvragers": "[b78943b8-caaf-426a-ade9-773e55801434]",
    #   "statusSubstatusCombinaties": "[IN_OPMAAK]",
    #   "creatieDatumVan": "2024-04-26",
    #   "creatieDatumTot": "2024-04-26",
    #   "vrijeZoekterm": "string",
    #   "verbergElisaAanleveringen": true,
    #   "ondernemingsnummer": "0687738908",
    #   "dienstbevelnummer": "string",
    #   "betrokkenen": "[b78943b8-caaf-426a-ade9-773e55801434]",
    #   "type": "Studie"
    #
}
cookie = 'd9b0fdba990a4891a450d80c6c99ab62'


class Environment(Enum):
    PRD = 'prd',
    DEV = 'dev',
    TEI = 'tei',
    AIM = 'aim'


class AbstractRequester(Session, metaclass=abc.ABCMeta):
    def __init__(self, first_part_url: str = ''):
        super().__init__()
        self.first_part_url = first_part_url

    @abc.abstractmethod
    def get(self, url: str = '', **kwargs) -> Response:
        print(f'url: {self.first_part_url}{url}')
        return super().get(url=self.first_part_url + url, **kwargs)

    @abc.abstractmethod
    def post(self, url: str = '', **kwargs) -> Response:
        print(f'url: {self.first_part_url}{url}')
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


class RequesterFactory:
    first_part_url_dict = {
        Environment.PRD: 'https://services.apps.mow.vlaanderen.be/',
        Environment.TEI: 'https://services.apps-tei.mow.vlaanderen.be/',
        Environment.DEV: 'https://services.apps-dev.mow.vlaanderen.be/',
        Environment.AIM: 'https://services-aim.apps-dev.mow.vlaanderen.be/'
    }

    @classmethod
    def create_requester(cls, env: Environment, **kwargs
                         ) -> AbstractRequester:
        try:
            first_part_url = cls.first_part_url_dict[env]
        except KeyError as exc:
            raise ValueError(f"Invalid environment: {env}") from exc

        return CookieRequester(cookie=kwargs['cookie'], first_part_url=first_part_url.replace('services.', ''))


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

        results = []
        while True:
            url = f'aanleveringen/zoek?from={_from}&size={size}'
            response = self.requester.post(url=url, json=filter_dict)

            result_dict = response.json()
            results.extend(result_dict['data'])

            if result_dict['links'].get('next') is None:
                break

            _from += size

        return results

    def historiek_by_aanlevering_id(self, id) -> [dict]:
        url = f'aanleveringen/{id}/historiek'
        response = self.requester.get(url=url)
        return response.json()


if __name__ == '__main__':
    requester = RequesterFactory.create_requester(cookie=cookie, env=Environment.PRD)
    davie_client = DavieCoreClient(requester=requester)

    aanleveringen = davie_client.zoek_aanleveringen(filter_dict=filters)

    with open('aanleveringen_rapport.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ['Nummer aanlevering', 'Datum/tijd aanlevering', 'Gestart door', 'Verificator bij creatie',
             'Contact AWV', 'Dossier', 'Bestek', 'Dienstbevel', 'Eigen referentie', 'Status', 'Datum/tijd goedkeuring',
             'Goedgekeurd door'])
        for aanlevering in aanleveringen:
            aanlevering_dict = aanlevering['aanlevering']
            aanlevering_details = davie_client.aanlevering_by_id(id=aanlevering['aanlevering']['id'])['aanlevering']
            verificateur = ''
            if aanlevering_details['info'].get('standaardVerificator'):
                verificateur = f"{aanlevering_details['info']['standaardVerificator']['voornaam']} {
                aanlevering_details['info']['standaardVerificator']['naam']}".rstrip()
            awv_contact = ''
            if aanlevering_details['info'].get('awvContactInfo'):
                awv_contact = f"{aanlevering_details['info']['awvContactInfo']['gebruiker']['voornaam']} {
                aanlevering_details['info']['awvContactInfo']['gebruiker']['naam']}".rstrip()

            datumtijd_goedkeuring = ''
            goedgekeurd_door = ''
            if aanlevering_dict['status'] == 'DATA_AANGELEVERD' and aanlevering_dict['substatus'] == 'GOEDGEKEURD':
                historiek = davie_client.historiek_by_aanlevering_id(id=aanlevering_dict['id'])
                goedkeuring = next((a for a in historiek if a['status'] == 'DATA_AANGELEVERD' and
                                    a['substatus'] == 'GOEDGEKEURD' and a['volledigeNaam'] != 'Systeem'), None)
                if goedkeuring is not None:
                    datumtijd_goedkeuring = goedkeuring['tijdstip']
                    goedgekeurd_door = goedkeuring['volledigeNaam']

            writer.writerow([
                aanlevering_dict['aanleveringnummer'],
                aanlevering_dict['aanmaakDatum'],
                aanlevering_dict['aanvrager'],
                verificateur,
                awv_contact,
                aanlevering_dict['dossierNummer'],
                aanlevering_dict['besteknummer'],
                aanlevering_dict.get('dienstbevelnummer', ''),
                aanlevering_dict['referentie'],
                f"{aanlevering_dict['status']} {aanlevering_dict.get('substatus', '')}".rstrip(),
                datumtijd_goedkeuring,
                goedgekeurd_door
            ])
