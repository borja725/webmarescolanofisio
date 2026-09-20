"""Local development server.

Python's built-in `http.server` sends no Cache-Control header, so browsers fall
back to heuristic caching and keep serving a stale copy of a page without ever
asking the server. This subclass tells the browser never to store HTML, so what
you see in the browser is always what is on disk.

    python serve.py          # http://localhost:8000
    python serve.py 8080     # another port

NOTHING is cached here, assets included. An earlier version only did this for
HTML, on the grounds that stylesheets carry a ?v= version anyway - but that
left JavaScript stale in the browser while the file on disk had changed. In
development you always want what is on disk; ?v= is a production concern.
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class DevHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, fmt, *args):
        if '" 200' not in fmt % args:
            super().log_message(fmt, *args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = partial(DevHandler, directory='.')
    # loopback only: this serves the whole working tree, .git included,
    # and has no business being reachable from the local network
    with ThreadingHTTPServer(('127.0.0.1', port), handler) as httpd:
        print(f'Serving on http://localhost:{port}  (HTML is never cached)')
        print('Ctrl+C to stop.')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nStopped.')


if __name__ == '__main__':
    main()
