import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(basedir, "..", ".env"))

login = os.environ.get("LOGIN2")
password = os.environ.get("PASSWORD2")

category_headers_row = ["shortcode", "post_link", "owner_username",
                        "owner_link", "likes", "comments",
                        "description", "title", "posted_at",
                        "post_content", "post_content_len"]

followers_headers_row = ["id", "username", "full_name", "user_url",
                         "bio", "posts_count", "igtv_count",
                         "highlight_reel_count", "edge_followed_by",
                         "edge_follow", "is_private", "followed_by_viewer",
                         "is_business_account", "business_category_name",
                         "category_name", "external_url", "profile_pic_hd",
                         "last_12_posts_shortcodes"]
