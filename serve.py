import argparse
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.dont_write_bytecode = True

from update_asset_versions import update_asset_versions


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def send_head(self):
        for name in ('If-Modified-Since', 'If-None-Match'):
            if name in self.headers:
                del self.headers[name]
        return super().send_head()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--bind', default='127.0.0.1')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    changed = update_asset_versions(root)
    print(f'Updated asset versions in {len(changed)} files.', flush=True)
    handler = partial(NoCacheHandler, directory=str(root))
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        print(f'Serving without caching at http://{args.bind}:{server.server_port}/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nServer stopped.', flush=True)


if __name__ == '__main__':
    main()
