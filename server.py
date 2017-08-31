"""
Basic REST API
Supports:
adding new url to parse links
fetching list of parsed urls
fetching list of parsed links and count of their occurenses
"""
import socket

from threading import Thread

import logging

import pickle

import main


def create_server_socket(host='127.0.0.1', port=8000):
    """
    :Parameters:
        - `host`: str
        - `port`: int
    :Return:
        socket.socket
    """
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serversocket.bind((host, port))
    except socket.error:
        logging.exception('Failed to run on port: %s host: %s', host, port)
        return

    serversocket.listen(5)

    return serversocket


create_server_socket()


def handler(data, connection):
    """
    Function for handling requests
    :param data: str
    :param connection: socket.connection
    :return:
    """
    data = pickle.loads(data)
    response = {'accepted': True}
    thread = Thread(target=main.fetch_urls, args=[data.get('urls', [])])
    thread.run()
    connection.sendall(pickle.dumps(response))


def client_thread(connection, client_address, handler):
    """
    :param connection: socket.connection
    :param client_address: str
    :return: Thread
    """

    def target():
        try:
            logging.info('Connection from %s', client_address)

            while True:
                data = connection.recv(1024)
                logging.info('received "%s"', data)

                if data:
                    handler(data, connection)
                else:
                    logging.info('no more data from: %s', client_address)
                    break

        finally:
            connection.close()

    return Thread(target=target)


def _main():
    serversocket = create_server_socket(port=8012)
    if not serversocket:
        return
    try:
        while True:
            connection, address = serversocket.accept()
            ct = client_thread(connection, address, handler)
            ct.run()
    finally:
        serversocket.close()

if __name__ == '__main__':
    _main()
