"""Exercise the real Docker SDK transport without a Docker daemon."""

import json
from http.server import BaseHTTPRequestHandler
from socketserver import UnixStreamServer
from tempfile import TemporaryDirectory
from threading import Thread

import docker


class DockerApiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/version':
            body = json.dumps({'ApiVersion': '1.45'}).encode()
        elif self.path == '/v1.45/_ping':
            body = b'OK'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        pass


def test_docker_client_negotiates_version_and_pings_over_unix_socket():
    # Pytest's per-test paths can exceed macOS's Unix socket path limit.
    with TemporaryDirectory(prefix='jd-', dir='/tmp') as directory:
        socket_path = f'{directory}/docker.sock'
        with UnixStreamServer(socket_path, DockerApiHandler) as server:
            thread = Thread(
                target=server.serve_forever,
                kwargs={'poll_interval': 0.01},
                daemon=True,
            )
            thread.start()
            try:
                client = docker.DockerClient(base_url=f'unix://{socket_path}', timeout=2)
                try:
                    assert client.api.api_version == '1.45'
                    assert client.ping() is True
                finally:
                    client.close()
            finally:
                server.shutdown()
                thread.join(timeout=2)
