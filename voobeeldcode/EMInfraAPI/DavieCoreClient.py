from voobeeldcode.EMInfraAPI.AbstractRequester import AbstractRequester


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
            yield from result_dict['data']

            if result_dict['links'].get('next') is None:
                break

            _from += size

    def historiek_by_aanlevering_id(self, id) -> [dict]:
        url = f'aanleveringen/{id}/historiek'
        response = self.requester.get(url=url)
        return response.json()




