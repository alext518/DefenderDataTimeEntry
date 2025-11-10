from pandas import pandas as pd
from selenium import webdriver as wd
from datetime import datetime
from FileManagement import log_result, get_time_data_path, read_time_data
from Task import Task
from TimeEntry import TimeEntry as te
from WebInteraction import *
from Attorney import Attorney

def setup_webdriver(attorney):
    """Sets up the Selenium WebDriver."""
    options = wd.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_experimental_option("detach", True)  # Keeps browser open after script ends
    driver = wd.Chrome(options=options)
    driver.get('https://east.justiceworks.com/dd7/web/start/31053')  # Replace with actual URL
    
    while True:
       if(login(driver, attorney)): # Call the login function after opening page
           print("Login successful!")
           break
       else:
           print("Login stuck, retrying")
           driver.refresh() # Refresh and try again if login failed

    click_toolbar_button_by_layout_id(driver, '5028') # Click the time entry button
    return driver

def populate_time_list(time_data: pd.DataFrame) -> list[te]:
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

def remove_failed_entries(time_list: list[te], case_number: str, attorney: Attorney) -> list[te]:
    """Remove all entries of a failed time entry"""
    try:
        for entry in time_list:
            if entry.caseNum == case_number:
                entry.saveEntry(False, attorney)
                time_list.remove(entry.caseNum)
    except ValueError as ve:
        # TODO: Log the message as "all cases removed" since this error indicates the list is now empty of that case number
        print(f"Removed all instances of {entry.caseNum} from the time list.")
        return

# Begin main script exectution
name = input("Enter attorney name (Shelby or Dane): ").strip()
if name not in ["Shelby", "Dane"]:
    print("Invalid attorney name. Please enter 'Shelby' or 'Dane'.")
    exit(1)
else:
    attorney = Attorney(name)

driver = setup_webdriver(attorney) # Start webdriver

print("Reading time sheet data from file...")
time_data = read_time_data(get_time_data_path(attorney.name))

time_list: list[te] = populate_time_list(time_data) # List to hold TimeEntry objects

print("All codes mapped!")
xpath = f"//input[contains(@class, 'ddinput input_col3d')]"
while True:
    if(wait_for_element(driver, xpath)): # Wait for timesheet to load to avoid user interaction
        print("Timesheet loaded successfully!")
        break
    else:
        print("Waiting for timesheet to load...")
        
date_str = datetime.now().date().isoformat()
for entry in time_list:
    if entry.add_time_entry(driver) and not check_for_error(driver):
        entry.saveEntry(True, attorney) # Save successful entry to file for processing later
    else:
        # TODO: Add function to loop through data list and remove matching case number entries and add them to the failure list all at once
        remove_failed_entries(time_list, entry.caseNum, attorney)
        click_toolbar_button_delete(driver) # Delete the failed entry row
