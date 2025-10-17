import pandas as pd
def logResult(log_name, log_entry):
    open(log_name, "a", encoding="utf-8").write(log_entry)

def getTimeDataPath(attorney):
    return attorney + '/current_time_report_final.csv'

def read_time_data(file_path):
    """Reads time data from a CSV file."""
    return pd.read_csv(file_path)