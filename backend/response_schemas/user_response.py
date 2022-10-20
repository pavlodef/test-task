from pydantic import BaseModel

class RegisterTokenResponse(BaseModel):
    access_token: str
    token_type: str

class LoginTokenResponse(RegisterTokenResponse):
    pass