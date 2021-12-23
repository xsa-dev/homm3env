import argparse
import json
import socketserver
import logging

from datetime import datetime
logPath = 'logs'
logsFilename = str(datetime.now().date())


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{logPath}/{logsFilename}.log"),
        logging.StreamHandler()
    ]
)

logging.info('info')


class HoMM3BattleTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024).strip()
        json_data = json.loads(data)
        logging.info(f'{json_data}')
        # TODO: logic
        self.request.sendall(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--port', dest='port', default=9999,
                        help='tcp server port', type=int)
    parser.add_argument('--host', dest='host', default='localhost',
                        help='tcp host url')
    args = parser.parse_args()

    logging.info(f'TCPServer start on {args.host}:{args.port}')
    with socketserver.TCPServer((args.host, args.port), HoMM3BattleTCPHandler) as server:
        try:
            server.serve_forever()
        except Exception as ex:
            pass
            logging.critical(msg=f'Problem: {str(ex)}\nexit')
