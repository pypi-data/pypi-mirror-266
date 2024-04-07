import requests
import socket
import subprocess

def fetch_url(url):
    response = requests.get(url)
    return response.text

def post_data(url, data):
    response = requests.post(url, data=data)
    return response.text

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def get_json(url):
    response = requests.get(url)
    return response.json()

def get_headers(url):
    response = requests.head(url)
    return response.headers

def get_ip_address(domain):
    return socket.gethostbyname(domain)

def check_host(hostname):
    result = subprocess.run(['ping', '-c', '1', hostname], stdout=subprocess.PIPE)
    return result.returncode == 0