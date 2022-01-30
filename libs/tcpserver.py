import socketserver
import json
import logging
import sys

from libs.homm3_state import hom3instance

logger = logging.getLogger(__name__)

BYTES_LENGHT = 32000


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
                action = hom3instance().json_handler_logic(request=json_data)
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
        logging.info(f'TCPServer starting on {host}:{port}')
        try:
            with socketserver.TCPServer((host, port), TcpServer.TcpHandler, bind_and_activate=True) as self.server:
                self.server.allow_reuse_address = True
                self.server.serve_forever(poll_interval=0.1)
        except Exception as ex:
            logging.critical(msg=f'Problem: {str(ex)}')
            sys.exit(1)

    def start_simple_tcp_server(self, host: str, port: int):
        import socket
        # Задаем адрес сервера
        SERVER_ADDRESS = (host, port)

        # Настраиваем сокет
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Помечаем чтобы менй пустил дальше
        self.server = True

        server_socket.bind(SERVER_ADDRESS)
        server_socket.listen(1)
        logging.info('Simple Tcp Server is running.')

        # Слушаем запросы
        while self.server:
            connection, address = server_socket.accept()
            logging.info("new connection from {address}".format(address=address))

            data = connection.recv(BYTES_LENGHT)

            # logic
            json_data = json.loads(data)
            action = hom3instance().json_handler_logic(request=json_data)
            connection.send(json.dumps(action).encode('ascii'))
            # close?
            connection.close()

    def stop_tcp_server(self, method=None):
        if method is None:
            if self.server is not None:
                self.server.shutdown()
                self.server.server_close()
                logging.info('Server stopped.')
            else:
                logging.info('Server was not started.')
        else:
            self.server = False
            self.exit = True
