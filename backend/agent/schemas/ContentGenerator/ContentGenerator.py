from pydantic import BaseModel




class PostMedia(BaseModel):

    name: str
    content: str
