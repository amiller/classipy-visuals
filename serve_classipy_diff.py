from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn
import urlparse
import threading

import classipy_diff

if not 'Handler' in globals():

    class Handler(SimpleHTTPRequestHandler):
        def log_request(self, code=None, size=None):
            pass


def do_GET(self):
    reload(classipy_diff)
    parsed_path = urlparse.urlparse(self.path)
    if parsed_path.path.startswith('/JPEGImages'):
        self.send_response(200)
        self.end_headers()
        with (open('.'+parsed_path.path, 'r')) as f:
            self.wfile.write(f.read())
        return

    self.send_response(200)
    self.end_headers()
    self.wfile.write(classipy_diff.render_html())
    return

Handler.do_GET = do_GET
if not 'server' in globals():

    class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
        pass


if __name__ == '__main__':
    port = 8080
    server = ThreadedHTTPServer(('localhost', port), Handler)
    print 'serving: http://localhost:%d' % port
    server.serve_forever()
    #thread = threading.Thread(target=server.serve_forever)
    #thread.start()
