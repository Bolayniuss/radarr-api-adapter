import argparse
import socketserver

from radarr_adapter import radarr_api_adapter_class_maker


def serve(port, api, key=None):
    handler_class = radarr_api_adapter_class_maker(api, key)
    httpd = socketserver.TCPServer(('', port), handler_class)
    print("Now serving at %d" % port)
    httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(
        prog="Radarr-api-adaptor"
    )

    parser.add_argument("port", type=int, help="Listening port.")
    parser.add_argument("api_url", type=str, help="url of the api to adapt.")
    parser.add_argument("--api_key", type=str, default=None, help="key used to protect the adaptor")

    args = parser.parse_args()

    serve(args.port, args.api_url, args.api_key)

if __name__ == "__main__":
    main()
