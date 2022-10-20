from pydantic import BaseModel

class AddPostResponse(BaseModel):
    post_id: int
    detail: str

class PostResponse(BaseModel):
    id: int
    text: str
    user_id: int
