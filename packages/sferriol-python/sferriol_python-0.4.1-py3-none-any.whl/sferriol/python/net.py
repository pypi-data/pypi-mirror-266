# -*- coding: utf-8 -*-
#
#  Copyright 2023 sferriol <s.ferriol@ip2i.in2p3.fr>
"""Network utilities"""
import socket


def is_port_in_use(port: int) -> bool:
    """Test if the port is already used"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def unused_port() -> int:
    """Return an unsued port

    Returns:
      Port value
    """
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    _, port = sock.getsockname()
    sock.close()
    return port
