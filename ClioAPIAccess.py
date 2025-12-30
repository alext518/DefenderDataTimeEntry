# clio_api_helper.py
from base_api_helper import BaseAPIHelper
import urllib.parse
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import Attorney
import datetime
import logging

class ClioAPIHelper(BaseAPIHelper):
    def __init__(self, client_id, client_secret, attorney, redirect_uri="https://app.clio.com/oauth/approval", logger = None):
        super().__init__(
            client_id,
            client_secret,
            attorney,
            auth_url="https://app.clio.com/oauth/authorize",
            token_url="https://app.clio.com/oauth/token?",
            api_url="https://app.clio.com/api/v4/",
            token_file_path=f"{attorney.name}\\API\\token.txt",
            redirect_uri=redirect_uri
        )
        self.logger = logger

    def get_new_token(self):
        auth_url = (
            f"{self.auth_url}?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={urllib.parse.quote(self.redirect_uri)}&"
        )
        options = wd.ChromeOptions()
        options.add_argument("--log-level=3")
        options.add_experimental_option("detach", True)
        driver = wd.Chrome(options=options)
        driver.get(auth_url)
        email = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        if email:
            email.send_keys(self.attorney.email)
            button = driver.find_element(By.ID, "next")
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
            print("Allow access button not found. Click manually then press enter key here.")
            input()
        WebDriverWait(driver, 60).until(
            EC.title_contains("Success code=")
        )
        full_title_text = driver.title
        prefix = "Success code="
        if prefix in full_title_text:
            authorization_code = full_title_text.split(prefix)[1].strip()
        else:
            self.logger.error("Could not find the authorization code in the page title.")
            driver.close()
            raise Exception("Could not find the authorization code in the page title.")
        self.logger.info(f"Success code acquired: {authorization_code}")
        driver.close()
        token_data = {
            'Content-type': 'application/x-www-form-urlencoded',
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        try:
            response = requests.post(self.token_url, data=token_data)
            response.raise_for_status()
            token_info = response.json()
            self.token_store = token_info
            self.token_store['expires_in_utc'] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=token_info['expires_in'])
            self.logger.info(f"\nSuccessfully obtained access token: \n\tToken: {token_info['access_token']} \n\tExpires in: {token_info['expires_in']} \n\tRefresh Token:{token_info['refresh_token']}")
            self.save_tokens_to_file()
        except requests.RequestException as e:
            self.logger.error("API request failed: %s", e)
            print(f"API request failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
            print(f"Unexpected error occurred: {e}")