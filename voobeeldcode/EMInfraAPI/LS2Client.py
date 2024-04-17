import json
from typing import Iterator, Generator

from requests import Response

from voobeeldcode.EMInfraAPI.AbstractRequester import AbstractRequester
from voobeeldcode.EMInfraAPI.ZoekParameterOTL import ZoekParameterOTL


class LS2Client:
    def __init__(self, requester: AbstractRequester):
        self.requester = requester
        self.requester.first_part_url += 'locatieservices2/rest/'

    def measure_punt_op_weg(self, wegnummer: str, x: float, y: float, crs: int = 31370) -> dict:
        url = f'weg/{wegnummer}/measure?crs={crs}&x={x}&y={y}'
        response = self.requester.get(url=url)
        return response.json()

    def wegsegment_by_id(self, id: str) -> dict:
        url = f'wegsegment/{id}'
        response = self.requester.get(url=url)
        return response.json()

