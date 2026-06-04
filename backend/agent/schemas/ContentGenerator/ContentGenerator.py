from pydantic import BaseModel

class PostContent(BaseModel):
    """Schema for SVG Graphic Generator output and callback"""
    svg_code: str
    media_name: str

class BasePost(BaseModel):
    """Schema for the Twitter Content Generator orchestrator summary output"""
    name: str
    platform: str
    summary: str
