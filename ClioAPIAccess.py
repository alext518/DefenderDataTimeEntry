import requests
import urllib.parse
import os
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import Attorney
import datetime

def get_access_keys(name):
    client_id = ""
    client_secret = ""
    with open(name + '\\API\\apiaccess.api', "r", encoding="utf-8") as api_codes:
        for line in api_codes:
            line = line.strip()
            if line.startswith("client_id="):
                client_id = line.split('=', 1)[1]
            elif line.startswith("client_secret="):
                client_secret = line.split('=', 1)[1]
        print(f"Successfully retrieved {name}'s api keys!")
    return client_id, client_secret

### For Authorizataion help see: https://docs.developers.clio.com/api-docs/authorization/#step-1-get-authorization-code
class ClioAPIHelper:
    def __init__(self, client_id: str, client_secret: str, attorney: Attorney, redirect_uri: str = "https://app.clio.com/oauth/approval", state: str = "state", response_type: str = "code", redirect_on_decline: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.attorney = attorney
        self.redirect_uri = redirect_uri
        self.state = state
        self.token_store: dict = self.read_tokens_from_file()
        self.CLIO_AUTH_URL = "app.clio.com/oauth/authorize"
        self.CLIO_TOKEN_URL = "https://app.clio.com/oauth/token?"
        self.CLIO_BASE_URL = "https://app.clio.com/"
        self.CLIO_API_URL = "https://app.clio.com/api/v4/"

    def get_new_token(self):
        auth_url = (
                f"https://{self.CLIO_AUTH_URL}?"
                f"response_type=code&"
                f"client_id={self.client_id}&"
                f"redirect_uri={urllib.parse.quote(self.redirect_uri)}&"
            )

        options = wd.ChromeOptions()
        options.add_argument("--log-level=3")
        options.add_experimental_option("detach", True)  # Keeps browser open after script ends
        driver = wd.Chrome(options=options)
        driver.get(auth_url) # Browse to authorization page to sign in and authorize app to perform lookups

        # sign in
        email = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
        if email:
            email.send_keys(self.attorney.email)
            button = driver.find_element(By.ID,"next")
            button.click()
        else:
            print("Email field not found, enter manually then press enter key here.")
            input()
        
        try:
            password = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "password"))
                )
            if password:
                password.send_keys(self.attorney.password)
                sign_in = driver.find_element(By.ID, "signin")
                sign_in.click()
        except:
            print("Password field not found, enter manually then press enter key here.")
            input()

        try:
            allow_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button.th-button.create"))
                )
            if allow_button:
                allow_button.click()
        except:
            print("Allow access button now found. Click manually then press enter key here.")
            input
        WebDriverWait(driver,60).until(
            EC.title_contains("Success code=")
        )
        # Using the special desktop redirect uri we can get the authorization code when approved from the page title after redirecting
        # Retrieve the full title text
        full_title_text = driver.title

        prefix = "Success code="
        if prefix in full_title_text:
            authorization_code = full_title_text.split(prefix)[1].strip()
        else:
            raise Exception("Could not find the authorization code in the page title.")

        print(f"Success code acquired: {authorization_code}")
        driver.close()

        # Exchange code for access token
        token_data = {
            'Content-type': 'application/x-www-form-urlencoded',
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(self.CLIO_TOKEN_URL, data = token_data)
        response.raise_for_status()
        token_info = response.json()

        self.token_store = token_info
        self.ACCESS_TOKEN = token_info['access_token']
        self.ACCESS_TOKEN_EXPIRES = token_info['expires_in']
        self.ACCESS_TOKEN_REFRESH = token_info['refresh_token']
        self.token_store['expires_in_utc'] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=self.ACCESS_TOKEN_EXPIRES)
        print(f"\nSuccessfully obtained access token: \n\tToken: {self.ACCESS_TOKEN} \n\tExpires in: {self.ACCESS_TOKEN_EXPIRES} \n\tRefresh Token:{self.ACCESS_TOKEN_REFRESH}")
        print("Congratulations! You've successfully logged into the Clio API!")
        self.save_tokens_to_file()

        # 3. Use the access token to make an API request (e.g., fetching user info) NOT IMPLEMENTED YET
        # THIS IS AN EXAMPLE OF AN API REQUEST CUSTOMIZE FOR OUR USE LATER
        # API_URL = "https://app.clio.com/api/v4/users/who_am_i"

        # headers = {
        #     'Authorization': f'Bearer {ACCESS_TOKEN}',
        #     'Accept': 'application/json'
        # }

        # api_response = requests.get(API_URL, headers=headers)
        # api_response.raise_for_status()
        # user_data = api_response.json()

        # print("\nAPI Request (who_am_i) successful:")
        # print(user_data)

    # Function to read tokens (your original logic, slightly cleaned up)
    def read_tokens_from_file(self) -> dict:
        """Reads stored tokens from a file for a given account name."""
        filepath = f"{self.attorney.name}\\API\\token.txt"
        token_store = {
            'access_token': "",
            'refresh_token': "",
            'expires_in_utc': None
        }

        if not os.path.exists(filepath):
            print(f"Token file not found for {self.attorney.name}. A new one will be created upon successful authorization/refresh.")
            return token_store
    
        try:
            with open(filepath, "r", encoding="utf-8") as api_codes:
                for line in api_codes:
                    line = line.strip()
                    if line.startswith("access_token="):
                        token_store['access_token'] = line.split('=', 1)[1]
                    elif line.startswith("refresh_token="):
                        token_store['refresh_token'] = line.split('=', 1)[1]
                    elif line.startswith("expires_in="):
                        token_store['expires_in'] = line.split('=', 1)[1]
                    elif line.startswith("expires_in_utc="):
                        # Convert the stored string back into a datetime object
                        date_str = line.split('=', 1)[1]
                        try:
                            # Assumes ISO 8601 format like '2025-12-22 15:00:00.123456+00:00'
                            token_store['expires_in_utc'] = datetime.datetime.fromisoformat(date_str)
                        except ValueError:
                            print(f"Warning: Could not parse expires_in_utc date string: {date_str}")

            print(f"Successfully retrieved tokens for {self.attorney.name} from file.")
        except IOError as e:
            print(f"Error reading token file: {e}")

        return token_store

    # Function to save/overwrite the file
    def save_tokens_to_file(self):
        """Saves or overwrites token information to a file for a given account name."""
        # Ensure the directory exists
        directory = f"{self.attorney.name}\\API"
        if not os.path.exists(directory):
            os.makedirs(directory)
    
        filepath = os.path.join(directory, 'token.txt')
    
        try:
            # Open the file in write mode ('w') - this creates the file if it doesn't exist 
            # and overwrites the contents if it does exist.
            with open(filepath, "w", encoding="utf-8") as api_codes:
                # Write key-value pairs
                api_codes.write(f"access_token={self.token_store.get('access_token', '')}\n")
                api_codes.write(f"refresh_token={self.token_store.get('refresh_token', '')}\n")
                api_codes.write(f"expires_in={self.token_store.get('expires_in', '')}\n")
                api_codes.write(f"expires_in_utc={self.token_store.get('expires_in_utc').isoformat()}\n")
            
            print(f"Successfully saved new tokens to {filepath}")

        except IOError as e:
            print(f"Error saving token file: {e}")


    def is_token_expired(self):
        if self.token_store['expires_in_utc'] is None:
            print("No token found in API folder. Attempting to authenticate and retrieve one.")
            return True # No token stored yet
        return datetime.datetime.now(datetime.timezone.utc) >= self.token_store['expires_in_utc']

    def is_token_valid(self) -> bool:
        return self.token_store['access_token'] != ""


    def refresh_clio_token(self):
        print("Access token expired. Refreshing token...")
            
        if self.token_store['refresh_token'] is None:
            raise Exception("No refresh token available. User must re-authenticate.")

        refresh_data = {
            'Content-type': 'application/x-www-form-urlencoded',
            'grant_type': 'refresh_token',
            'refresh_token': self.token_store['refresh_token'],
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        response = requests.post(self.CLIO_TOKEN_URL, data=refresh_data)
        response.raise_for_status()
        new_token_info = response.json()

        self.token_store['access_token'] = new_token_info['access_token']
        self.token_store['refresh_token'] = new_token_info['refresh_token']
        expires_in_seconds = new_token_info['expires_in']
        self.token_store['expires_in'] = new_token_info['expires_in']
        self.token_store['expires_in_utc'] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expires_in_seconds)
        
        print("Updating local token store with refreshed information")
        self.save_tokens_to_file()

        print("Token refreshed successfully.")

    def make_authenticated_clio_request(self, url, method='GET', **kwargs):
        if self.is_token_expired():
            self.refresh_clio_token()

        if not self.is_token_valid():
            self.get_new_token()

        headers = kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {self.token_store['access_token']}"
        headers['Accept'] = 'application/json'
        kwargs['headers'] = headers

        return requests.request(method, url, **kwargs)