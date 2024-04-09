import json
from urllib import error, parse, request

import certifi


class HTTPRequestException(Exception):
    pass


class ResponseIsNotJson(Exception):
    pass


class Response:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        try:
            return json.loads(self.data.decode())
        except json.decoder.JSONDecodeError:
            raise ResponseIsNotJson

    @property
    def text(self):
        return self.data.decode()

    def is_successful(self):
        return 200 <= self.status_code <= 299


class _Requests:
    def get(self, url):
        try:
            with request.urlopen(
                url,
                cafile=certifi.where(),
            ) as response:
                return Response(
                    response.status,
                    response.read(),
                )
        except error.URLError:
            raise HTTPRequestException

    def post(self, url, body=None, is_json=False):
        if is_json:
            request_body = json.dumps(body).encode("utf-8")
        else:
            request_body = parse.urlencode(body).encode()

        req = request.Request(
            url,
            data=request_body,
        )

        if is_json:
            req.add_header("Content-Type", "application/json")

        try:
            with request.urlopen(
                req,
                cafile=certifi.where(),
            ) as response:
                return Response(response.status, response.read())
        except error.HTTPError as e:
            return Response(e.status, e.read())


requests = _Requests()
