import gzip
import os
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

import urllib
import urllib.request
import urllib.response
import urllib.parse
import requests

import json

from handler_mixins import FileServingMixin


class HTTPError(Exception):
    def __init__(self, code: int, message: str = None):
        self.code = code
        self.message = message
        super().__init__(code)


def match(pattern, path):
    return re.fullmatch(pattern, path)


class _RadarrApiAdapter(BaseHTTPRequestHandler, FileServingMixin):

    serve_poster = None
    poster_mapping = None

    base_api = None
    auth_key = None

    def map_api_path(self, path):
        if self.poster_mapping:
            api_path, _ = self.poster_mapping
            path = path.replace(api_path, "")
        return path

    def mutate_data(self, data):
        def adapt_item(item, request_path):
            # local_db_id = item["id"]
            tmdb_id = item["tmdbId"]

            out = dict(
                overview=item["overview"],
                genres=item["genres"],
                title=item["title"],
                runtime=item["runtime"],
                id=tmdb_id,
                imdb_id=item.get("imdbId", ""),
                homepage=item.get("website"),
                trailer_key=item.get("youTubeTrailerId"),
                trailer_site="youtube",
            )

            if self.serve_poster:
                poster = None
                for media in item.get("images", []):
                    if media.get("coverType") == "poster":
                        poster = media.get("url")
                        break

                if poster:
                    poster = self.map_api_path(poster)
                    if poster[0] != "/":
                        poster = "/" + poster

                    parts = urllib.parse.urlsplit(request_path)
                    new_parts = (parts[0], parts[1], "/poster" + poster, "", "")  # TODO: add auth key ?auth_key=....
                    poster_url = urllib.parse.urlunsplit(new_parts)

                    out["poster"] = poster_url
                    out["poster"] = "https://m.media-amazon.com/images/M/MV5BMmM1ZTZhNDUtYzBkNi00YzQ0LWEyZjItM2M5OTI2ZTU0MDlkXkEyXkFqcGdeQXVyMjI0MjMwMzQ@._V1_SY1000_CR0,0,704,1000_AL_.jpg"

            return out

        return [adapt_item(v, self.path) for v in data]

    def api_adapter(self):
        headers = dict(self.headers.items())
        headers["Accept"] = "application/json"

        response = requests.get(self.base_api, headers=headers)

        response_status_code = response.status_code
        self.send_response(response_status_code)
        if response_status_code != 200:
            self.end_headers()
            return

        data = response.json()
        new_data = self.mutate_data(data)

        response_headers = response.headers
        # for h, v in response_headers.items():
        #     print("Set Header %s: %s" % (h, v))
        #     self.send_header(h, v)

        f = self.wfile
        # if response_headers.get("Content-Encoding") == "gzip":
        #     f = gzip.GzipFile(mode="wb", fileobj=f)

        j_data = json.dumps(new_data)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(j_data)))

        self.end_headers()


        f.write(j_data.encode("utf-8"))

    def poster(self, path):
        ext_path = "/%s" % path
        if "/../" in ext_path or "/./" in ext_path:
            raise HTTPError(HTTPStatus.FORBIDDEN)

        if not self.serve_poster:
            raise HTTPError(HTTPStatus.NOT_FOUND)

        if not self.poster_mapping and not len(self.poster_mapping) == 2:
            raise HTTPError(HTTPStatus.INTERNAL_SERVER_ERROR)

        _, local_base_path = self.poster_mapping
        local_path = os.path.join(local_base_path, path)

        if not os.path.isfile(local_path):
            raise HTTPError(HTTPStatus.NOT_FOUND)

        self.send_file(local_path)
        self.copyfile(local_path, self.wfile)

    routes = (
        (r"^/radarr-api-adapter/movie/$", api_adapter),
        (r"^/poster/(?P<poster_path>.*)$", poster),
    )

    def route(self, raise_exception=True):
        """ route the current request and return True on success else return False
        """

        for route_pattern, handler in self.routes:
            m = match(route_pattern, self.path)
            if m is not None:
                handler(self, *m.groups())
                return True
        if raise_exception:
            raise HTTPError(HTTPStatus.NOT_FOUND)
        return False

    def auth(self, raise_exception=True):
        if self.auth_key is None:
            return True
        if raise_exception:
            raise HTTPError(HTTPStatus.UNAUTHORIZED)
        return False

    def do_GET(self):
        try:
            self.auth()
            self.route()

        except HTTPError as e:
            self.send_error(e.code, e.message)
            return


def radarr_api_adapter_class_maker(api_url, api_key, serv_poster, poster_mapping):
    if serv_poster and poster_mapping is not None:
        try:
            _, _ = poster_mapping
        except:
            raise Exception("`poster_mapping` is not correctly set! poster_mapping=%s" % poster_mapping)

    attr = dict(
        base_api=api_url,
        auth_key=api_key,
        serve_poster=serv_poster,
        poster_mapping=poster_mapping,
    )

    return type("RadarrApiAdapter", (_RadarrApiAdapter, ), attr)
