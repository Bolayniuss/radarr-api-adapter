import gzip
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

import urllib
import urllib.request
import urllib.response
import requests

import json


class _RadarrApiAdapter(BaseHTTPRequestHandler):

    base_api = None
    auth_key = None

    def auth(self):
        if self.auth_key is None:
            return True
        return False

    def do_GET(self):
        if not self.auth():
            self.send_response(HTTPStatus.UNAUTHORIZED)
            self.end_headers()
            return

        if self.path != "/radarr-api-adapter/movie/":
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        headers = dict(self.headers.items())
        headers["Accept"] = "application/json"

        response = requests.get(self.base_api, headers=headers)

        response_status_code = response.status_code
        self.send_response(response_status_code)
        if response_status_code != 200:
            self.end_headers()
            return

        response_headers = response.headers

        data = response.json()
        new_data = self.mutate_data(data)

        # for h, v in response_headers.items():
        #     print("Set Header %s: %s" % (h, v))
        #     self.send_header(h, v)
        self.end_headers()

        f = self.wfile
        # if response_headers.get("Content-Encoding") == "gzip":
        #     f = gzip.GzipFile(mode="wb", fileobj=f)

        j_data = json.dumps(new_data)
        f.write(j_data.encode("utf-8"))

    def mutate_data(self, data):
        def adapt_item(item):
            # local_db_id = item["id"]
            tmdb_id = item["tmdbId"]

            return dict(
                overview=item["overview"],
                genres=item["genres"],
                title=item["title"],
                runtime=item["runtime"],
                id=tmdb_id,
                imdb_id=item.get("imdbId", ""),
                homepage=item.get("website", "")
            )
        return [adapt_item(v) for v in data]


def radarr_api_adapter_class_maker(api_url, api_key):
    cls = type("RadarrApiAdapter", (_RadarrApiAdapter, ), dict(base_api=api_url, auth_key=api_key))
    return cls