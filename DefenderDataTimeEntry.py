from tabnanny import check
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
    options.add_experimental_option("detach", False)  # Keeps browser open after script ends
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
        while any(item.caseNum == case_number for item in time_list):
            for index, item in enumerate(time_list):
                if case_number in item.caseNum:
                    item.saveEntry(False, attorney)
                    del time_list[index]
                    break # break loop to begin search again
    except ValueError as ve:
        # TODO: Log the message as "all cases removed" since this error indicates the list is now empty of that case number
        print(f"Removed all instances of {entry.caseNum} from the time list.")
        return

def create_mycase_entry_files(attorney: Attorney) -> None:
    try:
        date_str = datetime.now().date().isoformat()
        open (f"{attorney.name}\\Successful_Entries_{date_str}.csv", "x", encoding="utf-8").write(f"Date,Activity,Duration/Quantity,Case Number,Description\n")
        print(f"Successful_Entries file created!")
    except FileExistsError as e:
        print(f"{e}")
    try:
        open (f"{attorney.name}\\Failed_Entries_{date_str}.csv", "x", encoding="utf-8").write(f"Date,Activity,Duration/Quantity,Case Number,Description\n")
        print(f"Failed_Entries file created!")
    except FileExistsError as e:
        print(f"{e}")

# Begin main script exectution
name = input("Enter attorney name (Shelby or Dane): ").strip()
if name not in ["Shelby", "Dane", "John"]:
    print("Invalid attorney name. Please enter 'Shelby', 'Dane', or 'John'.")
    exit(1)
else:
    attorney = Attorney(name)

driver = setup_webdriver(attorney) # Start webdriver
create_mycase_entry_files(attorney) # Create files if needed
print("Reading time sheet data from file...")
time_data = read_time_data(get_time_data_path(attorney.name))

time_list: list[te] = populate_time_list(time_data) # List to hold TimeEntry objects

print("All codes mapped!")
xpath = f"//input[contains(@class, 'ddinput input_col3d')]"
while True:
    if(wait_for_element_presence(driver, By.XPATH, xpath)): # Wait for timesheet to load to avoid user interaction
        print("Timesheet loaded successfully!")
        break
    else:
        print("Waiting for timesheet to load...")
        
date_str = datetime.now().date().isoformat()

# We should eventually run out of items in time_list now, and we'll keep checking until that happens
while any(time_list):
    for entry in time_list:
        if entry.add_time_entry(driver) and not check_for_error(driver):
            entry.saveEntry(True, attorney) # Save successful entry to file for logging
            time_list.pop(0) # remove successful element so we don't add twice
        else:
            # DONE: Add function to loop through data list and remove matching case number entries and add them to the failure list all at once
            remove_failed_entries(time_list, entry.caseNum, attorney)
            click_toolbar_button_delete(driver) # Delete the failed entry row
            break # restart loop through time_list with all missing case time entries removed

log_result(f"{date_str}_TimeEntry_Log.txt", "All cases processed successfully! Please review success and failure time entries.")
print("All cases processed successfully! Please review success and failure time entries.")
driver.close()
check_for_error(driver)
