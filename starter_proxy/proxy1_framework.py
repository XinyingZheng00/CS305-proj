import requests
from flask import Flask, Response

app = Flask(__name__)



@app.route('/example')
def simple():
        return Response(requests.get('http://www.example.com'))


def modify_request(message):
    """
    Here you should change the requested bit rate according to your computation of throughput.
    And if the request is for big_buck_bunny.f4m, you should instead request big_buck_bunny_nolist.f4m 
    for client and leave big_buck_bunny.f4m for the use in proxy.
    """

def request_dns():
    """
    Request dns server here.
    """

def calculate_throughput():
    """
    Calculate throughput here.
    """


if __name__ == '__main__':
    app.run(port=8999)
