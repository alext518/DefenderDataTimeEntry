from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import logging 

logger = logging.getLogger(__name__)

def login(driver, username, password):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'userid'))
    )
    username_input = driver.find_element(By.ID, 'userid')
    password_input = driver.find_element(By.ID, 'password')

    username_input.clear()
    password_input.clear()

    username_input.send_keys(username)  # Pass the username
    password_input.send_keys(password)  # Pass the password

    time.sleep(1)
    password_input.send_keys(Keys.RETURN) # Press Enter to submit the form

    xpath = f"//div[contains(@class, 'toolbutton') and contains(@controlinit, 'layoutId:5028')]"
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return True
    except:
        return False

def setup_webdriver(username, password):
    """Sets up the Selenium WebDriver."""
    options = wd.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_experimental_option("detach", False)  # Keeps browser open after script ends
    driver = wd.Chrome(options=options)
    driver.get('https://east.justiceworks.com/dd7/web/start/31053')  # Replace with actual URL
    
    while True:
       if(login(driver, username, password)): # Call the login function after opening page
           logger.info("Login successful!")
           break
       else:
           logger.warning("Login stuck, retrying")
           driver.refresh() # Refresh and try again if login failed

    click_toolbar_button_by_layout_id(driver, '5028') # Click the time entry button
    return driver

def click_toolbar_button_by_layout_id(driver, layout_id, timeout=10):
    """
    Clicks a toolbar button based on its layoutId in the controlinit attribute.

    Args:
        driver: Selenium WebDriver instance.
        layout_id: The layoutId string to match (e.g., '5028').
        timeout: Maximum time to wait for the element (default is 10 seconds).
    """
    xpath = f"//div[contains(@class, 'toolbutton') and contains(@controlinit, 'layoutId:{layout_id}')]"
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        driver.execute_script("arguments[0].click();", button)
        logger.info(f"Clicked toolbar button with layoutId: {layout_id}")
    except Exception as e:
        logger.error(f"Failed to click toolbar button with layoutId {layout_id}: {e}")

def click_toolbar_button_timesheet_clear(driver, timeout=10):
    """
    Clicks a toolbar button based on its layoutId in the controlinit attribute.

    Args:
        driver: Selenium WebDriver instance.
        layout_id: The layoutId string to match (e.g., '5028').
        timeout: Maximum time to wait for the element (default is 10 seconds).
    """
    xpath = f"//div[contains(@class, 'toolbutton') and contains(@controlinit, 'layoutId:5028') and contains(@controlinit, 'preNavAction:save_new')]"
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        driver.execute_script("arguments[0].click();", button)
        logger.info(f"Clicked toolbar button Save/Clear")
    except Exception as e:
        logger.error(f"Failed to click toolbar button with layoutId 5028: {e}")

def click_toolbar_button_delete(driver, timeout=10):
    xpath = f"//div[contains(@class, 'toolbutton') and contains(@controlinit, 'action:delete,refresheditbtns')]"
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        driver.execute_script("arguments[0].click();", button)
        logger.info(f"Clicked toolbar button Delete")
        # After clicking the delete button, wait for the alert and accept it
        try:
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()  # This presses "OK" or "Enter" on the prompt
            logger.info("Alert accepted.")
        except Exception as e:
            logger.warning(f"No alert appeared or failed to accept: {e}")
        click_toolbar_button_timesheet_clear(driver)
    except Exception as e:
        logger.error(f"Failed to click toolbar button delete: {e}")

def add_new_time_row(driver):
    xpath = f"//div[@class = 'toolbutton new_without_data']"
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click()", button)
        logger.info("Clicked new row button")
    except Exception as e:
        logger.error(f"Error adding new row. {e}")

def check_for_error(driver):
    try:
        html = driver.source()
        validation_fail = html.find_element(By.CLASS_NAME, "dialogblocker")
        if validation_fail.is_displayed():
            close_button = validation_fail.find_element(By.TAG_NAME, "input")
            close_button.click()
            return True
    except:
        return False

def wait_for_element_presence(driver, type: By, identity) -> bool:
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((type, identity))    
        )
        return True
    except:
        return False

def wait_for_element_visibility(driver, type: By, identity) -> bool:
    try:
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((type, identity))    
        )
        return True
    except:
        return False

def wait_for_element_invisibility(driver, type: By, identity) -> bool:
    try:
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((type, identity))    
        )
        return True
    except:
        return False