from calendar import month_name

import urllib
from MyCaseAPIAccess import MyCaseAPIHelper

def dd_date_format(date):
    return f"{date[5:7]}/{date[8:10]}/{date[0:4]}"

class MyCaseTimeEntry(MyCaseAPIHelper):
    def __init__(self, client_id, client_secret, attorney, start_date, end_date, update_after_date):
        super().__init__(client_id, client_secret, attorney)
        self.activities_data: dict = {} # Dictionary for activity data
        self.month_number = int(start_date[5:7])
        self.month_name = ""
        match self.month_number:
            case 1:
                self.month_name = "January"
            case 2:
                self.month_name = "February"
            case 3:
                self.month_name = "March"
            case 4:
                self.month_name = "April"
            case 5:
                self.month_name = "May"
            case 6:
                self.month_name = "June"
            case 7:
                self.month_name = "July"
            case 8:
                self.month_name = "August"
            case 9:
                self.month_name = "September"
            case 10:
                self.month_name = "October"
            case 11:
                self.month_name = "November"
            case 12:
                self.month_name = "December"
            case _:
                self.month_name = "Invalid date"
        self.update_after_date = update_after_date
        # --- Build the API Url for activities ---
        # Fields included in the return of the API in a dict:
        # 0. id - integer

        # 1. activity_name - string
        # The activity name associated with this time entry.

        # 2. description - string
        
        # 3. billable - boolean
        # Whether or not this time entry is billable.

        # 4. entry_date - string
        # The entry date of this time entry in ISO 8601 date format.

        # 5. rate - string
        # The rate in dollars associated with this time entry.

        # 6. hours - number
        # The duration in hours associated with this time entry.

        # 7. flat_fee - boolean
        # Whether or not this time entry is a flat fee.

        # 8. case - object
        #   0. id - integer

        # 9. staff - object
        #   0. id - integer

        # 10. invoices - array[object]
        #   0. id - integer

        # 11. custom_field_values - array[CustomFieldValueResponse]
        #   0. custom_field - object
        #   The custom field that this value is associated with. By default, this object will only be returned with an id field. To specify more fields to be returned, please see the field query parameters.

        #   1. value - string or number or boolean
        #   The value of this custom field.

        #   2. created_at - string
        #   An ISO 8601 timestamp of when the Custom Field value was created.

        #   3. updated_at - string
        #   An ISO 8601 timestamp of when the Custom Field value was last updated.

        # 12. created_at - string
        
        # 13. updated_at - string

        MYCASE_TIME_ENTRY_URL = (
            f"{self.MYCASE_API_URL}/time_entries?"
            f"filter[updated_after]={self.update_after_date}T00:00:00Z{urllib.parse.quote_plus(',')}"
            f"page_size={self.MAX_PAGE_SIZE}"
        )

        # --- Make the API Request ---
        response = self.make_authenticated_mycase_request(
            url = MYCASE_TIME_ENTRY_URL,
            method = 'GET'
        )

        # Check that we were successful
        if response.status_code == 200:
            self.time_entry_data = response.json()
            print(f"Found {len(self.time_entry_data)} activities for {self.month_name}")
        else:
            print(f"Failed to fetch activities. Status code: {response.status_code}")
            print(f"Response body: {response.text}")

    def print_activity(self, time_entry: dict):
        dd_date = dd_date_format(time_entry['entry_date'])
        print(f" - Date: {dd_date}, Activity: {time_entry['activity_name']}, Duration: {time_entry['hours']:.2f}, Description: {time_entry['description']}, User: ID: {time_entry['staff']['id']}")
