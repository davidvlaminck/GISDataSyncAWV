from voobeeldcode.EMInfraAPI.AbstractRequester import AbstractRequester


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
