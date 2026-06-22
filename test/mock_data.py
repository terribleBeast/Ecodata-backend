from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str


class UserDB:
    def __init__(self):
        self.users = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"},
        ]

    def get_users(self):
        return self.users

    def add_user(self, user):
        self.users.append(user)


user_db = UserDB()
