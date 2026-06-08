from ast import List
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import logging

from WebInteraction import (
    wait_for_element_visibility,
    wait_for_element_invisibility,
    click_toolbar_button_timesheet_clear,
    check_for_error,
)

logger = logging.getLogger(__name__)

def sanitize_case(case_num: str) -> str:
    has_c = 'C' in case_num.upper()
    has_r = 'R' in case_num.upper()
    case_num_list: list[str] = list(case_num)
    if not has_c: case_num_list.insert(2, 'C')
    if not has_r: case_num_list.insert(3, 'R')
    if len(case_num_list) < 14:
        while len(case_num_list) < 14:
            case_num_list.insert(4, '0')
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
            open(f"{attorney_name}\\Successful_Entries_{date_str}.csv", "a", encoding="utf-8").write(f"{self.originalString}\n")
        else:
            logger.info(f"Saving {self.originalString} to {attorney_name}\\Failed_Entries_{date_str}.csv")
            open(f"{attorney_name}\\Failed_Entries_{date_str}.csv", "a", encoding="utf-8").write(f"{self.originalString}\n")

    def add_time_entry(self, driver) -> bool:
        try:
            parent_xpath = "//div[@control='recordtable']"
            droplist_css = "div.droplist"

            # Wait for the recordtable and get rowcount
            for _ in range(5):
                try:
                    wait_for_element_visibility(driver, By.XPATH, parent_xpath)
                    recordtable = driver.find_element(By.XPATH, parent_xpath)
                    rowcount = recordtable.get_attribute("rowcount")
                    if rowcount == '1':
                        break
                except Exception as e:
                    logger.warning(f"Retrying recordtable fetch due to: {e}")
                    time.sleep(1)
            else:
                raise TimeEntryException("Could not find recordtable with rowcount == 1")

            time.sleep(0.5)
            row_xpath = f"//div[@cid='{rowcount}']"

            # Always re-find row from driver, not from recordtable
            wait_for_element_visibility(driver, By.XPATH, row_xpath)
            row = driver.find_element(By.XPATH, row_xpath)

            # Date field
            date_field = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col1d")
            if not date_field:
                raise TimeEntryException(f"Date field not found/loaded for {self.caseNum}")
            date_field.clear()
            date_field.send_keys(self.date)
            date_field.send_keys(Keys.TAB)
            time.sleep(1)

            # Case number input
            case_inputs = row.find_elements(By.CSS_SELECTOR, "input.ddinput.input_col3d")
            if not case_inputs:
                raise TimeEntryException(f"Case number input field not found/loaded for {self.caseNum}")
            case_input = next((inp for inp in case_inputs if inp.is_displayed()), None)
            if not case_input:
                raise TimeEntryException(f"No visible case input for {self.caseNum}")
            case_input.clear()

            # Handle multiple case numbers
            case_found = False
            multi_case_list: List = self.caseNum.split(';')
            for num in multi_case_list:
                sanitized = sanitize_case(num.strip())
                case_input.send_keys(sanitized)
                wait_for_element_visibility(driver, By.CSS_SELECTOR, droplist_css)
                drop_list_text = driver.find_element(By.CSS_SELECTOR, droplist_css)
                if sanitized.upper() in drop_list_text.text.upper():
                    case_found = True
                    self.caseNum = sanitized
                    break
                else:
                    case_input.clear()
            if not case_found:
                raise TimeEntryException(f"Case number {self.caseNum} not found in DefenderData. Check case number/add case to DefenderData.")
            case_input.send_keys(Keys.TAB)
            wait_for_element_invisibility(driver, By.CSS_SELECTOR, droplist_css)

            # Task code input
            row = driver.find_element(By.XPATH, row_xpath)  # Re-find row after DOM change
            task_code_input = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col4d")
            if not task_code_input:
                raise TimeEntryException(f"Task code input not found/loaded for {self.caseNum}")
            task_code_input.clear()
            task_code_input.send_keys(self.Task.taskCode)
            wait_for_element_visibility(driver, By.CSS_SELECTOR, droplist_css)
            task_code_input.send_keys(Keys.TAB)
            wait_for_element_invisibility(driver, By.CSS_SELECTOR, droplist_css)

            # Time input
            row = driver.find_element(By.XPATH, row_xpath)
            time_input = row.find_element(By.CSS_SELECTOR, "input.inputfield.input_col5d")
            if not time_input:
                raise TimeEntryException(f"Time input not found/loaded for {self.caseNum}")
            time_input.clear()
            time_input.send_keys(self.duration)
            time_input.send_keys(Keys.TAB)
            time.sleep(0.5)

            # Task type input (for "Out Of Court")
            row = driver.find_element(By.XPATH, row_xpath)
            task_type_input = row.find_element(By.CSS_SELECTOR, "input.ddinput.input_col11d")
            if not task_type_input:
                raise TimeEntryException(f"Task type input not found/loaded for {self.caseNum}")
            if self.Task.taskCode == "Out Of Court":
                task_type_input.send_keys(self.Task.taskType)
                wait_for_element_visibility(driver, By.CSS_SELECTOR, droplist_css)
                time_input.send_keys(Keys.TAB)
                wait_for_element_invisibility(driver, By.CSS_SELECTOR, droplist_css)

            # Notes input
            if self.notes:
                row = driver.find_element(By.XPATH, row_xpath)
                notes_input = row.find_element(By.CSS_SELECTOR, "textarea.col.txtinput.timenotes2")
                if not notes_input:
                    raise TimeEntryException(f"Notes input not found/loaded for {self.caseNum}")
                notes_input.clear()
                notes_input.send_keys(self.notes)
                time.sleep(0.25)

            click_toolbar_button_timesheet_clear(driver)
            if check_for_error(driver):
                return False

            # Verify save by checking if the case number field is empty
            attempts = 0
            while attempts < 5:
                try:
                    time.sleep(1)
                    save_row = driver.find_element(By.XPATH, row_xpath)
                    save_check = save_row.find_elements(By.CSS_SELECTOR, "input.ddinput.input_col3d")
                    if all(not num.get_attribute("value") for num in save_check):
                        return True
                    else:
                        attempts += 1
                        logger.warning("Case save timeout, waiting before trying again")
                        time.sleep(3)
                        click_toolbar_button_timesheet_clear(driver)
                except Exception:
                    logger.warning("Stale element: retrying save record verification")
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