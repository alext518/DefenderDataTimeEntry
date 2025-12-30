import pandas as pd
def log_result(log_name, log_entry):
    open(log_name, "a", encoding="utf-8").write(log_entry)

def get_time_data_path(attorney):
    return attorney + '/current_time_report_final.csv'

def read_time_data(file_path, logger = None, file_reader = pd.read_csv):
    """Reads time data from a CSV file."""
    try:
        return file_reader(file_path)
    except Exception as e:
        logger.error(f"Failed to read time data: {e}")