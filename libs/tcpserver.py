import socketserver
import json
import logging
import sys

from libs.homm3_state import MlService

logger = logging.getLogger(__name__)

BYTES_LENGHT = 32000

LOG_INFO = False


class TcpServer:
    def __init__(self):
        self.server = None
        self.exit = False

    class TcpHandler(socketserver.BaseRequestHandler):

        def handle(self):
            data = self.request.recv(BYTES_LENGHT).strip()
            json_data = json.loads(data)
            # TODO: to ML predictions
            try:
                action = ml_service().update(request=json_data)
            except Exception as ex:
                raise ex

            # self.request.sendall(json.dumps(action).encode('ascii'))
            self.env_callback(
                request=self.request,
                encoded_data=json.dumps(action).encode('ascii')
            )

        @staticmethod
        def env_callback(request, encoded_data):
            request.sendall(encoded_data)

    def start_tcp_server(self, host: str, port: int):
        if LOG_INFO:
            logging.info(f'TCPServer starting on {host}:{port}')
        try:
            with socketserver.TCPServer((host, port), TcpServer.TcpHandler, bind_and_activate=True) as self.server:
                self.server.allow_reuse_address = True
                self.server.serve_forever(poll_interval=0.1)
        except Exception as ex:
            logging.critical(msg=f'Problem: {str(ex)}')
            sys.exit(1)

    def stop_tcp_server(self, method=None):
        if method is None:
            if self.server is not None:
                self.server.shutdown()
                self.server.server_close()
                if LOG_INFO:
                    logging.info('Server stopped.')
            else:
                if LOG_INFO:
                    logging.info('Server was not started.')
