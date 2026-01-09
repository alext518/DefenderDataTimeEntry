import logging 
logger = logging.getLogger(__name__)
class Attorney:
    def __init__(self, name, system):
        self.name = name
        self.system = system
        self.client_id = ""
        self.client_secret = ""
        self.username = ""
        self.password = ""
        self.email = ""
        self.user_id = ""
        self.getCredentials()

    def getCredentials(self):
        with open(self.name + '\\Account.acc', "r", encoding="utf-8") as account_file:
            for line in account_file:
                line = line.strip()
                if line.startswith("username="):
                    self.username = line.split('=', 1)[1]
                elif line.startswith("password="):
                    self.password = line.split('=', 1)[1]
                elif line.startswith("email="):
                    self.email = line.split('=', 1)[1]
                elif line.startswith("user_id="):
                    self.user_id = line.split('=', 1)[1]
        logger.info(f"Successfully retrieved {self.name}'s credentials!")

    def setup_webdriver(attorney):
        """Sets up the Selenium WebDriver."""
        options = wd.ChromeOptions()
        options.add_argument("--log-level=3")
        options.add_experimental_option("detach", False)  # Keeps browser open after script ends
        driver = wd.Chrome(options=options)
        driver.get('https://east.justiceworks.com/dd7/web/start/31053')  # Replace with actual URL
    
        while True:
           if(login(driver, attorney)): # Call the login function after opening page
               logger.info("Login successful!")
               break
           else:
               logger.warning("Login stuck, retrying")
               driver.refresh() # Refresh and try again if login failed

        click_toolbar_button_by_layout_id(driver, '5028', logger = logger) # Click the time entry button
        return driver

    def get_access_keys(self) -> None:
        with open(self.name + '\\API\\apiaccess.api', "r", encoding="utf-8") as api_codes:
            for line in api_codes:
                line = line.strip()
                if line.startswith("client_id="):
                    self.client_id = line.split('=', 1)[1]
                elif line.startswith("client_secret="):
                    self.client_secret = line.split('=', 1)[1]
        logger.info(f"Successfully retrieved {name}'s api keys!")

    def process_data(self):
        system.parse(system.get_data(self.name, logger), logger)