from pydantic import BaseModel
from pydantic import field_validator
from backend.dependencies import MAX_SIZE

class PostCreateSchema(BaseModel):
    text: str

    @field_validator('text')
    def validate_text(cls, v):
        if len(v.encode('utf-8')) > MAX_SIZE:
            raise ValueError('Text is too long')
        return v
