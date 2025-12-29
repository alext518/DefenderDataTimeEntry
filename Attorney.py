class Attorney:
    def __init__(self, name):
        self.name = name
        self.username = ""
        self.password = ""
        self.email = ""
        self.user_id = ""
        self.getCredentials()

    def getCredentials(self):
        with open(self.name + '\\Account.acc', "r", encoding="utf-8") as account_file:
            for line in account_file:
                line = line.strip()
                if line.startswith("username="):
                    self.username = line.split('=', 1)[1]
                elif line.startswith("password="):
                    self.password = line.split('=', 1)[1]
                elif line.startswith("email="):
                    self.email = line.split('=', 1)[1]
                elif line.startswith("user_id="):
                    self.user_id = line.split('=', 1)[1]
        print(f"Successfully retrieved {self.name}'s credentials!")