"""
This module contains simple communication related functions for initial testing, which will be replaced by
more suitable communication methods in the productive system.
"""

import pickle
import socket
from typing import Any, Dict


DEFAULT_PORT = 4442
LOCALHOST = "localhost"


def receive_data(host: str = LOCALHOST, port: int = DEFAULT_PORT) -> Any:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))  # wait for response and collect parts

        s.listen()
        conn, addr = s.accept()

        data = []
        with conn:
            while True:
                packet = conn.recv(4096)
                if not packet:
                    break
                data.append(packet)

        return pickle.loads(b"".join(data))


def send_data_to_other_party(data: Dict, host: str = LOCALHOST, port: int = DEFAULT_PORT) -> Any:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        connected = False
        while not connected:
            try:
                s.connect((host, port))
                connected = True
            except ConnectionRefusedError:
                # We expect the next party to be online, otherwise we just simply try again
                # print("\n\nConnection attempt to " + host + ":" + str(port) + " failed.")
                pass

        s.sendall(pickle.dumps(data))
