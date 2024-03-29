from dataclasses import dataclass
import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(basedir, "..", ".env"))

login = os.environ.get("LOGIN2")
password = os.environ.get("PASSWORD2")

# these profiles must either be public,
# or the account whose cookies you are using must be following them.
SUCCESS_TEST_LINKS = [
    os.environ.get("SUCCESS_TEST_LINK_01"),
    os.environ.get("SUCCESS_TEST_LINK_02"),
]

SUCCESS_SINGLE_POST_LINKS = [
    os.environ.get("SUCCESS_SINGLE_POST_LINK_01"),
    os.environ.get("SUCCESS_SINGLE_POST_LINK_02"),
    os.environ.get("SUCCESS_SINGLE_POST_LINK_03"),
]

# getting the "followers" list or "followed by user" list
# may be very time consuming. For test cases choose some account
# with a small numbers of "followers" and "following"
OPEN_PROFILE_FOLLOWERS_TEST_LINK = [os.environ.get("OPEN_PROFILE_FOLLOWERS_TEST_LINK")]
PRIVATE_PROFILE_FOLLOWERS_TEST_LINK = [os.environ.get("PRIVATE_PROFILE_FOLLOWERS_TEST_LINK")]

# private and not followed by the account whose cookie you are using
FAILED_TEST_LINK = [os.environ.get("FAILED_TEST_LINK")]


PRIVATE_PROFILE_SINGlE_POST_LINKS = [
    os.environ.get("PRIVATE_PROFILE_SINGlE_POST_LINKS_01"),
    os.environ.get("PRIVATE_PROFILE_SINGlE_POST_LINKS_02"),
]

NOT_FOUND_ERROR_LINKS = [
    os.environ.get("NOT_FOUND_SINGLE_POST_LINK"),
    os.environ.get("NOT_FOUND_SINGLE_USER_LINK"),
]


@dataclass
class InstaConstants:
    base_url: str = "https://www.instagram.com/"
    stories_url: str = "https://i.instagram.com/"
    graphql_query: str = "graphql/query/"
    stories_query: str = "api/v1/feed/reels_media/"
    all_posts_query_hash: str = "003056d32c2554def87228bc3fd9668a"
    user_reels_query_hash: str = "d4d88dc1500312af6f937f7b804c68c3"
    user_igtvs_query_hash: str = "bc78b344a68ed16dd5d7f264681c4c76"
    cookie_user_timeline_hash: str = "b1245d9d251dff47d91080fbdd6b274a"
    followers_query_hash: str = "c76146de99bb02f6415203be841dd25a"
    followed_by_user_query_hash: str = "d04b0a864b4b54837c0d870b0e77e076"
    x_ig_app_id: str = "936619743392459"


if __name__ == "__main__":
    pass
