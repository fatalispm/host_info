"""
Basic REST API
Supports:
adding new url to parse links
fetching list of parsed urls
fetching list of parsed links and count of their occurenses
"""
import socket
import logging
import json

from threading import Thread

import insert_db


def create_server_socket(host='127.0.0.1', port=8000):
    """
    :Parameters:
        - `host`: str
        - `port`: int
    :Return:
        socket.socket
    """
    serversocket = socket.socket()

    try:
        serversocket.bind((host, port))
    except socket.error:
        logging.exception('Failed to run on port: %s host: %s', host, port)
        return

    serversocket.listen(5)

    return serversocket


def handler(data, connection):
    """
    Function for handling requests
    :Parameters:
         - `data`: str
         - `connection`: socket.connection
    """
    try:
        data = json.loads(data)
    except ValueError:
        connection.sendall('Send valid data')
        return

    try:
        data['urls']
    except KeyError:
        connection.sendall('Include urls in your json data')
        return

    thread = Thread(target=insert_db.fetch_urls, args=[data.get('urls', [])])
    thread.run()
    connection.sendall(json.dumps({'accepted': True}))


def client_thread(connection, client_address, handler):
    """
    :Parameters:
         - `connection`: socket.connection
         - `client_address`: str
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


def main():
    port = int(raw_input('Please enter port number(int)'))  # let it fail
    serversocket = create_server_socket(port=port)
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
    main()
