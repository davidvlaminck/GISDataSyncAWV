import csv

from voobeeldcode.EMInfraAPI.DavieCoreClient import DavieCoreClient
from voobeeldcode.EMInfraAPI.RequesterFactory import RequesterFactory
from voobeeldcode.EMInfraAPI.TakenClient import TakenClient
from voobeeldcode.Enums import AuthType, Environment

filters = {
    # "statusSubstatusCombinaties":
    #     [{"status": "IN_OPMAAK", "substatus": None},
    #      {"status": "DATA_AANGEVRAAGD", "substatus": "BESCHIKBAAR"},
    #      {"status": "DATA_AANGELEVERD", "substatus": "GOEDGEKEURD"}],
    # "creatieDatumVan": "2024-04-26",
    "verbergElisaAanleveringen": True
    #   "creatieDatumTot": "2024-04-26",
}

if __name__ == '__main__':
    requester_davie = RequesterFactory.create_requester(cookie='603959beece74e59aa330a7ccd260095',
                                                        auth_type=AuthType.COOKIE,
                                                        env=Environment.PRD)
    davie_client = DavieCoreClient(requester=requester_davie)
    requester_taken = RequesterFactory.create_requester(cookie='603959beece74e59aa330a7ccd260095',
                                                        auth_type=AuthType.COOKIE,
                                                        env=Environment.PRD)

    taken_client = TakenClient(requester=requester_taken)
    taken_dict = {taak['identificatieLabel']: taak for taak in taken_client.get_niet_afgesloten()}

    with open('taken_rapport.csv', 'w', newline='') as csvfile:
        headers = ['creatieTijdstip', 'machtigingen', 'omschrijving', 'metadata', 'linken', 'locaties',
                   'aangemaaktDoorVoId', 'typeKey', 'eigenaarToepassing', 'aangemaaktDoorNaam', 'uitvoerenVoorDeadline',
                   'deadline', 'toegekendAanVoId', 'typeLabel', 'status', 'dringend', 'identificatieLabel',
                   'toegekendAanNaam', 'id', 'statuswijzigingen']
        writer = csv.DictWriter(csvfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL, fieldnames=headers)
        writer.writeheader()

        for taak_dict in taken_dict.values():
            writer.writerow(taak_dict)

    with open('aanleveringen_rapport.csv', 'w', newline='') as csvfile:
        headers = ['aanleveringnummer', 'type', 'status', 'substatus', 'aanmaakDatum', 'vervalOfEinddatum',
                   'aanvrager', 'referentie', 'ondernemingsnummer', 'onderneming', 'id', 'omschrijving', 'isStudie',
                   'dossierNummer', 'besteknummer', 'dienstbevelnummer', 'opmaakDatum', 'aangebodenDatum',
                   'goedgekeurdDatum', 'afgekeurdDatum', 'geannuleerdDatum', 'vervallenDatum',
                   'verificatieDringend', 'verificatieToegekendAan', 'verificatieStatus']
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
            aanlevering_dict['aangebodenDatum'] = next((x['tijdstip'] for x in aanlevering_historiek if
                                                        x['status'] == 'DATA_AANGELEVERD' and x[
                                                            'substatus'] == 'AANGEBODEN'), None)
            aanlevering_dict['goedgekeurdDatum'] = next((x['tijdstip'] for x in aanlevering_historiek if
                                                         x['status'] == 'DATA_AANGELEVERD' and x[
                                                             'substatus'] == 'GOEDGEKEURD'), None)
            aanlevering_dict['afgekeurdDatum'] = next((x['tijdstip'] for x in aanlevering_historiek if
                                                       x['status'] == 'DATA_AANGELEVERD' and x[
                                                           'substatus'] == 'AFGEKEURD'), None)
            aanlevering_dict['geannuleerdDatum'] = next(
                (x['tijdstip'] for x in aanlevering_historiek if x['status'] == 'GEANNULEERD'), None)
            aanlevering_dict['vervallenDatum'] = next(
                (x['tijdstip'] for x in aanlevering_historiek if x['status'] == 'VERVALLEN'), None)

            taak_details = taken_dict.get(aanlevering_dict['aanleveringnummer'])
            if taak_details is not None:
                aanlevering_dict['verificatieToegekendAan'] = taak_details['toegekendAanNaam']
                aanlevering_dict['verificatieStatus'] = taak_details['status']
                aanlevering_dict['verificatieDringend'] = taak_details['dringend']

            writer.writerow(aanlevering_dict)
            #
            # aanlevering_details = davie_client.aanlevering_by_id(id=aanlevering['aanlevering']['id'])['aanlevering']
            # verificateur = ''
            # if aanlevering_details['info'].get('standaardVerificator'):
            #     verificateur = f"{aanlevering_details['info']['standaardVerificator']['voornaam']} {
            #     aanlevering_details['info']['standaardVerificator']['naam']}".rstrip()
            # awv_contact = ''
            # if aanlevering_details['info'].get('awvContactInfo'):
            #     awv_contact = f"{aanlevering_details['info']['awvContactInfo']['gebruiker']['voornaam']} {
            #     aanlevering_details['info']['awvContactInfo']['gebruiker']['naam']}".rstrip()
            #
            # datumtijd_goedkeuring = ''
            # goedgekeurd_door = ''
            # if aanlevering_dict['status'] == 'DATA_AANGELEVERD' and aanlevering_dict['substatus'] == 'GOEDGEKEURD':
            #     historiek = davie_client.historiek_by_aanlevering_id(id=aanlevering_dict['id'])
            #     goedkeuring = next((a for a in historiek if a['status'] == 'DATA_AANGELEVERD' and
            #                         a['substatus'] == 'GOEDGEKEURD' and a['volledigeNaam'] != 'Systeem'), None)
            #     if goedkeuring is not None:
            #         datumtijd_goedkeuring = goedkeuring['tijdstip']
            #         goedgekeurd_door = goedkeuring['volledigeNaam']

            # writer.writerow([
            #     aanlevering_dict['aanleveringnummer'],
            #     aanlevering_dict['aanmaakDatum'],
            #     aanlevering_dict['aanvrager'],
            #     verificateur,
            #     awv_contact,
            #     aanlevering_dict['dossierNummer'],
            #     aanlevering_dict['besteknummer'],
            #     aanlevering_dict.get('dienstbevelnummer', ''),
            #     aanlevering_dict['referentie'],
            #     f"{aanlevering_dict['status']} {aanlevering_dict.get('substatus', '')}".rstrip(),
            #     datumtijd_goedkeuring,
            #     goedgekeurd_door
            # ])
