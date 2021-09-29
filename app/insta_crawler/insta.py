from json.decoder import JSONDecodeError
import logging
from random import randint
from time import sleep
from typing import Dict, List, Optional, Type, Union

from fake_useragent import UserAgent
import requests

from .authentication import Auth
from .exceptions import (BlockedByInstagramError, NotFoundError,
                         PrivateProfileError)
from .models import Highlight, IGTV, Post, Storie, User
from .utils import how_sleep


class InstaCrawler:
    """
    Used to collect information and data from Instagram profile.
    """
    BASE_URL: str = "https://www.instagram.com/"
    STORIES_URL: str = "https://i.instagram.com/"
    GRAPHQL_QUERY: str = "graphql/query/"
    STORIES_QUERY: str = "api/v1/feed/reels_media/"

    all_posts_query_hash: str = "003056d32c2554def87228bc3fd9668a"
    user_reels_query_hash: str = "d4d88dc1500312af6f937f7b804c68c3"
    followers_query_hash: str = "c76146de99bb02f6415203be841dd25a"
    followed_by_user_query_hash: str = "d04b0a864b4b54837c0d870b0e77e076"
    user_igtvs_query_hash: str = "bc78b344a68ed16dd5d7f264681c4c76"
    cookie_user_timeline_hash: str = "b1245d9d251dff47d91080fbdd6b274a"
    x_ig_app_id: str = "936619743392459"

    cookie: Dict

    def __init__(self, login: str, password: str, authenticator: Type[Auth]):
        self.login = login
        self.password = password
        self.cookie = self._auth_and_get_cookie(authenticator)

        logging.basicConfig(filename="insta_crawler.log",
                            format="%(asctime)s: %(name)s: %(levelname)s: %(funcName)s: %(lineno)s: %(message)s",
                            level=logging.INFO)
        logging.info(f"Class initialised with cookie: '{self.cookie}'")

    def _make_request(self, url: str,
                      params: Dict[str, str],
                      headers: Optional[Dict[str, Union[str, int]]] = None) -> Dict:
        """
        Makes a request to the given url with the parameters,
        headers and cookies.

        :param url: URL to send.
        :param params: URL parameters to append to the URL.
        :param headers: dictionary of headers to send.
        """
        data = requests.get(url=url,
                            params=params,
                            cookies=self.cookie,
                            headers=headers)
        try:
            data_dict = data.json()
            if len(data_dict) == 0:  # This part for the single_post function
                # url should be without any parameters
                original_url = data.url.split("?")[0]
                data = requests.get(url=original_url,
                                    cookies=self.cookie)
                # when the profile is private and the cookie user
                # is not following the profile, the request url
                # changes to the user profile url, but this is
                # not a redirect, so we have to check if
                # the original url and the redirected url are equal
                if original_url == data.url:
                    # if they are equal but the response is empty
                    logging.error("NotFoundError")
                    raise NotFoundError()
                else:
                    raise PrivateProfileError()
        except JSONDecodeError as e:
            logging.error(f"BlockedByInstagramError. Cause: {repr(e)}")
            raise BlockedByInstagramError()
        else:
            return data_dict

    def _auth_and_get_cookie(self, authenticator: Type[Auth]) -> Dict:
        auth = authenticator(login=self.login, password=self.password)
        cookies = auth.get_cookies()

        return cookies

    def get_cookie_user(self) -> User:
        """
        Gives an information about cookie-user.
        """
        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        params = {
            "query_hash": self.cookie_user_timeline_hash,
        }
        cookie_user_username = self._make_request(query_url, params=params)
        if cookie_user_username is not None:
            cookie_user_username = cookie_user_username["data"]["user"]["username"]

            user_url = f"{self.BASE_URL}{cookie_user_username}/"
            cookie_user_info = self.get_user_info(url=user_url)

            logging.info(msg=f"cookie user: {user_url}")

        return cookie_user_info

    def get_user_info(self, url: str) -> User:
        """
        Gives information about the user by link to his profile.

        :param url: link to a profile
        (https://www.instagram.com/username/).
        """

        params = {"__a": "1"}
        user_data = self._make_request(url, params)["graphql"]
        user_data = user_data.get("user") or user_data.get("shortcode_media")["owner"]

        logging.info(msg=f"user info requested: {url}")

        if user_data.get("edge_owner_to_timeline_media"):
            posts_count = user_data["edge_owner_to_timeline_media"]["count"]

            last_twelve_posts = []
            for post in user_data["edge_owner_to_timeline_media"]["edges"]:
                post = post["node"]
                last_twelve_posts.append(
                    self.forming_post_data(post_data=post))

        user = User(
            bio=user_data.get("biography"),
            external_url=user_data.get("external_url"),
            followed_by=user_data["edge_followed_by"]["count"],
            follow=user_data["edge_follow"]["count"],
            full_name=user_data.get("full_name"),
            highlight_reel_count=user_data.get("highlight_reel_count"),
            user_id=user_data.get("id"),
            is_busuness_account=user_data.get("is_business_account"),
            business_category_name=user_data.get("business_category_name"),
            category_name=user_data.get("category_name"),
            is_private=user_data.get("is_private"),
            username=user_data.get("username"),
            igtv_count=user_data["edge_felix_video_timeline"]["count"],
            posts_count=posts_count or 0,
            last_twelve_posts=last_twelve_posts or [],
            profile_pic_hd=user_data.get("profile_pic_url_hd"),
            followed_by_viewer=user_data.get("followed_by_viewer"),
            user_url=url,
        )
        if self._can_parse_profile(user):
            raise PrivateProfileError()

        return user

    def get_single_post(self, url: str) -> Post:
        """
        Gives information about the post by link to it.

        :param url: link to the post or igtv
        (https://www.instagram.com/[p OR tv]/shortcode/).
        """
        logging.info(msg=f"single post: {url}")

        params = {"__a": "1"}
        post_data = self._make_request(
            url, params)["graphql"]["shortcode_media"]

        return self.forming_post_data(post_data=post_data)

    def get_highlights(self, url: str) -> List[Highlight]:
        """
        Collects all content and information about highlights
        on the user page.

        :param url: link to a profile
        (https://www.instagram.com/username/).
        """

        user_data = self.get_user_info(url=url)

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        params = {
            "query_hash": self.user_reels_query_hash,
            "user_id": str(user_data.user_id),
            "include_chaining": "true",
            "include_reel": "true",
            "include_suggested_users": "false",
            "include_logged_out_extras": "false",
            "include_highlight_reels": "true",
            "include_live_status": "true",
        }
        highlights_data = self._make_request(
            query_url,
            params=params,
        )["data"]["user"]
        logging.info(f"User {url} highlights.")

        highlights = []
        for hl in highlights_data["edge_highlight_reels"]["edges"]:
            highlight_content = self.get_stories(reel_id=f'highlight:{hl["node"]["id"]}')
            post_content = [
                post.post_content[0]
                for post in highlight_content
            ]
            highlights.append(
                Highlight(
                    owner_link=url,
                    owner_username=highlights_data["reel"]["owner"]["username"],
                    highlight_id=hl["node"]["id"],
                    post_content=post_content,
                    post_content_len=len(post_content),
                    post_link=f'{self.BASE_URL}stories/highlights/{hl["node"]["id"]}',
                    title=hl["node"]["title"],
                ),
            )

        logging.info(f"Highlights count: {len(highlights)}")
        return highlights

    def get_posts(self, url: str) -> List[Post]:
        """
        Collects all content and information about regular posts
        on the user page.

        :param url: link to a profile
        (https://www.instagram.com/username/).
        """

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        posts = []
        after = ""

        user_data = self.get_user_info(url=url)

        while True:
            params = {
                "query_hash": self.all_posts_query_hash,
                "id": user_data.user_id,
                "first": 50,
                "after": after if after else "",
            }

            sleep(randint(0, 2))
            posts_data = self._make_request(
                url=query_url,
                params=params,
            )["data"]["user"]["edge_owner_to_timeline_media"]

            for post in posts_data["edges"]:
                post = post["node"]
                description = None
                if post["edge_media_to_caption"]["edges"]:
                    post["edge_media_to_caption"]["edges"][0]["node"]["text"]

                if post.get("edge_sidecar_to_children"):
                    post_links = post["edge_sidecar_to_children"]["edges"]
                    post_content = [
                        (
                            post["node"].get("video_url")
                            or
                            post["node"].get("display_url")
                        )
                        for post in post_links
                    ]
                else:
                    post_content = [
                        (post.get("video_url") or post.get("display_url"))]

                posts.append(
                    Post(
                        description=description,
                        likes=post["edge_media_preview_like"]["count"],
                        comments=post["edge_media_to_comment"]["count"],
                        owner_link=f'{self.BASE_URL}{post["owner"]["username"]}',
                        owner_username=post["owner"]["username"],
                        post_content=post_content,
                        post_content_len=len(post_content),
                        posted_at=post["taken_at_timestamp"],
                        shortcode=post["shortcode"],
                        post_link=f'{self.BASE_URL}p/{post["shortcode"]}/',
                    ),
                )
            if posts_data["page_info"]["has_next_page"]:
                after = posts_data["page_info"]["end_cursor"]
            else:
                logging.info(
                    msg=f"User {url} posts. Count: {len(posts)}")
                break

        return posts

    def get_all_igtv(self, url: str) -> List[IGTV]:
        """
        Collects all content and information about igtvs
        on the user page.

        :param url: link to a profile
        (https://www.instagram.com/username/).
        """

        user_data = self.get_user_info(url=url)

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        igtvs = []
        after = ""

        logging.info(msg=f"User {url} igtvs.")
        while True:
            params = {
                "query_hash": self.user_igtvs_query_hash,
                "id": str(user_data.user_id),
                "first": "50",
                "after": after if after else "",
            }

            igtv_data = self._make_request(url=query_url, params=params)[
                "data"]["user"]["edge_felix_video_timeline"]

            for igtv in igtv_data["edges"]:
                igtv = igtv["node"]

                post_link = f'{self.BASE_URL}tv/{igtv["shortcode"]}'
                post_info = self.get_single_post(url=post_link)

                igtvs.append(
                    IGTV(
                        description=igtv["edge_media_to_caption"]["edges"][0]["node"]["text"],
                        likes=igtv["edge_liked_by"]["count"],
                        comments=post_info.comments,
                        owner_link=post_info.owner_link,
                        owner_username=post_info.owner_username,
                        post_content=post_info.post_content,
                        post_content_len=1,
                        posted_at=igtv["edge_liked_by"]["count"],
                        shortcode=igtv["shortcode"],
                        post_link=post_link,
                        title=igtv["title"],
                    ),
                )
            if igtv_data["page_info"]["has_next_page"]:
                after = igtv_data["page_info"]["end_cursor"]
            else:
                logging.info(f"IGTVs count: {len(igtvs)}")
                break
        return igtvs

    def get_stories(self, url: str = "", reel_id: str = "") -> List[Storie]:
        """
        Collects all content and information about active stories
        on the user page.

        :param url: link to a profile
        (https://www.instagram.com/username/).
        """

        if url:
            user_data = self.get_user_info(url=url)

        query_url = f"{self.STORIES_URL}{self.STORIES_QUERY}"
        params = {
            "reel_ids": reel_id if reel_id else str(user_data.user_id),
        }
        headers = {
            "authority": "i.instagram.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "dnt": "1",
            "x-ig-app-id": self.x_ig_app_id,
            "origin": self.BASE_URL,
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "accept": "*/*",
            "referer": self.BASE_URL,
            "user-agent": UserAgent().chrome,
        }

        stories_data = self._make_request(
            query_url, params=params, headers=headers)["reels_media"]
        stories: List = []
        if stories_data:
            stories_data = stories_data[0]
        else:
            return stories

        for storie in stories_data["items"]:
            if storie["media_type"] == 1:
                post_content = [storie["image_versions2"]
                                ["candidates"][0]["url"]]
            else:
                post_content = [storie["video_versions"][0]["url"]]

            username = stories_data["user"]["username"]
            stories.append(
                Storie(
                    owner_link=f"{self.BASE_URL}{username}",
                    owner_username=username,
                    post_content=post_content,
                    post_content_len=1,
                    post_link=f'{self.BASE_URL}stories/{username}/{storie["id"]}',
                    posted_at=storie["taken_at"],
                    shortcode=storie["id"],
                ),
            )
        logging.info(msg=f"User {url} stories. Count: {len(stories)}")

        return stories

    def get_followers(self, url: str) -> Dict:
        """
        Collects all information about user followers.

        :param url: link to a profile
        (https://www.instagram.com/username/).
        """

        user_data = self.get_user_info(url=url)

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        after = ""

        user_followers = {
            "count": user_data.followed_by,
            "usernames": list(),
            "followers": list(),
        }
        while True:
            params = {
                "query_hash": self.followers_query_hash,
                "id": user_data.user_id,
                "include_reel": False,
                "fetch_mutual": False,
                "first": 50,
                "after": after or "",
            }
            data = self._make_request(url=query_url, params=params)["data"]["user"]["edge_followed_by"]
            self._extract_usernames(users=data["edges"], result=user_followers["usernames"])
            after = self._has_next_page(data)
            if after is None:
                break

        self._extract_users_by_usernames(usernames=user_followers["usernames"], result=user_followers["followers"])
        logging.info(msg=f'User {url} followers. Count: {len(user_followers["followers"])}')

        return user_followers

    # almost 17 minutes for 800 items
    def get_followed_by_user(self, url: str) -> Dict:
        """
        Collects all information about users followed
        by requested profile owner.

        :param url: link to a profile
        (https://www.instagram.com/username/).
        """

        user_data = self.get_user_info(url=url)

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        after = ""

        user_follow = {
            "count": user_data.follow,
            "usernames": list(),
            "followed": list(),
        }
        while True:
            params = {
                "query_hash": self.followed_by_user_query_hash,
                "id": user_data.user_id,
                "first": 50,
                "after": after if after else "",
            }

            data = self._make_request(url=query_url, params=params)["data"]["user"]["edge_follow"]
            self._extract_usernames(users=data["edges"], result=user_follow["usernames"])

            after = self._has_next_page(data)
            if after is None:
                break

        self._extract_users_by_usernames(usernames=user_follow["usernames"], result=user_follow["followed"])
        logging.info(msg=f'Followed by user {url}. Count: {len(user_follow["followed"])}')

        return user_follow

    def _extract_usernames(self, users: List, result: List[str]) -> None:
        for user in users:
            result.append(user["node"]["username"])

    def _extract_users_by_usernames(self, usernames: List[str], result: List[User]) -> None:
        for username in usernames:
            user_url = f"{self.BASE_URL}{username}/"
            user_info = self.get_user_info(url=user_url)

            result.append(user_info)

            how_sleep(data_len=len(result))

    def _has_next_page(self, data: Dict) -> Optional[str]:
        if data["page_info"]["has_next_page"]:
            return data["page_info"]["end_cursor"]
        else:
            return None

    def _collect_post_content(self, post: Dict) -> List:
        if post.get("edge_sidecar_to_children"):
            post_content = [
                (
                    elem["node"].get("video_url")
                    or
                    elem["node"].get("display_url")
                )
                for elem in post["edge_sidecar_to_children"]["edges"]
            ]
        elif post.get("product_type") == "igtv":
            post_content = [post.get("video_url")]
        else:
            post_content = [post.get(
                "video_url") or post.get("display_url")]

        return post_content

    def _can_parse_profile(self, user_data: User) -> bool:
        """
        Check can or cannot parse a user's profile,
        depending on account privacy and is the viewer
        followed to that or not.

        :param user-data: dictionary with information
        about user account.

        :return bool: True if profile is private and
        cookie user does not follow it else False.
        """

        is_private = user_data.is_private
        followed_by_viewer = user_data.followed_by_viewer

        return is_private and not followed_by_viewer

    def forming_post_data(self, post_data: Dict) -> Post:
        post_content = self._collect_post_content(post=post_data)
        product_type = "tv/" if post_data.get("product_type") == "igtv" else "p/"

        if post_data["edge_media_to_caption"]["edges"]:
            description = post_data["edge_media_to_caption"]["edges"][0]["node"]["text"]
        else:
            description = None

        comments = post_data.get("edge_media_preview_comment") or post_data.get(
            "edge_media_to_comment")

        return Post(
            description=description,
            likes=post_data["edge_media_preview_like"]["count"],
            comments=comments["count"],
            owner_link=f"{self.BASE_URL}{post_data['owner']['username']}/",
            owner_username=post_data["owner"]["username"],
            post_content=post_content,
            post_content_len=len(post_content),
            posted_at=post_data["taken_at_timestamp"],
            shortcode=post_data["shortcode"],
            post_link=f"{self.BASE_URL}{product_type}{post_data['shortcode']}/",

        )
