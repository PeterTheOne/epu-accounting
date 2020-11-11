class Member:
    def __init__(self, member_id, first_name, last_name):
        self.member_id = member_id
        self.first_name = first_name
        self.last_name = last_name

    def update(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
