import requests


class ServerFetcher:

    def __init__(self, domain, token, program):
        self.domain = domain
        self.token = token
        self.program = program

    def request_get(self, url, params=None):
        if params is None:
            params = {}
        return requests.get(url, params)

    def request_post(self, url, data):
        res = requests.post(url, json=data, headers={
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json',
        })

        if not 200 <= res.status_code < 300:
            raise Exception(res.text)
        return res

    def post_log_error(self, exception, traceback):
        return self.request_post(f'{self.domain}/logs/errors/', {
            'program': self.program,
            'exception': exception,
            'traceback': traceback,
        })
