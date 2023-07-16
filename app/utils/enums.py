from enum import StrEnum


class Queues:
    class User(StrEnum):
        CREATE = "user.create"
        FIND_BY_ID = "user.find.id"
        FIND = "user.find"
    
    class Auth(StrEnum):
        CREATE = "auth.password.initial"
        CHANGE_PASSWORD = "auth.password.change"
        LOGIN = "auth.login"
        VERIFY = "auth.verify"

    class Session(StrEnum):
        EXISTS = "auth.session.exists"
        USER = "auth.session.get-user"

    EMAIL = "email"

class EmailTypes(StrEnum):
    VERIFY = "sign_up"