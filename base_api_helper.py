import os
import datetime
import requests

class BaseAPIHelper:
    def __init__(self, client_id, client_secret, attorney, auth_url, token_url, api_url, token_file_path, redirect_uri=""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.attorney = attorney
        self.auth_url = auth_url
        self.token_url = token_url
        self.api_url = api_url
        self.redirect_uri = redirect_uri
        self.token_file_path = token_file_path
        self.token_store = self.read_tokens_from_file()

    def read_tokens_from_file(self):
        token_store = {
            'access_token': "",
            'refresh_token': "",
            'expires_in': "",
            'expires_in_utc': None
        }
        if not os.path.exists(self.token_file_path):
            print(f"Token file not found for {self.attorney.name}. A new one will be created upon successful authorization/refresh.")
            return token_store
        try:
            with open(self.token_file_path, "r", encoding="utf-8") as api_codes:
                for line in api_codes:
                    line = line.strip()
                    if line.startswith("access_token="):
                        token_store['access_token'] = line.split('=', 1)[1]
                    elif line.startswith("refresh_token="):
                        token_store['refresh_token'] = line.split('=', 1)[1]
                    elif line.startswith("expires_in="):
                        token_store['expires_in'] = line.split('=', 1)[1]
                    elif line.startswith("expires_in_utc="):
                        date_str = line.split('=', 1)[1]
                        try:
                            token_store['expires_in_utc'] = datetime.datetime.fromisoformat(date_str)
                        except ValueError:
                            print(f"Warning: Could not parse expires_in_utc date string: {date_str}")
            print(f"Successfully retrieved tokens for {self.attorney.name} from file.")
        except IOError as e:
            print(f"Error reading token file: {e}")
        return token_store

    def save_tokens_to_file(self):
        directory = os.path.dirname(self.token_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            with open(self.token_file_path, "w", encoding="utf-8") as api_codes:
                api_codes.write(f"access_token={self.token_store.get('access_token', '')}\n")
                api_codes.write(f"refresh_token={self.token_store.get('refresh_token', '')}\n")
                api_codes.write(f"expires_in={self.token_store.get('expires_in', '')}\n")
                expires_in_utc = self.token_store.get('expires_in_utc')
                if expires_in_utc:
                    api_codes.write(f"expires_in_utc={expires_in_utc.isoformat()}\n")
                else:
                    api_codes.write(f"expires_in_utc=\n")
            print(f"Successfully saved new tokens to {self.token_file_path}")
        except IOError as e:
            print(f"Error saving token file: {e}")

    def is_token_expired(self):
        if self.token_store['expires_in_utc'] is None:
            print("No token found in API folder. Attempting to authenticate and retrieve one.")
            return True
        return datetime.datetime.now(datetime.timezone.utc) >= self.token_store['expires_in_utc']

    def is_token_valid(self):
        return self.token_store['access_token'] != ""

    def refresh_token(self):
        print("Access token expired. Refreshing token...")
        if not self.token_store['refresh_token']:
            raise Exception("No refresh token available. User must re-authenticate.")
        refresh_data = {
            'Content-type': 'application/x-www-form-urlencoded',
            'grant_type': 'refresh_token',
            'refresh_token': self.token_store['refresh_token'],
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(self.token_url, data=refresh_data)
        response.raise_for_status()
        new_token_info = response.json()
        self.token_store['access_token'] = new_token_info['access_token']
        self.token_store['refresh_token'] = new_token_info['refresh_token']
        expires_in_seconds = new_token_info['expires_in']
        self.token_store['expires_in'] = new_token_info['expires_in']
        self.token_store['expires_in_utc'] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=int(expires_in_seconds))
        print("Updating local token store with refreshed information")
        self.save_tokens_to_file()
        print("Token refreshed successfully.")

    def make_authenticated_request(self, url, method='GET', **kwargs):
        if self.is_token_expired():
            self.refresh_token()
        if not self.is_token_valid():
            self.get_new_token()
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {self.token_store['access_token']}"
        headers['Accept'] = 'application/json'
        kwargs['headers'] = headers
        return requests.request(method, url, **kwargs)

    def get_new_token(self):
        raise NotImplementedError("Subclasses must implement get_new_token for their OAuth flow.")
