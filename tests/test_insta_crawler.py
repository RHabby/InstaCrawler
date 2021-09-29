from app.insta_crawler import insta as i
from app.insta_crawler.authentication import InstaAuth
from app.insta_crawler.exceptions import PrivateProfileError
from app.insta_crawler.models import Highlight, IGTV, Post, Storie, User
import pytest
import tests.tests_config as tc


@pytest.fixture(scope="module")
def insta() -> i.InstaCrawler:
    insta = i.InstaCrawler(login=tc.login,
                           password=tc.password,
                           authenticator=InstaAuth)
    return insta


@pytest.mark.success
def test_insta_consts(insta):
    assert isinstance(insta.cookie, dict)
    assert insta.BASE_URL == tc.InstaConstants.base_url
    assert insta.STORIES_URL == tc.InstaConstants.stories_url
    assert insta.GRAPHQL_QUERY == tc.InstaConstants.graphql_query
    assert insta.STORIES_QUERY == tc.InstaConstants.stories_query
    assert insta.all_posts_query_hash == tc.InstaConstants.all_posts_query_hash
    assert insta.user_reels_query_hash == tc.InstaConstants.user_reels_query_hash
    assert insta.user_igtvs_query_hash == tc.InstaConstants.user_igtvs_query_hash
    assert insta.cookie_user_timeline_hash == tc.InstaConstants.cookie_user_timeline_hash
    assert insta.followers_query_hash == tc.InstaConstants.followers_query_hash
    assert insta.followed_by_user_query_hash == tc.InstaConstants.followed_by_user_query_hash
    assert insta.x_ig_app_id == tc.InstaConstants.x_ig_app_id


@pytest.mark.success
def test_get_cookie_user(insta):
    cookie_user = insta.get_cookie_user()
    assert isinstance(cookie_user, User)
    assert cookie_user.user_url == f"{insta.BASE_URL}{cookie_user.username}/"

    if cookie_user.posts_count <= 12:
        assert len(cookie_user.last_twelve_posts) == int(cookie_user.posts_count)
    else:
        assert len(cookie_user.last_twelve_posts) == 12


@pytest.mark.success
@pytest.mark.parametrize("link", tc.SUCCESS_TEST_LINKS)
def test_get_user_info(insta, link):
    user_info = insta.get_user_info(url=link)

    assert isinstance(user_info, User)
    assert user_info.username in user_info.user_url

    if user_info.posts_count <= 12:
        assert len(user_info.last_twelve_posts) == int(user_info.posts_count)
    else:
        assert len(user_info.last_twelve_posts) == 12


@pytest.mark.success
@pytest.mark.parametrize("link", tc.FAILED_TEST_LINK)
def test_get_user_info_fail(insta, link):
    with pytest.raises(PrivateProfileError):
        insta.get_user_info(link)


@pytest.mark.success
@pytest.mark.parametrize("link", tc.SUCCESS_TEST_LINKS)
def test_get_single_post(insta, link):
    user_info = insta.get_user_info(url=link)
    for post in user_info.last_twelve_posts[:10]:
        url = f"{tc.InstaConstants.base_url}p/{post.shortcode}/"

        single_post = insta.get_single_post(url=post.post_link)

        assert isinstance(single_post, Post)
        assert single_post.post_link == url
        assert single_post.shortcode == url.split("/")[-2]


@pytest.mark.success
@pytest.mark.parametrize("link", tc.SUCCESS_TEST_LINKS)
def test_get_highlights(insta, link):
    highlights = insta.get_highlights(url=link)
    assert isinstance(highlights, list)

    if len(highlights) > 0:
        assert isinstance(highlights[0], Highlight)


@pytest.mark.success
@pytest.mark.parametrize("link", tc.SUCCESS_TEST_LINKS)
def test_get_posts(insta, link):
    user_info = insta.get_user_info(url=link)
    posts = insta.get_posts(url=link)
    assert isinstance(posts, list)
    if len(posts) > 0:
        assert isinstance(posts[0], Post)
    assert len(posts) == user_info.posts_count


@pytest.mark.success
@pytest.mark.parametrize("link", tc.SUCCESS_TEST_LINKS)
def test_get_all_igtv(insta, link):
    user_info = insta.get_user_info(url=link)
    igtv = insta.get_all_igtv(url=link)
    assert isinstance(igtv, list)

    if len(igtv) > 0:
        assert isinstance(igtv[0], IGTV)

    assert len(igtv) == user_info.igtv_count


@pytest.mark.success
@pytest.mark.parametrize("link", tc.SUCCESS_TEST_LINKS)
def test_get_stories(insta, link):
    stories = insta.get_stories(url=link)
    assert isinstance(stories, list)

    if len(stories) > 0:
        assert isinstance(stories[0], Storie)


@pytest.mark.success
@pytest.mark.parametrize("link", tc.SUCCESS_TEST_LINKS)
def test_can_parse_profile_success(insta, link):
    user_info = insta.get_user_info(url=link)
    assert isinstance(insta._can_parse_profile(user_data=user_info), bool)


@pytest.mark.success
@pytest.mark.follow
@pytest.mark.parametrize("link", tc.OPEN_PROFILE_FOLLOWERS_TEST_LINK)
def test_get_followers(insta, link):
    followers = insta.get_followers(url=link)

    assert isinstance(followers, dict)
    assert isinstance(followers["count"], int)
    assert isinstance(followers["usernames"], list)
    assert isinstance(followers["followers"], list)
    assert followers["count"] == len(followers["usernames"])
    # assert len(followers["usernames"]) == len(followers["followers"])


@pytest.mark.success
@pytest.mark.follow
@pytest.mark.parametrize("link", tc.OPEN_PROFILE_FOLLOWERS_TEST_LINK)
def test_get_followed_by_user(insta, link):
    followed = insta.get_followed_by_user(url=link)

    assert isinstance(followed, dict)
    assert isinstance(followed["count"], int)
    assert isinstance(followed["usernames"], list)
    assert isinstance(followed["followed"], list)
    assert followed["count"] == len(followed["usernames"])
    # assert len(followed["usernames"]) == len(followed["followed"])


@pytest.mark.success
@pytest.mark.follow
@pytest.mark.parametrize("link", tc.PRIVATE_PROFILE_FOLLOWERS_TEST_LINK)
def test_private_profile_get_followers(insta, link):
    with pytest.raises(PrivateProfileError):
        insta.get_followers(url=link)


@pytest.mark.success
@pytest.mark.follow
@pytest.mark.parametrize("link", tc.PRIVATE_PROFILE_FOLLOWERS_TEST_LINK)
def test_private_profile_get_followed_by_user(insta, link):
    with pytest.raises(PrivateProfileError):
        insta.get_followed_by_user(url=link)
