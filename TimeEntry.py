from ast import List
from datetime import datetime
from encodings.punycode import T
from math import isnan
from WebInteraction import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from FileManagement import log_result
import time
import Attorney
import logging 

logger = logging.getLogger(__name__)

def sanitize_case(case_num: str) -> str:
    has_c = 'C' in case_num.upper()
    has_r = 'R' in case_num.upper()
    # Convert to list to make adding characters simpler
    case_num_list: list[str] = list(case_num)
    if not has_c: case_num_list.insert(2, 'C')
    if not has_r: case_num_list.insert(3, 'R')
    if len(case_num_list) < 14:
        while len(case_num_list) < 14:
            case_num_list.insert(4, '0')
    # Convert list back to string to get the sanitized case number
    final_string: str = "".join(case_num_list)
    return final_string

class TimeEntry:
    def __init__(self, date: str, Task, duration, caseNum: str, notes: str, originalString: str):
        self.date = date
        self.Task = Task
        self.duration = duration
        self.caseNum = caseNum
        self.notes = notes
        self.originalString = originalString

    def saveEntry(self, success: bool, attorney_name: str) -> None:
        date_str = datetime.now().date().isoformat()
        if success:
            logger.info(f"Saving {self.originalString} to {attorney_name}\\Successful_Entries_{date_str}.csv")
            open (f"{attorney_name}\\Successful_Entries_{date_str}.csv", "a", encoding="utf-8").write(f"{self.originalString}\n")
        else:
            logger.info(f"Saving {self.originalString} to {attorney_name}\\Failed_Entries_{date_str}.csv")
            open (f"{attorney_name}\\Failed_Entries_{date_str}.csv", "a", encoding="utf-8").write(f"{self.originalString}\n")

    def add_time_entry(self, driver) -> bool:
        try:
            # Find the parent record table that holds all rows
            parent_xpath = f"//div[@control='recordtable']" 
            recordtable = ""
            rowcount = 0 # Row count is measured on the parent div of the input rows in "rowcount" attribute
            # Wait for the recordtable to be fresh and rowcount to be '1'
            recordtable = None
            rowcount = None
            while True:
                try:
                    time.sleep(1)
                    recordtable = driver.find_element(By.XPATH, parent_xpath)
                    rowcount = recordtable.get_attribute("rowcount")
                    if rowcount == '1':
                        break
                except Exception as e:
                    # Catch stale element and retry
                    logger.warning(f"Retrying recordtable fetch due to: {e}")
                time.sleep(1)

            time.sleep(.5)
            # Find the specific child row we're adding
            row_xpath = f"//div[@cid='{rowcount}']" # Figure out which row we're editing using the last count in the row
            row = recordtable.find_element(By.XPATH, row_xpath)
            date_field = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col1d")
            if not date_field:
                raise TimeEntryException(f"Date field not found/loaded for {self.caseNum}")
            else:
                date_field.clear() # Clear default date value
                date_field.send_keys(self.date) # Send out date value
                date_field.send_keys(Keys.TAB)
                time.sleep(1) # Let the tab complete and next field load
        
            case_inputs = row.find_elements(By.CSS_SELECTOR, "input.ddinput.input_col3d")
            if not case_inputs:
                raise TimeEntryException(f"Case number input field not found/loaded for {self.caseNum}")
            for inp in case_inputs:
                if inp.is_displayed():
                    case_input = inp
                    break;
                else:
                    case_input = None
            case_input.clear()
            # Handle case numbers with semi-colons in them. This indicates that there may be multiple cases for the same client and were entered under one case in MyCase.
            case_found: bool = False
            droplist_css: str = "div.droplist"
            while case_found == False:
                multi_case_list:List = self.caseNum.split(';')
                for num in multi_case_list:
                    self.caseNum = sanitize_case(num.strip())
                    case_input.send_keys(self.caseNum)
                    # time.sleep(1)
                    wait_for_element_visibility(driver, By.CSS_SELECTOR, droplist_css)
                    drop_list_text = driver.find_element(By.CSS_SELECTOR, droplist_css)
                    if self.caseNum.upper() not in drop_list_text.text.upper():
                        case_input.clear()
                        continue
                    else:
                        case_found = True
                        break
                if case_found == False:
                    raise TimeEntryException(f"Case number {self.caseNum} not found in DefenderData. Check case number/add case to DefenderData.")
            
            case_input.send_keys(Keys.TAB) # Tab to next field
            wait_for_element_invisibility(driver, By.CSS_SELECTOR, droplist_css)            
            
            task_code_input = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col4d")
            if not task_code_input:
                raise TimeEntryException(f"Task code input not found/loaded for {self.caseNum}")
            else:
                task_code_input.clear()
                task_code_input.send_keys(self.Task.taskCode)
                # time.sleep(1)
                wait_for_element_visibility(driver, By.CSS_SELECTOR, droplist_css)
                task_code_input.send_keys(Keys.TAB) # Tab to next field
                #time.sleep(1)
                wait_for_element_invisibility(driver, By.CSS_SELECTOR, droplist_css)
            time_input = row.find_element(By.CSS_SELECTOR, "input.inputfield.input_col5d")
            if not time_input:
                raise TimeEntryException(f"Time input not found/loaded for {self.caseNum}")
            else:
                time_input.clear()
                time_input.send_keys(self.duration)
                # time.sleep(1)
                time_input.send_keys(Keys.TAB) # Tab to next field
                # time.sleep(1) # Let the tab complete and next field load

            # If the task is out of court we have to select a specific task code from a drop down. Hard coded for now, going to create a lookup table that I can append to later.
            task_type_input = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col11d")
            if not task_type_input:
                raise TimeEntryException(f"Task type input not found/loaded for {self.caseNum}\n")
            if self.Task.taskCode == "Out Of Court":
                    # time.sleep(1)
                    task_type_input.send_keys(self.Task.taskType)
                    wait_for_element_visibility(driver, By.CSS_SELECTOR, droplist_css)
                    # time.sleep(1)
                    time_input.send_keys(Keys.TAB) # Tab to next field
                    wait_for_element_invisibility(driver, By.CSS_SELECTOR, "div.droplist")

            if self.notes == "":
                pass # No notes to add
            else:
                notes_input = row.find_element(By.CSS_SELECTOR, "textarea.col.txtinput.timenotes2")
                if not notes_input:
                    raise TimeEntryException(f"Notes input not found/loaded for {self.caseNum}")
                else:
                    notes_input.clear()
                    notes_input.send_keys(self.notes)
                    time.sleep(.25) # Let the data entry complete before saving

            click_toolbar_button_timesheet_clear(driver) # Click save and clear button after timesheet is filled out
            if check_for_error(driver): # Check for any errors
                return False
            else:
                # Check that the record was saved properly by seeing if the case number field is empty now
                attempts: int = 0
                while True and attempts < 5:
                    while True:
                        try:
                            time.sleep(1)
                            save_recordtable = driver.find_element(By.XPATH, parent_xpath)
                            save_rowcount = save_recordtable.get_attribute("rowcount")
                            save_row_xpath = f"//div[@cid='{save_rowcount}']" # Figure out which row we're editing using the last count in the row
                            if save_rowcount == '1':
                                break
                        except Exception:
                            logger.warning("Stale element: retrying save record verification")
                            time.sleep(1)
                    save_row = save_recordtable.find_element(By.XPATH, row_xpath)
                    save_check = save_row.find_elements(By.CSS_SELECTOR, "input.ddinput.input_col3d")
                    for num in save_check:
                        if not num.text:
                            return True
                        else:
                            attempts += 1
                            logger.warn("Case save timeout, waiting before trying again")
                            time.sleep(3)
                            click_toolbar_button_timesheet_clear(driver, logger) # Try to save record again
            return False

        except TimeEntryException as e:
            logger.error(f"TimeEntryException: {e.message}")
            return False
        except Exception as e:
            logger.error(f"Error with site on case {self.caseNum}: {e}")
            return False

    def case_found(self, drop_list_text):
        return self.caseNum.upper() in drop_list_text.text.upper()
        

class TimeEntryException(Exception):
    """Custom exception for TimeEntry errors."""
    def __init__(self, message):
        self.message = message
    pass