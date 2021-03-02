from app.insta_crawler.exceptions import PrivateProfileError
from typing import Dict, OrderedDict, List

import pytest
from app.insta_crawler import insta as i
import tests.tests_config as tc


# paste your fresh baked cookie into the tests_config file
cookie = tc.COOKIE


@pytest.fixture(scope="module", params=tc.SUCCESS_TEST_LINKS)
def insta_instance(request):
    user_url = str(request.param)
    insta = i.InstaCrawler(cookie=cookie)
    user_info = insta.get_user_info(url=user_url)

    return insta, user_info


@pytest.mark.success
def test_insta_consts(insta_instance):
    assert isinstance(insta_instance[0].cookie, str)
    assert insta_instance[0].BASE_URL == tc.InstaConstants.base_url
    assert insta_instance[0].STORIES_URL == tc.InstaConstants.stories_url
    assert insta_instance[0].GRAPHQL_QUERY == tc.InstaConstants.graphql_query
    assert insta_instance[0].STORIES_QUERY == tc.InstaConstants.stories_query
    assert insta_instance[0].all_posts_query_hash == tc.InstaConstants.all_posts_query_hash
    assert insta_instance[0].user_reels_query_hash == tc.InstaConstants.user_reels_query_hash
    assert insta_instance[0].user_igtvs_query_hash == tc.InstaConstants.user_igtvs_query_hash
    assert insta_instance[0].cookie_user_timeline_hash == tc.InstaConstants.cookie_user_timeline_hash
    assert insta_instance[0].followers_query_hash == tc.InstaConstants.followers_query_hash
    assert insta_instance[0].followed_by_user_query_hash == tc.InstaConstants.followed_by_user_query_hash
    assert insta_instance[0].x_ig_app_id == tc.InstaConstants.x_ig_app_id


@pytest.mark.success
def test_get_cookie_user(insta_instance):
    cookie_user = insta_instance[0].get_cookie_user()
    assert isinstance(cookie_user, dict)
    assert cookie_user["user_url"] == f'{insta_instance[0].BASE_URL}{cookie_user["username"]}/'

    if cookie_user["posts_count"] <= 12:
        assert len(cookie_user["last_twelve_posts"]) == int(
            cookie_user["posts_count"])
    else:
        assert len(cookie_user["last_twelve_posts"]) == 12


@pytest.mark.success
def test_get_user_info(insta_instance):
    user_info = insta_instance[1]
    assert isinstance(user_info, Dict)
    assert user_info["username"] in user_info["user_url"]

    if user_info["posts_count"] <= 12:
        assert len(user_info["last_twelve_posts"]) == int(
            user_info["posts_count"])
    else:
        assert len(user_info["last_twelve_posts"]) == 12


@pytest.mark.success
def test_get_single_post(insta_instance):
    for post in insta_instance[1]["last_twelve_posts"][:5]:
        url = f'{tc.InstaConstants.base_url}p/{post["shortcode"]}/'
        single_post = insta_instance[0].get_single_post(url=url)

        assert isinstance(single_post, Dict)
        assert single_post["shortcode"] == url.split("/")[-2]


@pytest.mark.success
def test_get_highlights(insta_instance):
    user_info = insta_instance[1]
    highlights = insta_instance[0].get_highlights(url=user_info["user_url"])
    assert isinstance(highlights, OrderedDict)
    assert len(highlights) == user_info["highlight_reel_count"]


@pytest.mark.success
def test_get_posts(insta_instance):
    user_info = insta_instance[1]
    posts = insta_instance[0].get_posts(url=user_info["user_url"])
    assert isinstance(posts, OrderedDict)
    assert len(posts) == user_info["posts_count"]


@pytest.mark.success
def test_get_all_igtv(insta_instance):
    user_info = insta_instance[1]
    igtv = insta_instance[0].get_all_igtv(url=user_info["user_url"])
    assert isinstance(igtv, OrderedDict)
    assert len(igtv) == user_info["igtv_count"]


