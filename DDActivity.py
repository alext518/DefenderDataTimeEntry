class DDActivity():
    def __init__(self, date, case_number, duration, task_code, user, description, sub_task_code = "" ):
        self.date = date
        self.case_number = case_number
        self.duration = duration
        self.task_code = task_code
        self.sub_task_code = sub_task_code
        self.user = user
        self.description = description
