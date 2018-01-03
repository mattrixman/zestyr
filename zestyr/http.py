import urllib3, sys
import json

class Client:

    def __init__(self, auth):
        self.auth_header = auth
        self.http = urllib3.PoolManager()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get(self, url):
        try:
            response = self.http.request('GET',
                                    url,
                                    headers=self.auth_header)
        except urllib3.exceptions.MaxRetryError as ex:
            print("    GET {} failed with {}".format(url, ex.reason))
            sys.exit(1)
        print("    GET from {}".format(url))
        return response

    def post(self, url, data):
        try:
            response = self.http.request('POST',
                                    url,
                                    headers=self.auth_header,
                                    body=data)
        except urllib3.exceptions.MaxRetryError as ex:
            print("    POST failed with {}".format(url, ex.reason))
            sys.exit(1)
        print("    POST to {}".format(url))
        return response

    def put(self, url, data):
        try:
            response = self.http.request('PUT',
                                    url,
                                    headers=self.auth_header,
                                    body=data)
        except urllib3.exceptions.MaxRetryError as ex:
            print("    PUT {} failed with {}".format(url, ex.reason))
            sys.exit(1)
        print("    PUT to {}".format(url))
        return response

    def delete(self, url):
        try:
            response = self.http.request('DELETE',
                                    url,
                                    headers=self.auth_header)
        except urllib3.exceptions.MaxRetryError as ex:
            print("    DELETE {} failed with {}".format(verb, url, ex.reason))
            sys.exit(1)
        print("    DELETE {}".format(url))
        return response

def exit_on_error(resp, message=None):
    if resp.status < 200 or resp.status > 299:
        if message is not None:
            print(message)
        print(resp.status, resp.reason)
        if resp.status == 403:
            print("try logging in with a browser first")
        sys.exit(2)

# Exit with message on http errors
def response_data(verb, slug, resp):
    # exit with message on error
    exit_on_error(resp, message="while {}ing {}: ".format(verb, slug))

    # otherwise return response
    if resp.data:
        return json.loads(resp.data.decode('UTF-8'))
    else:
        return {}

class RestCaller():
    def __init__(self, client, host):
        self.client = client
        self.host = host

    def url(self, slug):
        return "https://{}{}".format(self.host, slug)

    def get(self, slug):
        return response_data('GET', slug, self.client.get(self.url(slug)))

    def post(self, slug, data):
        return response_data('POST', slug, self.client.post(self.url(slug), json.dumps(data.__dict__)))

    def put(self, slug, data):
        return response_data('PUT', slug, self.client.put(self.url(slug), json.dumps(data.__dict__)))

    def delete(self, slug):
        return response_data('DELETE', slug, self.client.post(self.url(slug)))