@pytest.mark.success
def test_get_stories(insta_instance):
    user_info = insta_instance[1]
    stories = insta_instance[0].get_stories(url=user_info["user_url"])
    assert isinstance(stories, OrderedDict)


@pytest.mark.success
def test_cookie_to_json(insta_instance):
    assert isinstance(insta_instance[0]._cookie_to_json(), Dict)


@pytest.mark.success
def test_can_parse_profile_success(insta_instance):
    user_info = insta_instance[1]
    assert insta_instance[0]._can_parse_profile(user_data=user_info) is None


@pytest.fixture(scope="function", params=[tc.FOLLOWERS_TEST_LINK])
def insta_follow_part(request):
    user_url = str(request.param)
    insta = i.InstaCrawler(cookie=cookie)
    user_info = insta.get_user_info(url=user_url)

    return insta, user_info


@pytest.mark.success
@pytest.mark.follow
def test_get_followers(insta_follow_part):
    user_info = insta_follow_part[1]
    followers = insta_follow_part[0].get_followers(url=user_info["user_url"])

    assert isinstance(followers["count"], int)
    assert isinstance(followers["followers_usernames"], List)
    assert isinstance(followers["followers"], Dict)
    assert int(user_info["edge_followed_by"]) == followers["count"]
    assert followers["count"] == len(followers["followers_usernames"])
    assert len(followers["followers_usernames"]) == len(followers["followers"])
    assert followers["followers_usernames"] == [*followers["followers"]]


@pytest.mark.success
@pytest.mark.follow
def test_get_followed_by_user(insta_follow_part):
    user_info = insta_follow_part[1]
    followed = insta_follow_part[0].get_followed_by_user(
        url=user_info["user_url"])

    assert isinstance(followed["count"], int)
    assert isinstance(followed["usernames"], List)
    assert isinstance(followed["followed"], Dict)
    assert int(user_info["edge_follow"]) == followed["count"]
    assert followed["count"] == len(followed["usernames"])
    assert len(followed["usernames"]) == len(followed["followed"])
    assert followed["usernames"] == [*followed["followed"]]


@pytest.fixture(scope="function", params=[tc.FAILED_TEST_LINK])
def insta_failure(request):
    user_url = str(request.param)
    insta = i.InstaCrawler(cookie=cookie)
    user_info = insta.get_user_info(url=user_url)

    return insta, user_info


@pytest.mark.failed
def test_get_posts_exception(insta_failure):
    with pytest.raises(PrivateProfileError):
        insta_failure[0].get_posts(url=insta_failure[1]["user_url"])


@pytest.mark.failed
def test_get_stories_exception(insta_failure):
    with pytest.raises(PrivateProfileError):
        insta_failure[0].get_stories(url=insta_failure[1]["user_url"])


@pytest.mark.failed
def test_get_highlights_exception(insta_failure):
    with pytest.raises(PrivateProfileError):
        insta_failure[0].get_highlights(url=insta_failure[1]["user_url"])


@pytest.mark.failed
def test_get_igtv_exception(insta_failure):
    with pytest.raises(PrivateProfileError):
        insta_failure[0].get_all_igtv(url=insta_failure[1]["user_url"])


@pytest.mark.failed
@pytest.mark.xfail(run=True)
def test_get_posts_fail(insta_failure):
    assert insta_failure[0].get_posts(url=insta_failure[1]["user_url"])


@pytest.mark.failed
@pytest.mark.xfail(run=True)
def test_get_stories_fail(insta_failure):
    assert insta_failure[0].get_stories(url=insta_failure[1]["user_url"])


@pytest.mark.failed
@pytest.mark.xfail(run=True)
def test_get_highlights_fail(insta_failure):
    assert insta_failure[0].get_highlights(url=insta_failure[1]["user_url"])


@pytest.mark.failed
@pytest.mark.xfail(run=True)
def test_get_igtv_fail(insta_failure):
    assert insta_failure[0].get_all_igtv(url=insta_failure[1]["user_url"])
