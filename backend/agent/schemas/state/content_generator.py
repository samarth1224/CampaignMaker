from pydantic import BaseModel

class ContentForPlatform(BaseModel):
    twitter: bool = False
    instagram: bool = False
    linkedin: bool = False