from collections import namedtuple
from zestyr import context
import urllib3
import sys
import json

Response = namedtuple("Response", "verb url http_obj")
class Client:
    def __init__(self, auth, ctxt=context.default()):
        self.context = ctxt
        self.auth_header = auth
        self.http = urllib3.PoolManager()
        urllib3.disable_warnings(
                urllib3.exceptions.InsecureRequestWarning)

    def request(self, verb, url, body=None):
        try:
            if body is not None:
                response = self.http.request(verb,
                                        url,
                                        headers=self.auth_header,
                                        body=body)
            else:
                response = self.http.request(verb,
                                        url,
                                        headers=self.auth_header)
        except urllib3.exceptions.MaxRetryError as ex:
            print("    {} {} failed with {}".format(verb, url, ex.reason))
            sys.exit(1)
        print("    {} -> {}".format(verb, url))
        return Response(verb, url, response)



def exit_on_error(resp, message=None):
    if resp.status < 200 or resp.status > 299:
        if message is not None:
            print(message)
        print(resp.status, resp.reason)
        if resp.status == 403:
            print("try logging in with a browser first")
        sys.exit(2)

GoodResponse = namedtuple("GoodResponse", "verb url data")
def exit_or_read(response):
    # exit with message on error
    exit_on_error(response.http_obj, message="while {}ing {}: ".format(response.verb, response.url))

    # otherwise return response
    if response.http_obj.data:
        return GoodResponse(response.verb, 
                            response.url, 
                            json.loads(response.http_obj.data.decode('UTF-8')))
    else:
        return GoodResponse(response.verb, 
                            response.url, 
                            {})

class RestCaller():
    def __init__(self, client, host):
        self.client = client
        self.host = host

    def url(self, slug):
        return "https://{}{}".format(self.host, slug)

    def get(self, slug):
        return exit_or_read(self.client.request('GET', self.url(slug)))

    def post(self, slug, data):
        return exit_or_read(self.client.request('POST', self.url(slug), json.dumps(data.__dict__)))

    def put(self, slug, data):
        return exit_or_read(self.client.request('PUT', self.url(slug), json.dumps(data.__dict__)))

    def delete(self, slug):
        return exit_or_read(self.client.request('DELETE', (self.url(slug))))
