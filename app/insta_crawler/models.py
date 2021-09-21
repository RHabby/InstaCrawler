from typing import List, Optional

from pydantic import BaseModel


class Post(BaseModel):
    description: Optional[str] = None
    likes: int
    comments: int
    owner_link: str
    owner_username: str
    post_content: List[str]
    post_content_len: int
    posted_at: int
    shortcode: str
    post_link: str


class IGTV(Post):
    title: str


class Highlight(BaseModel):
    owner_link: str
    owner_username: str
    highlight_id: int
    post_content: List
    post_content_len: int
    post_link: str
    title: str


class Storie(BaseModel):
    owner_link: str
    owner_username: str
    post_content: List[str]
    post_content_len: int
    post_link: str
    posted_at: int
    shortcode: int


class User(BaseModel):
    bio: str
    external_url: Optional[str]
    followed_by: int
    follow: int
    full_name: Optional[str]
    highlight_reel_count: int
    user_id: int
    is_busuness_account: bool
    business_category_name: Optional[str]
    category_name: Optional[str]
    is_private: bool
    username: str
    igtv_count: int
    posts_count: Optional[int]
    last_twelve_posts: Optional[List[Post]]
    profile_pic_hd: str
    followed_by_viewer: bool
    user_url: str
