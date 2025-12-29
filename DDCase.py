# May need to come up with a search algorithm for charges/charge levels: https://www.ncleg.gov/Search/GeneralStatutes
class DDCase():
    def __init__(self, case_number, case_type, case_sub_type, appointed_date, in_custody, charge, attorney):
        self.case_number = case_number
        self.case_type = case_type
        self.case_sub_type = case_sub_type
        self.appointed_date = appointed_date
        self.in_custody = in_custody
        self.charge = charge
        self.attorney = attorney
