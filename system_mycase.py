from system_base_interface import system_base
from Attorney import Attorney
import pandas as pd
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from Task import Task
from TimeEntry import TimeEntry as te
import WebInteraction as wi
from datetime import datetime
import logging 

logger = logging.getLogger(__name__)

class system_mycase(system_base):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.api_key = api_key

    def get_data(self, attorney_name: str, file_reader = pd.read_csv):
        """Reads time data from a CSV file."""
        path: str = attorney_name + '/current_time_report_final.csv'
        try:
            return file_reader(path)
        except Exception as e:
            logger.error(f"Failed to read time data: {e}")

    def create_mycase_entry_files(self, attorney_name: str) -> None:
        try:
            date_str = datetime.now().date().isoformat()
            open (f"{attorney_name}\\Successful_Entries_{date_str}.csv", "x", encoding="utf-8").write(f"Date,Activity,Duration/Quantity,Case Number,Description\n")
            logger.info(f"Successful_Entries file created!")
        except FileExistsError as e:
            logger.warning(f"{e}")
        try:
            open (f"{attorney_name}\\Failed_Entries_{date_str}.csv", "x", encoding="utf-8").write(f"Date,Activity,Duration/Quantity,Case Number,Description\n")
            logger.info(f"Failed_Entries file created!")
        except FileExistsError as e:
            logger.warning(f"{e}")

    def populate_time_list(self, time_data: pd.DataFrame) -> list[te]:
        """Populate time_list with data from CSV file"""
        data = pd.DataFrame(time_data)
        data.fillna("", inplace=True) # Replace NaN with empty strings
        time_list: list[te] = []
        for index, row in data.iterrows():
            date = row['Date']
            activity = row['Activity']
            duration = row['Duration/Quantity']
            case_number = row['Case Number']
            notes = row['Description']
    
            task = Task(activity) # create task object
            time_list.append(te(date, task, duration, case_number, notes, f"{date},{activity},{duration},{case_number},{notes}"))

        return time_list

    def remove_failed_entries(self, time_list: list[te], case_number: str, attorney_name: str) -> list[te]:
        """Remove all entries of a failed time entry"""
        try:
            while any(item.caseNum == case_number for item in time_list):
                for index, item in enumerate(time_list):
                    if case_number in item.caseNum:
                        item.saveEntry(False, attorney, logger)
                        del time_list[index]
                        break # break loop to begin search again
        except ValueError as ve:
            # DONE: Log the message as "all cases removed" since this error indicates the list is now empty of that case number
            logger.info(f"Removed all instances of {entry.caseNum} from the time list.")
            return

    def parse(self, data, attorney_name, username, password):
        driver = wi.setup_webdriver(username, password) # Start webdriver
        self.create_mycase_entry_files(attorney_name) # Create files if needed
        logger.info("Reading time sheet data from file...")
        #time_data = read_time_data(get_time_data_path(attorney.name), logger = logger)

        time_list: list[te] = self.populate_time_list(data) # List to hold TimeEntry objects

        logger.info("All codes mapped!")
        xpath = f"//input[contains(@class, 'ddinput input_col3d')]"
        while True:
            if(wi.wait_for_element_presence(driver, By.XPATH, xpath)): # Wait for timesheet to load to avoid user interaction
                logger.info("Timesheet loaded successfully!")
                break
            else:
                logger.info("Waiting for timesheet to load...")
        
        # We should eventually run out of items in time_list now, and we'll keep checking until that happens
        while any(time_list):
            for entry in time_list:
                if entry.add_time_entry(driver) and not wi.check_for_error(driver):
                    entry.saveEntry(True, attorney_name) # Save successful entry to file for logging
                    time_list.pop(0) # remove successful element so we don't add twice
                    break
                else:
                    # DONE: Add function to loop through data list and remove matching case number entries and add them to the failure list all at once
                    self.remove_failed_entries(time_list, entry.caseNum, attorney_name)
                    click_toolbar_button_delete(driver) # Delete the failed entry row
                    break # restart loop through time_list with all missing case time entries removed

        logger.info("All cases processed successfully! Please review success and failure time entries.")
        driver.close()
        check_for_error(driver)