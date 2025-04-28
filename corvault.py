import requests
import json
import yaml
import os
from tenacity import retry, stop_after_delay, stop_after_attempt
import logging

# NOTE: This is to suppress the insecure connection warning for certificate
# verification.
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Corvault:
    def __init__(self, host, username="user", password="password"):
        self.host = host
        self.username = username
        self.password = password
        self.login_session = None

        # create a directory for the session files if it doesn't exist
        if not os.path.exists('.sessions'):
            os.makedirs('.sessions')

    def load_config(self, config_file='config.yaml'):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        self.username = config['username']
        self.password = config['password']

    def login(self):
        login_url = self.host + '/api/login'
        # check if the session file exists
        session_file = '.sessions/' + self.host
        if os.path.exists(session_file):
            # read the session key from the file
            with open(session_file, 'r') as f:
                self.login_session = f.read().strip()
            # check if the session is still valid
            headers = {'sessionKey': self.login_session, 'datatype': 'json'}
            r = requests.get('https://' + self.host + '/api/show/versions', headers=headers, verify=False)
            if r.status_code == 200:
                logging.debug("Session is still valid.")
                return self.login_session
            elif r.status_code == 401:
                logging.error("Session is invalid")
                # delete the session file
                os.remove(session_file)
            else:
                logging.error("Session is invalid. Status code: %s", r.status_code)
                os.remove(session_file)

        # Do a login since the old session is invalid or doesn't exist
        r = requests.get("https://" + login_url, auth=(self.username, self.password),
                         headers={'datatype': 'json'}, verify=False)
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
            self.login_session = response['status'][0]['response']
            # save the session key to a file
            with open('.sessions/' + self.host, 'w') as f:
                f.write(self.login_session)
            return self.login_session
        else:
            logging.error(f"Login failed with status code: {r.status_code}")
            return None

    @retry(stop=(stop_after_delay(10) | stop_after_attempt(5)))
    def get_page(self, path):
        page_url = 'https://' + self.host + path
        headers = {'sessionKey': self.login_session, 'datatype': 'json'}
        r = requests.get(page_url, headers=headers, verify=False)
        if r.status_code == 200:
            return json.loads(r.content.decode('utf-8'))
        else:
            logging.error(f"Failed to get page: {path}, status code: {r.status_code}")
            raise OSError(f"Failed to get page: {path}")
