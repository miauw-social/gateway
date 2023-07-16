from fastapi.responses import JSONResponse

class ProblemJSONResponse(JSONResponse):
    media_type = "application/problem+json"

class BaseProblemJSONException(Exception):
    def __init__(self, **kwargs):
        self.content = kwargs
        self.status_code = kwargs.get("status")



class UserNotFoundException(BaseProblemJSONException):
    pass

class UserAlreadyExsistsException(BaseProblemJSONException):
    pass