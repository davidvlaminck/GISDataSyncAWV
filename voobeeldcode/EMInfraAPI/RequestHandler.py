from requests import Response


class RequestHandler:
    def __init__(self, requester):
        self.requester = requester

    def perform_get_request(self, url) -> Response:
        response = self.requester.get(url=url)
        if str(response.status_code)[:1] != '2':
            raise ConnectionError(f'status {response.status_code}')
        return response
    #
    # def perform_post_request(self, url, json_data=None, **kwargs) -> Response:
    #     if json_data is not None:
    #         kwargs['json'] = json_data
    #     response = self.requester.post(url=url, **kwargs)
    #     if str(response.status_code)[:1] != '2':
    #         raise ConnectionError(f'status {response.status_code}')
    #     return response

    def perform_post_request(self, url, **kwargs) -> Response:
        response = self.requester.post(url=url, **kwargs)
        if str(response.status_code)[:1] != '2':
            raise ConnectionError(f'status {response.status_code}')
        return response

    def perform_put_request(self, url, **kwargs) -> Response:
        response = self.requester.put(url=url, **kwargs)
        if str(response.status_code)[:1] != '2':
            raise ConnectionError(f'status {response.status_code}')
        return response

