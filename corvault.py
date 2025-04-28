import sys
import requests
import json
import hashlib
import pprint
import yaml

# NOTE: This is to suppress the insecure connection warning for certificate
# verification.
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

headers = {'datatype':'json'}

class Corvault:
    def __init__(self, url, username="user", password="password"):
        self.url = url
        self.username = username
        self.password = password
        self.login_session = None
    
    def load_config(self, config_file='config.yaml'):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        self.username = config['username']
        self.password = config['password']

    def login(self):
        login_url = self.url + '/api/login'
        r = requests.get(login_url, auth=(self.username, self.password), headers=headers, verify=False)
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
            self.login_session = response['status'][0]['response']
            return self.login_session
        else:
            print("Login failed!")
            return None
    
    # TODO: retry if session is invalid
    def get_page(self, path):
        page_url = self.url + path
        headers = {'sessionKey': self.login_session, 'datatype':'json'}
        r = requests.get(page_url, headers=headers, verify=False)
        if r.status_code == 200:
            return json.loads(r.content.decode('utf-8'))
        else:
            print(f"Failed to get page: {path}")
            return None