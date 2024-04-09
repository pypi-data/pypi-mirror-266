import json
from urllib import error, parse, request


class HTTPRequestException(Exception):
    pass


class Response:
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def json(self):
        return json.loads(self.data.decode())

    @property
    def text(self):
        return self.data.decode()


class _Requests:
    def get(self, url):
        with request.urlopen(
            url,
        ) as response:
            return Response(
                response.status,
                response.read(),
            )

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
            with request.urlopen(req) as response:
                return Response(response.status, response.read())
        except error.HTTPError as e:
            return Response(e.status, e.read())


requests = _Requests()
