from sys import orig_argv
from pandas import pandas as pd
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
from FileManagement import logResult, getTimeDataPath, read_time_data as fm
from Task import Task as Task
from TimeEntry import TimeEntry as te

# class Task:
#     def __init__(self, taskCode):
#         self.taskCode = taskCode
#         self.taskType = ""

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

# def read_time_data(file_path):
#     """Reads time data from a CSV file."""
#     return pd.read_csv(file_path)

# def convert_task_code_entries(Task):
#     tcode = Task.taskCode
#     ttype = Task.taskType
#     # Code list format will be this: "Task Description string,tcodes index pos,ttypes index pos"
#     current_codes = []
#     tcodes = ["In Court", "In Court Waiting", "Out Of Court"]
#     ttypes = ["Case Development", "Discovery Review", "Hearing/Trial Prep", "Interview In Custody", "Interview Out of Custody", "Negotiations", "Other", "Research/Motions","Travel"]
#     codes_filename = "task_codes.txt"
#     try:
#         open(codes_filename, "x", encoding="utf-8") # If file doesn't exist create one
#     except FileExistsError: # If it already exits, read the contents
#         with open(codes_filename, "r", encoding="utf-8") as codes_file:
#             current_codes.extend([line.strip() for line in codes_file])
#     # with open(codes_filename, "a", encoding="utf-8") as codes_file:
#     #     current_codes.append(codes_file.read().splitlines())

#     # Try to see if we have code mapped already
#     code_found = False
#     for code in current_codes:
#         code_found = False
#         curr_code_desc = code.split(',')[0]
#         curr_code_code = code.split(',')[1]
#         curr_code_type = code.split(',')[2]
#         if curr_code_desc.upper() != tcode.upper():
#             continue
#         else:
#             code_found = True
#             Task.taskCode = tcodes[int(curr_code_code)]
#             Task.taskType = ttypes[int(curr_code_type)] if ttypes[int(curr_code_type)] != '-1' else ""
#             break;

#     if code_found == False: # Map it and append to code file
#         print(f"\nTask code '{tcode}' not found in existing codes. Please map it.")
#         print("Available Task Codes:")
#         for idx, code in enumerate(tcodes):
#             print(f"{idx}: {code}")
#         code_index = input("Enter the index number for the appropriate Task Code: ")
#         if code_index == '2': # If out of court, we need to map a task type as well
#             print("Available Task Types:")
#             for idx, ttype in enumerate(ttypes):
#                 print(f"{idx}: {ttype}")
#             type_index = input("Enter the index number for the appropriate Task Type: ")
#             Task.taskType = ttypes[int(type_index)]
#         else:
#             type_index = -1 # Indicate we don't need type for things in court

#         Task.taskCode = tcodes[int(code_index)]
#         with open(codes_filename, "a", encoding="utf-8") as codes_file:
#             codes_file.write(f"{tcode},{code_index},{type_index}\n")
#             print(f"Added new task code mapping: {tcode},{code_index},{type_index}")


def setup_webdriver(name):
    """Sets up the Selenium WebDriver."""
    options = wd.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_experimental_option("detach", True)  # Keeps browser open after script ends
    driver = wd.Chrome(options=options)
    driver.get('https://east.justiceworks.com/dd7/web/start/31053')  # Replace with actual URL
    login(driver, name) # Call the login function after opening page
    return driver

# def add_time_entry(driver, timeEntry):
#     try:
#         # Find the parent record table that holds all rows
#         parent_xpath = f"//div[@control='recordtable']" 
#         recordtable = ""
#         rowcount = 0 # Row count is measured on the parent div of the input rows in "rowcount" attribute
#         # Wait for the recordtable to be fresh and rowcount to be '1'
#         recordtable = None
#         rowcount = None
#         while True:
#             try:
#                 recordtable = driver.find_element(By.XPATH, parent_xpath)
#                 rowcount = recordtable.get_attribute("rowcount")
#                 if rowcount == '1':
#                     break
#             except Exception as e:
#                 # Catch stale element and retry
#                 print(f"Retrying recordtable fetch due to: {e}")
#             time.sleep(1)

#         time.sleep(1)
#         # Find the specific child row we're adding
#         row_xpath = f"//div[@cid='{rowcount}']" # Figure out which row we're editing using the last count in the row
#         row = recordtable.find_element(By.XPATH, row_xpath)
#         date_field = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col1d")
#         case_inputs = row.find_elements(By.CSS_SELECTOR, "input.ddinput.input_col3d")
#         for inp in case_inputs:
#             if inp.is_displayed():
#                 case_input = inp
#                 break;
#             else:
#                 case_input = None
#         task_code_input = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col4d")
#         time_input = row.find_element(By.CSS_SELECTOR, "input.inputfield.input_col5d")
#         task_type_input = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col11d")
#         try:
#             date_field.clear() # Clear default date value
#             date_field.send_keys(timeEntry.date) # Send out date value
#             date_field.send_keys(Keys.TAB)
#             time.sleep(1) # Let the tab complete and next field load
#         except Exception as e:
#             print(f"Error with date input field on case {timeEntry.caseNum}: {e}")
#             return False
        
