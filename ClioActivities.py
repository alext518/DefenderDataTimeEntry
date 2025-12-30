from calendar import month_name

import urllib
from ClioAPIAccess import ClioAPIHelper

def dd_date_format(date):
    return f"{date[5:7]}/{date[8:10]}/{date[0:4]}"

class ClioActivities(ClioAPIHelper):
    def __init__(self, client_id, client_secret, attorney, start_date, end_date, logger = None):
        super().__init__(client_id, client_secret, attorney)
        self.activities_data: dict = {} # Dictionary for activity data
        self.month_number = int(start_date[5:7])
        self.month_name = ""
        self.logger = logger
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
        
        # --- Build the API Url for activities ---
        # Fields needed for DD Time entries:
        # date = date of activity (also the date used when checking between the start/end date)
        # activity_description{'name'} = category on the activity. Equivalent to 'Task Code' in DD. When 'Out Of Court' is selected we will parse the sub-type from this category as well.
        # quantity_in_hours = time spent on activity formatted for hours.
        # matter{'number'} = case number. TODO: work with John on this, numbers don't match up between the two systems
        # note = description written on activity. Can be added to the 'Exaplanation' box in DD.

        CLIO_ACTIVITY_URL = (
            f"{self.api_url}activities?"
            f"start_date={start_date}&"
            f"end_date={end_date}&"
            f"type=TimeEntry&"
            f"user_id={attorney.user_id}&"
            f"order=date(asc)&"
            f"fields=date{urllib.parse.quote_plus(',')}"
            f"activity_description{urllib.parse.quote_plus('{')}"
            f"name{urllib.parse.quote_plus('}')}{urllib.parse.quote_plus(',')}"
            f"quantity_in_hours{urllib.parse.quote_plus(',')}"
            f"matter{urllib.parse.quote_plus('{')}number{urllib.parse.quote_plus('}')}{urllib.parse.quote_plus(',')}"
            f"note{urllib.parse.quote_plus(',')}"
            f"user{urllib.parse.quote_plus('{')}id{urllib.parse.quote_plus(',')}name{urllib.parse.quote_plus('}')}"
        )

        # --- Make the API Request ---
        try:
            response = self.make_authenticated_request(
                url = CLIO_ACTIVITY_URL,
                method = 'GET'
            )
        except requests.RequestException as e:
            self.logger.error("API request failed: %s", e)
        except Exception as e:
            self.logger.exception("Unexpected error occurred")

        # Check that we were successful
        if response.status_code == 200:
            self.activities_data = response.json()
            self.logger.info(f"Found {len(self.activities_data['data'])} activities for {self.month_name}")
        else:
            self.logger.error(f"Failed to fetch activities. Status code: {response.status_code}")
            self.logger.info(f"Response body: {response.text}")

    def print_activity(self, activity: dict):
        category = "N/A"
        if activity['activity_description'] is not None:
            category = activity['activity_description']['name']
        dd_date = dd_date_format(activity['date'])
        self.logger.info(f" - Date: {dd_date}, Activity: {category}, Duration: {activity['quantity_in_hours']:.2f}, Description: {activity['note']}, User: ID: {activity['user']['id']} Name: {activity['user']['name']}")

