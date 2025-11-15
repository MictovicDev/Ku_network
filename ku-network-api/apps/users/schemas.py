from pydantic import field_validator, Field, EmailStr
from apps.common.schemas import BaseSchema, ResponseSchema


class EmailSchema(BaseSchema):
    email: EmailStr = Field(..., examples="johndoe@example.com")
    
    
class RegisterUserSchema(EmailSchema):
    username: str =  Field(..., example="John", max_length=50)
    password: str = Field(..., example="strongpassword", max_length=8)
    password2: str = Field(..., example="strongpassword", min_length=8)
    
    @field_validator("username")
    def no_spaces(cls, username: str):
        if " " in username:
            raise ValueError("No spacing allowed")
        return username