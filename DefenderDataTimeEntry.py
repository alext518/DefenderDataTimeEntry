from pandas import pandas as pd
from selenium import webdriver as wd
from datetime import datetime
from FileManagement import logResult, getTimeDataPath, read_time_data
from Task import Task
from TimeEntry import TimeEntry as te
from WebInteraction import login, click_toolbar_button_timesheet_clear, click_toolbar_button_delete, check_for_error
from Attorney import Attorney

def setup_webdriver(attorney):
    """Sets up the Selenium WebDriver."""
    options = wd.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_experimental_option("detach", True)  # Keeps browser open after script ends
    driver = wd.Chrome(options=options)
    driver.get('https://east.justiceworks.com/dd7/web/start/31053')  # Replace with actual URL
    login(driver, attorney) # Call the login function after opening page
    return driver

# Begin main script exectution
name = input("Enter attorney name (Shelby or Dane): ").strip()
if name not in ["Shelby", "Dane"]:
    print("Invalid attorney name. Please enter 'Shelby' or 'Dane'.")
    exit(1)
else:
    attorney = Attorney(name)

driver = setup_webdriver(attorney) # Start webdriver

print("Reading time sheet data from file...")
time_data = read_time_data(getTimeDataPath(attorney.name))

d = pd.DataFrame(time_data)

time_list = [] # List to hold TimeEntry objects
for index, row in d.iterrows():
    date = row['Date']
    activity = row['Activity']
    duration = row['Duration']
    case_number = row['Case Number']
    task = Task(activity) # create task object
    task.convert_task_code_entries() # Convert codes to time sheet values
    time_list.append(te(date, task, duration, case_number, f"{date},{activity},{duration},{case_number}"))
print("All codes mapped!")

input("Press Enter to continue when timesheet is loaded...")
click_toolbar_button_timesheet_clear(driver) # Clear timesheet to one row after it loads
date_str = datetime.now().date().isoformat()
for entry in time_list:
    if entry.add_time_entry(driver) and not check_for_error(driver):
        logResult(f"Entry_Success_{date_str}", f"{datetime.now()}: Added time entry for {entry.date}, {entry.Task.taskCode}, {entry.duration}, {entry.caseNum}\n")
        entry.saveEntry(f"{attorney}\\Successful_Entries_{date_str}.csv") # Save successful entry to file for processing later
    else:
        logResult(f"Entry_Failure_{date_str}", f"{datetime.now()}: Time entry failed to be added for {entry.date}, {entry.Task.taskCode}, {entry.duration}, {entry.caseNum}\n")
        entry.saveEntry(f"{attorney}\\Failed_Entries_{date_str}.csv") # Save failed entry to file for processing later
        click_toolbar_button_delete(driver) # Delete the failed entry row
