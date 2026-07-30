from typing import List, Optional
from pydantic import BaseModel

class PostContent(BaseModel):
    """Schema for SVG Graphic Generator output and callback"""
    svg_code: str
    media_name: str

class GeneratedPostSummary(BaseModel):
    """Schema for the Content Generator orchestrator summary output"""
    name: Optional[str] = "Campaign Post Set"
    platform: Optional[str] = "twitter"
    summary: Optional[str] = "Content generated successfully"
    svg_code: Optional[str] = None
    media_name: Optional[str] = None

class SinglePost(BaseModel):
    """Individual generated post representation"""
    name: str
    platform: str
    post_text: str
    has_media: bool
    media_name: Optional[str] = None

class PostCollection(BaseModel):
    """Structured collection of posts for a campaign"""
    platform: str
    posts: List[SinglePost]
