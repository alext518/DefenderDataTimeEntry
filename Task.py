class Task:
    def __init__(self, taskCode):
        self.taskCode = taskCode
        self.taskType = ""
        self.convert_task_code_entries()

    def convert_task_code_entries(self):
        taskCode = self.taskCode
        taskType = self.taskType
        # Code list format will be this: "Task Description string,tcodes index pos,ttypes index pos"
        mapped_codes = []
        taskCodes = ["In Court", "In Court Waiting", "Out Of Court"]
        taskTypes = ["Case Development", "Discovery Review", "Hearing/Trial Prep", "Interview In Custody", "Interview Out of Custody", "Negotiations", "Other", "Research/Motions","Travel"]
        codes_filename = "task_codes.txt"
        try:
            open(codes_filename, "x", encoding="utf-8") # If file doesn't exist create one
        except FileExistsError: # If it already exits, read the contents
            with open(codes_filename, "r", encoding="utf-8") as mapped_codes_file:
                mapped_codes.extend([line.strip() for line in mapped_codes_file])
        # Try to see if we have code mapped already
        code_found = False
        for code in mapped_codes:
            code_found = False
            curr_code_desc: str = code.split(',')[0]
            curr_code_code: int = code.split(',')[1]
            curr_code_type: int = code.split(',')[2]
            if curr_code_desc.upper() != taskCode.upper():
                continue
            else:
                code_found = True
                self.taskCode = taskCodes[int(curr_code_code)]
                self.taskType = taskTypes[int(curr_code_type)] if taskTypes[int(curr_code_type)] != '-1' else ""
                break;

        if code_found == False: # Map it and append to code file
            print(f"\nTask code '{taskCode}' not found in existing codes. Please map it.")
            print("Available Task Codes:")
            for idx, code in enumerate(taskCodes):
                print(f"{idx}: {code}")
            code_index = input("Enter the index number for the appropriate Task Code: ")
            if code_index == '2': # If out of court, we need to map a task type as well
                print("Available Task Types:")
                for idx, taskType in enumerate(taskTypes):
                    print(f"{idx}: {taskType}")
                type_index = input("Enter the index number for the appropriate Task Type: ")
                self.taskType = taskTypes[int(type_index)]
            else:
                type_index = -1 # Indicate we don't need type for things in court

            self.taskCode = taskCodes[int(code_index)]
            with open(codes_filename, "a", encoding="utf-8") as mapped_codes_file:
                mapped_codes_file.write(f"{taskCode},{code_index},{type_index}\n")
                print(f"Added new task code mapping: {taskCode},{code_index},{type_index}")