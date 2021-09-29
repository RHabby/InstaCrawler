from app.insta_crawler import insta as i
from app.insta_crawler.authentication import InstaAuth
from app.insta_crawler.exceptions import NotFoundError, PrivateProfileError
import pytest
import tests.tests_config as tc


@pytest.fixture(scope="module")
def insta_instance() -> i.InstaCrawler:
    insta = i.InstaCrawler(login=tc.login,
                           password=tc.password,
                           authenticator=InstaAuth)
    return insta


@pytest.mark.success
@pytest.mark.parametrize("test_input", tc.SUCCESS_TEST_LINKS)
def test_make_request_success(insta_instance: i.InstaCrawler, test_input: str) -> None:
    params = {
        "__a": "1",
    }
    response = insta_instance._make_request(
        url=test_input,
        params=params,
    )
    assert isinstance(response, dict)


@pytest.mark.success
@pytest.mark.parametrize("test_input", tc.PRIVATE_PROFILE_SINGlE_POST_LINKS)
def test_make_request_raise_private_profile_error(insta_instance: i.InstaCrawler, test_input: str) -> None:
    params = {
        "__a": "1",
    }
    with pytest.raises(PrivateProfileError):
        insta_instance._make_request(
            url=test_input,
            params=params,
        )


@pytest.mark.success
@pytest.mark.parametrize("test_input", tc.NOT_FOUND_ERROR_LINKS)
def test_make_request_raise_not_found_error(insta_instance: i.InstaCrawler, test_input: str) -> None:
    params = {
        "__a": "1",
    }
    with pytest.raises(NotFoundError):
        insta_instance._make_request(
            url=test_input,
            params=params,
        )
