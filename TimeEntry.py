from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

class TimeEntry:
    def __init__(self, date, Task, duration, caseNum, originalString):
        self.date = date
        self.Task = Task
        self.duration = duration
        self.caseNum = caseNum
        self.originalString = originalString

    def saveEntry(self, file_name):
        print(f"Saving {self.originalString} to {file_name}")
        open (file_name, "a", encoding="utf-8").write(f"{self.originalString}\n")

    def add_time_entry(self, driver):
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
                    recordtable = driver.find_element(By.XPATH, parent_xpath)
                    rowcount = recordtable.get_attribute("rowcount")
                    if rowcount == '1':
                        break
                except Exception as e:
                    # Catch stale element and retry
                    print(f"Retrying recordtable fetch due to: {e}")
                time.sleep(1)

            time.sleep(1)
            # Find the specific child row we're adding
            row_xpath = f"//div[@cid='{rowcount}']" # Figure out which row we're editing using the last count in the row
            row = recordtable.find_element(By.XPATH, row_xpath)
            date_field = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col1d")
            case_inputs = row.find_elements(By.CSS_SELECTOR, "input.ddinput.input_col3d")
            for inp in case_inputs:
                if inp.is_displayed():
                    case_input = inp
                    break;
                else:
                    case_input = None
            task_code_input = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col4d")
            time_input = row.find_element(By.CSS_SELECTOR, "input.inputfield.input_col5d")
            task_type_input = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col11d")
            try:
                date_field.clear() # Clear default date value
                date_field.send_keys(self.date) # Send out date value
                date_field.send_keys(Keys.TAB)
                time.sleep(1) # Let the tab complete and next field load
            except Exception as e:
                print(f"Error with date input field on case {self.caseNum}: {e}")
                return False
        
            try:
                case_input.clear()
                case_input.send_keys(self.caseNum)
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.droplist"))    
                )
                drop_list_text = driver.find_element(By.CSS_SELECTOR, "div.droplist")
                if self.caseNum not in drop_list_text.text:
                    print(f"Case number {self.caseNum} not found in drop down list.")
                    return False
                case_input.send_keys(Keys.TAB) # Tab to next field
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.droplist"))    
                )
            except Exception as e:
                print(f"Error finding case number input on case {self.caseNum}: {e}")
                return False

            try:
                task_code_input.clear()
                task_code_input.send_keys(self.Task.taskCode)
                time.sleep(1)
                task_code_input.send_keys(Keys.TAB) # Tab to next field
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.droplist"))    
                )
            except Exception as e:
                print(f"Error finding task code input on case {self.caseNum}: {e}")
                return False

            try:
                time_input.clear()
                time_input.send_keys(self.duration)
                time.sleep(1) # Let the tab complete and next field load
                time_input.send_keys(Keys.TAB) # Tab to next field
            except Exception as e:
                print(f"Error finding time input on case {self.caseNum}: {e}")
                return False

            # If the task is out of court we have to select a specific task code from a drop down. Hard coded for now, going to create a lookup table that I can append to later.
            if self.Task.taskCode == "Out Of Court":
                try:
                    task_type_input.send_keys(self.Task.taskType)
                    time.sleep(1)
                    time_input.send_keys(Keys.TAB) # Tab to next field
                    WebDriverWait(driver, 10).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.droplist"))    
                    )
                except Exception as e:
                    print(f"Error finding task code input on case {self.caseNum}: {e}")
                    return False
            else:
                click_toolbar_button_timesheet_clear(driver) # Click save and clear button after timesheet opens up
                if check_for_error(driver): # Check for any errors
                    return False
                else:
                    return True

            # Retry clicking the toolbar button to handle stale element exceptions
            for attempt in range(3):
                try:
                    click_toolbar_button_timesheet_clear(driver) # Click save and clear button after timesheet opens up
                    if check_for_error(driver): # Check for any errors
                        return False
                    break
                except Exception as e:
                    print(f"Attempt {attempt+1}: Failed to click toolbar button due to: {e}")
                    time.sleep(2)
            else:
                print("Failed to click toolbar button after multiple attempts.")
                return False

        except Exception as e:
            print(f"Error with site on case {self.caseNum}: {e}")
            return False