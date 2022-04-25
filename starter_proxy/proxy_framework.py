import math
from multiprocessing.dummy import active_children
import socket
import sys
import threading
import time
from threading import Thread

from dns.query import udp
from dns import *
import dns
import argparse

"""
This framework is just a reference for beginning. Feel free to change it!
Have a good luck!
"""

def recv(s):
    """
    recevie the request passed to proxy.
    """

def send(s):
    """
    send the response here.
    """  

def exit():
    """
    you should provide a way to exit your proxy well.
    """

def accept(PORT):
    """
    you should bind the ip of your socket to 0.0.0.0 to make the proxy work well
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", PORT))


def modify_request(message):
    """
    Here you should change the requested bit rate according to your computation of throughput.
    And if the request is for big_buck_bunny.f4m, you should instead request big_buck_bunny_nolist.f4m 
    for client and leave big_buck_bunny.f4m for the use in proxy.
    """

def request_dns():
    """
    Request dns server here. Specify the domain name as you want.
    """
    query = message.make_query("xxx", dns.rdatatype.A,
                                        dns.rdataclass.IN)

def calculate_throughput():
    """
    Calculate throughput here.
    """


class Proxy():
    """
    The class is used to manage connections from clients.
    """
    def __init__(self):
        self.connection = None
        self.send_buffer = None
        self.receive_buffer = None
        """
        Add field as you want
        """


class Connection():
    def __init__(self, conn, address):
        self.conn = conn
        self.address = address
        """
        Add field as you want
        """
    


if __name__ == '__main__':
   
    """
    Parse command varibles first.
    """
    parser = argparse.ArgumentParser(description='start proxying......')
    parser.add_argument('-p', '--port', required=True,
                            help='listening port for proxy.')
    args = parser.parse_args()

    """
    Start your proxy.
    """

    accept(args.port)
    

