import csv

from voobeeldcode.EMInfraAPI.DavieCoreClient import DavieCoreClient
from voobeeldcode.EMInfraAPI.RequesterFactory import RequesterFactory
from voobeeldcode.Enums import AuthType, Environment

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


if __name__ == '__main__':
    requester = RequesterFactory.create_requester(cookie='d9b0fdba990a4891a450d80c6c99ab62', auth_type=AuthType.COOKIE,
                                                  env=Environment.PRD)
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
