import os

from app.insta_crawler.models import Highlight, IGTV, Post, Storie, User
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(basedir, "..", ".env"))

login = os.environ.get("LOGIN2")
password = os.environ.get("PASSWORD2")

category_headers_row = {
    "posts": list(Post.__fields__.keys()),
    "stories": list(Storie.__fields__.keys()),
    "highlights": list(Highlight.__fields__.keys()),
    "igtv": list(IGTV.__fields__.keys()),
}

followers_headers_row = [
    field
    for field in User.__fields__.keys()
    if field != "last_twelve_posts"
]


if __name__ == "__main__":
    pass
