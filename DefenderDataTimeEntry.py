from pandas import pandas as pd
from ClioAPIAccess import ClioAPIHelper
from ClioActivities import ClioActivities
import DDActivity
from selenium import webdriver as wd
from datetime import datetime
from FileManagement import log_result, get_time_data_path, read_time_data
from Task import Task
from TimeEntry import TimeEntry as te
from WebInteraction import *
from Attorney import Attorney
from DDActivity import DDActivity
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("DefenderDataTimeEntry.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_access_keys(name, logger = None):
    client_id = ""
    client_secret = ""
    with open(name + '\\API\\apiaccess.api', "r", encoding="utf-8") as api_codes:
        for line in api_codes:
            line = line.strip()
            if line.startswith("client_id="):
                client_id = line.split('=', 1)[1]
            elif line.startswith("client_secret="):
                client_secret = line.split('=', 1)[1]
        logger.info(f"Successfully retrieved {name}'s api keys!")
    return client_id, client_secret


def setup_webdriver(attorney, logger = None):
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

def populate_time_list(time_data: pd.DataFrame, logger = None) -> list[te]:
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
    
        task = Task(activity, logger) # create task object
        time_list.append(te(date, task, duration, case_number, notes, f"{date},{activity},{duration},{case_number},{notes}"))

    return time_list

def remove_failed_entries(time_list: list[te], case_number: str, attorney: Attorney, logger = None) -> list[te]:
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

def create_mycase_entry_files(attorney: Attorney, logger = None) -> None:
    try:
        date_str = datetime.now().date().isoformat()
        open (f"{attorney.name}\\Successful_Entries_{date_str}.csv", "x", encoding="utf-8").write(f"Date,Activity,Duration/Quantity,Case Number,Description\n")
        logger.info(f"Successful_Entries file created!")
    except FileExistsError as e:
        logger.warning(f"{e}")
    try:
        open (f"{attorney.name}\\Failed_Entries_{date_str}.csv", "x", encoding="utf-8").write(f"Date,Activity,Duration/Quantity,Case Number,Description\n")
        logger.info(f"Failed_Entries file created!")
    except FileExistsError as e:
        logger.warning(f"{e}")

# Begin main script exectution
name = input("Enter attorney name (Shelby, Dane, or John): ").strip()
# name = 'John' # hard-coding for easier debugging
if name not in ["Shelby", "Dane", "John"]:
    print("Invalid attorney name. Please enter 'Shelby', 'Dane', or 'John'.")
    exit(1)
else:
    attorney = Attorney(name, logger = logger)

if name == "John": # add time entries via Clio API
    dd_activities = []
    # Check current API Status
    access_keys = get_access_keys(name)
    clio_api = ClioAPIHelper(access_keys[0], access_keys[1], attorney)
    while True:
        valid_token: bool = not clio_api.is_token_expired() and clio_api.is_token_valid()
        if not valid_token:
            clio_api.get_new_token()
            continue # Start the while loop over to validate new token

        # Get activity data for provided dates
        start_date = '2025-12-01' # hard-coding for easier debugging
        end_date = '2025-12-31' # hard-coding for easier debugging
        # start_date = input("Enter activity start date YYYY-MM-DD: ")
        # end_date = input("Enter activity end date YYYY-MM-DD: ")

        activities = ClioActivities(access_keys[0], access_keys[1], attorney, start_date, end_date, logger = logger)
        print("Displaying activities in defender data format:")
        for activity in activities.activities_data['data']:
            activities.print_activity(activity)
            date = activity['date'] if activity['date'] else "9/9/9999"                
            task_code = ""
            task_description = ""
            case_number = activity['matter']['number'] if activity['matter'] else ""
            duration = activity['quantity_in_hours'] if activity['quantity_in_hours'] else "0.0"
            if activity['activity_description']:
                if "out of court" in activity['activity_description']['name'].lower():
                    task = activity['activity_description']['name'].split('-')
                    task_code = task[0].strip()
                    task_description = task[1].strip()
                else:
                    task_code = activity['activity_description']['name']
            user = activity['user'] if activity['user'] else ""                
            description = activity['note'] if activity['note'] else ""
            dd_activities.append(DDActivity(date, case_number, duration, task_code, user, description, task_description))
        input() # pause for testing
        break # End program for testing
else: # add time entries via CSV file
    driver = setup_webdriver(attorney, logger = logger) # Start webdriver
    create_mycase_entry_files(attorney, logger = logger) # Create files if needed
    logger.info("Reading time sheet data from file...")
    time_data = read_time_data(get_time_data_path(attorney.name), logger = logger)

    time_list: list[te] = populate_time_list(time_data, logger = logger) # List to hold TimeEntry objects

    logger.info("All codes mapped!")
    xpath = f"//input[contains(@class, 'ddinput input_col3d')]"
    while True:
        if(wait_for_element_presence(driver, By.XPATH, xpath)): # Wait for timesheet to load to avoid user interaction
            logger.info("Timesheet loaded successfully!")
            break
        else:
            logger.info("Waiting for timesheet to load...")
        
    date_str = datetime.now().date().isoformat()

    # We should eventually run out of items in time_list now, and we'll keep checking until that happens
    while any(time_list):
        for entry in time_list:
            if entry.add_time_entry(driver, logger = logger) and not check_for_error(driver):
                entry.saveEntry(True, attorney, logger = logger) # Save successful entry to file for logging
                time_list.pop(0) # remove successful element so we don't add twice
                break
            else:
                # DONE: Add function to loop through data list and remove matching case number entries and add them to the failure list all at once
                remove_failed_entries(time_list, entry.caseNum, attorney, logger = logger)
                click_toolbar_button_delete(driver, logger = logger) # Delete the failed entry row
                break # restart loop through time_list with all missing case time entries removed

    logger.info("All cases processed successfully! Please review success and failure time entries.")
    driver.close()
    check_for_error(driver)
