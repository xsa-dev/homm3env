# смотри CConnection в connect.cpp
# CConnection::CConnection(std::string host, ui16 port, std::string Name, std::string UUID)
    # : io_service(std::make_shared<asio::io_service>()), iser(this), oser(this), name(Name), uuid(UUID), connectionID(0)
# Тоесть объект CConnection используется как сервис отправки/получения
#  одновременно создает сервис сирилизации/десериализации io_service
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # сирализаторы на ввод и вывод
    # Параметры Connection
    # ui16 беззнаковое 16-ричное
    # string
    # string
    # string
    uuid = 'uuid'
    send_buffer_size = 4194304
    receive_buffer_size = 4194304
    port = 3030
    oser = None
    name = 'name'
    iser = None
    host = '127.0.0.1'
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, send_buffer_size)
    s.connect((host, port))
    print(data.decode())
    data = s.recv(receive_buffer_size)

