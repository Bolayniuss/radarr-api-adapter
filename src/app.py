import argparse
import socketserver

from radarr_adapter import radarr_api_adapter_class_maker


def serve(port, api, key=None, serv_poster=False, poster_mapping=None):
    handler_class = radarr_api_adapter_class_maker(api, key, serv_poster, poster_mapping)
    httpd = socketserver.TCPServer(('', port), handler_class)
    print("Now serving at %d" % port)
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(
        prog="Radarr-api-adaptor"
    )

    parser.add_argument("port", type=int, help="Listening port.")
    parser.add_argument("api_url", type=str, help="url of the api to adapt.")
    parser.add_argument("--serv_poster", default=False, help="The proxy will also serv the posters", action="store_true")
    parser.add_argument("--poster_mapping", type=str, default=None, help="Map api relative path to local path. format: api_relative:local_relative")
    parser.add_argument("--api_key", type=str, default=None, help="key used to protect the adaptor")

    args = parser.parse_args()

    poster_mapping = None
    if args.poster_mapping:
        poster_mapping = args.poster_mapping.split(":")

    serve(args.port, args.api_url, args.api_key, args.serv_poster, poster_mapping)


if __name__ == "__main__":
    main()
