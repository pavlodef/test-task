from pydantic import BaseModel, EmailStr

class UserRegisterModel(BaseModel):
  email: EmailStr
  password: str

class UserLoginModel(UserRegisterModel):
  pass

