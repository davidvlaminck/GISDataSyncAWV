import json
from typing import Iterator, Generator

from requests import Response

from voobeeldcode.EMInfraAPI.RequestHandler import RequestHandler


class EMInfraImporter:
    def __init__(self, request_handler: RequestHandler):
        self.request_handler = request_handler
        self.request_handler.requester.first_part_url += 'eminfra/'
        self.paging_cursors = {}

    def get_objects_from_oslo_endpoint_with_iterator(self, resource: str, size: int = 100
                                                     ) -> Generator[Iterator[dict], None, None]:
        cursor = ''
        while True:
            response = self.get_objects_from_oslo_endpoint(resource=resource, cursor=cursor, size=size)

            decoded_string = response.content.decode("utf-8")
            graph = json.loads(decoded_string)
            headers = dict(response.headers)

            yield graph['@graph']

            if 'em-paging-next-cursor' not in headers:
                break
            cursor = headers['em-paging-next-cursor']

    def get_objects_from_oslo_endpoint(self, resource: str, cursor: str | None = None, size: int = 100,
                                       filter_dict: dict = None) -> Response:
        url = f'core/api/otl/{resource}'
        return self.request_handler.perform_get_request(url=url)
