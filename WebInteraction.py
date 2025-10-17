from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

def login(driver, name):
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'userid'))
    )
    username_input = driver.find_element(By.ID, 'userid')
    username_input.clear()
    if name == "Shelby":
        username_input.send_keys('Stowne')  # Pass the username
    if name == "Dane":
        username_input.send_keys('DPeddicord')  # Pass the username

    password_input = driver.find_element(By.ID, 'password')
    password_input.clear()
    if name == "Shelby":
        password_input.send_keys('Mary-Elizabeth2024!')  # Pass the password
    if name == "Dane":
        password_input.send_keys('Gremlin12!')
    
        time.sleep(3)
    password_input.send_keys(Keys.RETURN) # Press Enter to submit the form

    # Navigate to the time entry screen after logging in
    input("Press Enter to continue when logged in...")
    click_toolbar_button_by_layout_id(driver, '5028') # Click the time entry button
    time.sleep(10) # Letting time entry page load

    # Navigate to the time entry screen after logging in
    input("Press Enter to continue when logged in...")
    click_toolbar_button_by_layout_id(driver, '5028') # Click the time entry button
    time.sleep(10) # Letting time entry page load

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
        print(f"Clicked toolbar button with layoutId: {layout_id}")
    except Exception as e:
        print(f"Failed to click toolbar button with layoutId {layout_id}: {e}")

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
        print(f"Clicked toolbar button Save/Clear")
    except Exception as e:
        print(f"Failed to click toolbar button with layoutId 5028: {e}")

def click_toolbar_button_delete(driver, timeout=10):
    xpath = f"//div[contains(@class, 'toolbutton') and contains(@controlinit, 'action:delete,refresheditbtns')]"
    try:
        button = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        driver.execute_script("arguments[0].click();", button)
        print(f"Clicked toolbar button Delete")
        # After clicking the delete button, wait for the alert and accept it
        try:
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.accept()  # This presses "OK" or "Enter" on the prompt
            print("Alert accepted.")
        except Exception as e:
            print(f"No alert appeared or failed to accept: {e}")
        click_toolbar_button_timesheet_clear(driver)
    except Exception as e:
        print(f"Failed to click toolbar button delete: {e}")

def add_new_time_row(driver):
    xpath = f"//div[@class = 'toolbutton new_without_data']"
    try:
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click()", button)
        print("Clicked new row button")
    except Exception as e:
        print(f"Error adding new row. {e}")

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