#         try:
#             case_input.clear()
#             case_input.send_keys(timeEntry.caseNum)
#             WebDriverWait(driver, 10).until(
#                 EC.visibility_of_element_located((By.CSS_SELECTOR, "div.droplist"))    
#             )
#             drop_list_text = driver.find_element(By.CSS_SELECTOR, "div.droplist")
#             if timeEntry.caseNum not in drop_list_text.text:
#                 print(f"Case number {timeEntry.caseNum} not found in drop down list.")
#                 return False
#             case_input.send_keys(Keys.TAB) # Tab to next field
#             WebDriverWait(driver, 10).until(
#                 EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.droplist"))    
#             )
#         except Exception as e:
#             print(f"Error finding case number input on case {timeEntry.caseNum}: {e}")
#             return False

#         try:
#             task_code_input.clear()
#             task_code_input.send_keys(timeEntry.Task.taskCode)
#             time.sleep(1)
#             task_code_input.send_keys(Keys.TAB) # Tab to next field
#             WebDriverWait(driver, 10).until(
#                 EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.droplist"))    
#             )
#         except Exception as e:
#             print(f"Error finding task code input on case {timeEntry.caseNum}: {e}")
#             return False

#         try:
#             time_input.clear()
#             time_input.send_keys(timeEntry.duration)
#             time.sleep(1) # Let the tab complete and next field load
#             time_input.send_keys(Keys.TAB) # Tab to next field
#         except Exception as e:
#             print(f"Error finding time input on case {timeEntry.caseNum}: {e}")
#             return False

#         # If the task is out of court we have to select a specific task code from a drop down. Hard coded for now, going to create a lookup table that I can append to later.
#         if timeEntry.Task.taskCode == "Out Of Court":
#             try:
#                 task_type_input.send_keys(timeEntry.Task.taskType)
#                 time.sleep(1)
#                 time_input.send_keys(Keys.TAB) # Tab to next field
#                 WebDriverWait(driver, 10).until(
#                     EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.droplist"))    
#                 )
#             except Exception as e:
#                 print(f"Error finding task code input on case {timeEntry.caseNum}: {e}")
#                 return False
#         else:
#             click_toolbar_button_timesheet_clear(driver) # Click save and clear button after timesheet opens up
#             if check_for_error(driver): # Check for any errors
#                 return False
#             else:
#                 return True

#         # Retry clicking the toolbar button to handle stale element exceptions
#         for attempt in range(3):
#             try:
#                 click_toolbar_button_timesheet_clear(driver) # Click save and clear button after timesheet opens up
#                 if check_for_error(driver): # Check for any errors
#                     return False
#                 break
#             except Exception as e:
#                 print(f"Attempt {attempt+1}: Failed to click toolbar button due to: {e}")
#                 time.sleep(2)
#         else:
#             print("Failed to click toolbar button after multiple attempts.")
#             return False

#     except Exception as e:
#         print(f"Error with site on case {timeEntry.caseNum}: {e}")
#         return False

# Begin main script exectution
attorney = input("Enter attorney name (Shelby or Dane): ").strip()
if attorney not in ["Shelby", "Dane"]:
    print("Invalid attorney name. Please enter 'Shelby' or 'Dane'.")
    exit(1)

driver = setup_webdriver(attorney)

print("Reading time sheet data from file...")
time_data = fm.read_time_data(fm.getTimeDataPath(attorney))

d = pd.DataFrame(time_data)

time_list = [] # List to hold TimeEntry objects
for index, row in d.iterrows():
    date = row['Date']
    activity = row['Activity']
    duration = row['Duration']
    case_number = row['Case Number']
    task = Task.Task(activity) # create task object
    task.convert_task_code_entries() # Convert codes to time sheet values
    time_list.append(te.TimeEntry(date, task, duration, case_number, f"{date},{activity},{duration},{case_number}"))
print("All codes mapped!")

input("Press Enter to continue when timesheet is loaded...")
click_toolbar_button_timesheet_clear(driver) # Clear timesheet to one row after it loads
date_str = datetime.now().date().isoformat()
for entry in time_list:
    if entry.add_time_entry(driver) and not check_for_error(driver):
        fm.logResult(f"Entry_Success_{date_str}", f"{datetime.now()}: Added time entry for {entry.date}, {entry.Task.taskCode}, {entry.duration}, {entry.caseNum}\n")
        entry.saveEntry(f"{attorney}\\Successful_Entries_{date_str}.csv") # Save successful entry to file for processing later
    else:
        fm.logResult(f"Entry_Failure_{date_str}", f"{datetime.now()}: Time entry failed to be added for {entry.date}, {entry.Task.taskCode}, {entry.duration}, {entry.caseNum}\n")
        entry.saveEntry(f"{attorney}\\Failed_Entries_{date_str}.csv") # Save failed entry to file for processing later
        click_toolbar_button_delete(driver) # Delete the failed entry row
