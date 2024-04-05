from http.server import SimpleHTTPRequestHandler
from http import HTTPStatus
from typing import Dict
import os


def make_handler(config: Dict):
    class SimpleButEnhancedHTTPRequestHandler(SimpleHTTPRequestHandler):
        """A simple HTTP server which is meant to serve the output directory, with some enhancements (emulates URL rewrite
        for HTML files without .html extension; emulates custom 404 error page"""
        protocol_version = 'HTTP/1.1'

        def __init__(self, *args, **kvargs):
            try:
                super().__init__(*args, **kvargs, directory=config['OUTPUT_DIR'])
            except (ConnectionAbortedError, BrokenPipeError):
                pass

        def translate_path(self, path):
            path = super().translate_path(path)

            if not path.endswith(('\\', '/')):
                _, extension = os.path.splitext(path)

                if not extension:
                    path += '.html'

            return path

        def send_error(self, code, message=None, explain=None):
            if self.command != 'HEAD' and code == HTTPStatus.NOT_FOUND:
                try:
                    f = open(os.path.join(self.directory, '404.html'), 'rb')
                except OSError:
                    return super().send_error(code, message=message, explain=explain)

                fs = os.fstat(f.fileno())

                self.log_error("code %d, message %s", code, message)
                self.send_response(code, message)
                self.send_header('Connection', 'close')

                self.send_header('Content-Type', self.error_content_type)
                self.send_header('Content-Length', str(fs[6]))
                self.end_headers()

                self.copyfile(f, self.wfile)
            else:
                return super().send_error(code, message=message, explain=explain)

    return SimpleButEnhancedHTTPRequestHandler
