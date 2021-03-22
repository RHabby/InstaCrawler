import logging
from collections import OrderedDict
from json.decoder import JSONDecodeError
from typing import Dict, List, Union

from fake_useragent import UserAgent

import requests

from .exceptions import (BlockedByInstagramError,
                         NoCookieError, NotFoundError,
                         PrivateProfileError)
from .utils import how_sleep


class InstaCrawler:
    """
    Used to collect information and data from Instagram profile.

    :param cookie: cookie-string from your browser.
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

    user_info: Union[Dict, None]

    # Should be enough to paste values of 'ig_did' and 'sessionid'
    # example: "ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
    cookie: str

    def __init__(self, cookie: str):
        if not cookie:
            raise NoCookieError
        else:
            self.cookie = cookie
        self.user_info = None

        logging.basicConfig(filename="insta_crawler.log",
                            format="%(asctime)s: %(name)s: %(levelname)s: %(funcName)s: %(lineno)s: %(message)s",
                            level=logging.INFO)
        logging.info(f"Class initialised with cookie: '{self.cookie}'")

    def _make_request(self, url: str,
                      params: Dict[str, str],
                      headers: Union[Dict[str, str], None] = None) -> Dict:
        """
        Makes a request to the given url with the parameters,
        headers and cookies.

        :param url: URL to send.
        :param params: URL parameters to append to the URL.
        :param headers: dictionary of headers to send.
        """
        data = requests.get(
            url=url,
            params=params,
            cookies=self._cookie_to_json(),
            headers=headers,
        )

        try:
            if data.json():
                return data.json()
            elif not data.json():  # This part for the single_post function
                # url should be without any parameters
                original_url = data.url.split("?")[0]
                data = requests.get(
                    url=original_url,
                    cookies=self._cookie_to_json(),
                )
                # when the profile is private and the cookie user
                # is not following the profile, the request url
                # changes to the user profile url, but this is
                # not a redirect, so we have to check if
                # the original url and the redirected url are equal
                if original_url == data.url:
                    # if they are equal but the response is empty
                    logging.error("NotFoundError")
                    raise NotFoundError
                else:
                    user_data = self.get_user_info(url=data.url)
                    self._can_parse_profile(user_data=user_data)
        except JSONDecodeError as e:
            logging.error(f"BlockedByInstagramError. Cause: {repr(e)}")
            raise BlockedByInstagramError

    def get_cookie_user(self) -> Dict:
        """
        Gives an information about cookie-user.
        """
        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        params = {
            "query_hash": self.cookie_user_timeline_hash,
        }
        cookie_user_username = self._make_request(
            query_url, params=params,
        )["data"]["user"]["username"]

        user_url = f"{self.BASE_URL}{cookie_user_username}/"
        cookie_user_info = self.get_user_info(url=user_url)
        self.user_info = None

        logging.info(msg=f"cookie user: {user_url}")

        return cookie_user_info

    def get_user_info(self, url: str) -> Dict:
        """
        Gives information about the user by link to his profile.

        :param url: link to a profile (https://www.instagram.com/username/).
        """

        params = {"__a": 1}

        if not (self.user_info and self.user_info.get("user_url") == url):
            logging.info(msg="request for the user info")

            user_data = self._make_request(url, params)["graphql"]
            user_data = user_data.get("user") or user_data.get(
                "shortcode_media")["owner"]

            if user_data.get("edge_owner_to_timeline_media"):
                posts_count = user_data["edge_owner_to_timeline_media"]["count"]

                last_twelve_posts = []
                for post in user_data["edge_owner_to_timeline_media"]["edges"]:
                    post = post["node"]
                    last_twelve_posts.append(self.forming_post_data(post_data=post))
            else:
                last_twelve_posts = None
                posts_count = None

            self.user_info = {
                "bio": user_data.get("biography"),
                "external_url": user_data.get("external_url"),
                "edge_followed_by": user_data["edge_followed_by"]["count"],
                "edge_follow": user_data["edge_follow"]["count"],
                "full_name": user_data.get("full_name"),
                "highlight_reel_count": user_data.get("highlight_reel_count"),
                "id": user_data.get("id"),
                "is_business_account": user_data.get("is_business_account"),
                "business_category_name": user_data.get("business_category_name"),
                "category_name": user_data.get("category_name"),
                "is_private": user_data.get("is_private"),
                "username": user_data.get("username"),
                "igtv_count": user_data["edge_felix_video_timeline"]["count"],
                "posts_count": posts_count,
                "last_twelve_posts": last_twelve_posts,
                "profile_pic_hd": user_data.get("profile_pic_url_hd"),
                "followed_by_viewer": user_data.get("followed_by_viewer"),
                "user_url": url,
            }
            logging.info(msg=f'user: {self.user_info["user_url"]}')

        return self.user_info

    def get_single_post(self, url: str) -> Dict:
        """
        Gives information about the post by link to it.

        :param url: link to the post or igtv
        (https://www.instagram.com/[p OR tv]/shortcode/).
        """

        params = {"__a": "1"}
        post_data = self._make_request(url, params)["graphql"]["shortcode_media"]

        logging.info(msg=f'single post: {url}')

        return self.forming_post_data(post_data=post_data)

    def get_highlights(self, url: str) -> OrderedDict:
        """
        Collects all content and information about highlights
        on the user page.

        :param url: link to a profile (https://www.instagram.com/username/).
        """

        user_data = self.get_user_info(url=url)
        self._can_parse_profile(user_data=user_data)

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        params = {
            "query_hash": self.user_reels_query_hash,
            "user_id": user_data["id"],
            "include_chaining": "true",
            "include_reel": "true",
            "include_suggested_users": "false",
            "include_logged_out_extras": "false",
            "include_highlight_reels": "true",
            "include_live_status": "true",
        }

        highlights_data = self._make_request(query_url, params=params)[
            "data"]["user"]

        logging.info(f'User {url} highlights.')

        highlights = OrderedDict()
        for hl in highlights_data["edge_highlight_reels"]["edges"]:
            highlights_content = self.get_stories(
                reel_id=f'highlight:{hl["node"]["id"]}',
            )

            username = highlights_data["reel"]["owner"]["username"]

            post_content = [
                post["post_content"][0]
                for post in highlights_content.values()
            ]

            highlights[hl["node"]["id"]] = {
                "comments": None,
                "description": None,
                "likes": None,
                "owner_link": f'{self.BASE_URL}{username}',
                "owner_username": username,
                "id": hl["node"]["id"],
                "post_content": post_content,
                "post_content_len": len(post_content),
                "post_link": f'{self.BASE_URL}stories/highlights/{hl["node"]["id"]}',
                "posted_at": None,
                "title": hl["node"]["title"],
                "shortcode": None,
            }

        logging.info(f'Highlights count: {len(highlights)}')

        return highlights

    def get_posts(self, url: str) -> OrderedDict:
        """
        Collects all content and information about regular posts
        on the user page.

        :param url: link to a profile (https://www.instagram.com/username/).
        """

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        posts = OrderedDict()
        after = ""

        user_data = self.get_user_info(url=url)
        self._can_parse_profile(user_data=user_data)

        while True:
            params = {
                "query_hash": self.all_posts_query_hash,
                "id": user_data["id"],
                "first": "50",
                "after": after if after else None,
            }

            posts_data = self._make_request(
                url=query_url, params=params,
            )["data"]["user"]["edge_owner_to_timeline_media"]

            for post in posts_data["edges"]:
                post = post["node"]
                description = post["edge_media_to_caption"]["edges"][0][
                    "node"]["text"] if post["edge_media_to_caption"]["edges"] else None

                if post.get("edge_sidecar_to_children"):
                    post_links = post["edge_sidecar_to_children"]["edges"]

                    post_content = [
                        (post["node"].get("video_url") or post["node"].get("display_url")) for post in post_links
                    ]
                else:
                    post_content = [
                        (post.get("video_url") or post.get("display_url")),
                    ]

                posts[post["shortcode"]] = {
                    "comments": post["edge_media_to_comment"]["count"],
                    "description": description,
                    "likes": post["edge_media_preview_like"]["count"],
                    "owner_link": f'{self.BASE_URL}{post["owner"]["username"]}',
                    "owner_username": post["owner"]["username"],
                    "post_content": post_content,
                    "post_content_len": len(post_content),
                    "post_link": f'{self.BASE_URL}p/{post["shortcode"]}/',
                    "posted_at": post["taken_at_timestamp"],
                    "title": None,
                    "shortcode": post["shortcode"],
                }

            if posts_data["page_info"]["has_next_page"]:
                after = posts_data["page_info"]["end_cursor"]
            else:
                logging.info(
                    msg=f'User {url} posts. Count: {len(posts)}')
                break

        return posts

    def get_all_igtv(self, url: str) -> OrderedDict:
        """
        Collects all content and information about igtvs
        on the user page.

        :param url: link to a profile (https://www.instagram.com/username/).
        """

        user_data = self.get_user_info(url=url)
        self._can_parse_profile(user_data=user_data)

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        igtvs = OrderedDict()
        after = ""

        logging.info(msg=f'User {url} igtvs.')
        while True:
            params = {
                "query_hash": self.user_igtvs_query_hash,
                "id": user_data["id"],
                "first": "50",
                "after": after if after else "",
            }

            igtv_data = self._make_request(
                url=query_url, params=params,
            )["data"]["user"]["edge_felix_video_timeline"]

            for igtv in igtv_data["edges"]:
                igtv = igtv["node"]

                post_link = f'{self.BASE_URL}tv/{igtv["shortcode"]}'
                post_info = self.get_single_post(url=post_link)

                igtvs[igtv["shortcode"]] = {
                    "comments": post_info["comments"],
                    "description": igtv["edge_media_to_caption"]["edges"][0]["node"]["text"],
                    "likes": igtv["edge_liked_by"]["count"],
                    "owner_link": post_info["owner_link"],
                    "owner_username": post_info["owner_username"],
                    "post_content": post_info["post_content"],
                    "post_content_len": 1,
                    "post_link": post_link,
                    "posted_at": igtv["edge_liked_by"]["count"],
                    "title": igtv["title"],
                    "shortcode": igtv["shortcode"],
                }

            if igtv_data["page_info"]["has_next_page"]:
                after = igtv_data["page_info"]["end_cursor"]
            else:
                logging.info(f'IGTVs count: {len(igtvs)}')
                break

        return igtvs

    def get_stories(self, url: str = "", reel_id: str = "") -> OrderedDict:
        """
        Collects all content and information about active stories
        on the user page.

        :param url: link to a profile (https://www.instagram.com/username/).
        """

        if url:
            user_data = self.get_user_info(url=url)
            self._can_parse_profile(user_data=user_data)

        query_url = f"{self.STORIES_URL}{self.STORIES_QUERY}"

        params = {
            "reel_ids": reel_id if reel_id else user_data["id"],
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

        stories = OrderedDict()
        stories_data = self._make_request(
            query_url, params=params, headers=headers)["reels_media"]

        if stories_data:
            stories_data = stories_data[0]
        else:
            return stories

        for storie in stories_data["items"]:
            username = stories_data["user"]["username"]

            stories[storie["id"]] = {
                "comments": None,
                "description": None,
                "likes": None,
                "owner_link": f'{self.BASE_URL}{username}',
                "owner_username": username,
                "post_content_len": 1,
                "post_link": f'{self.BASE_URL}stories/{username}/{storie["id"]}',
                "posted_at": storie["taken_at"],
                "title": None,  # TODO: у хайлайтов должен быт тайтл, добавить
                "shortcode": storie["id"],
            }

            if storie["media_type"] == 1:
                stories[storie["id"]]["post_content"] = [
                    storie["image_versions2"]["candidates"][0]["url"],
                ]
            else:
                stories[storie["id"]]["post_content"] = [
                    storie["video_versions"][0]["url"],
                ]
        logging.info(msg=f'User {url} stories. Count: {len(stories)}')

        return stories

    def get_followers(self, url: str) -> Dict:
        """
        Collects all information about user followers.

        :param url: link to a profile (https://www.instagram.com/username/).
        """

        user_data = self.get_user_info(url=url)
        self._can_parse_profile(user_data=user_data)

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        after = ""

        user_followers = {
            "count": user_data["edge_followed_by"],
            "followers_usernames": [],
            "followers": {},
        }

        user_id = user_data["id"]
        while True:
            params = {
                "query_hash": self.followers_query_hash,
                "id": user_id,
                "include_reel": False,
                "fetch_mutual": False,
                "first": 50,
                "after": after if after else "",
            }

            data = self._make_request(
                url=query_url, params=params,
            )["data"]["user"]["edge_followed_by"]

            for user in data["edges"]:
                user_followers["followers_usernames"].append(
                    user["node"]["username"])

            if data["page_info"]["has_next_page"]:
                after = data["page_info"]["end_cursor"]
            else:
                break

        for username in user_followers["followers_usernames"]:
            follower_url = f'{self.BASE_URL}{username}/'
            follower_info = self.get_user_info(url=follower_url)
            user_followers["followers"][username] = follower_info
            how_sleep(data_len=len(user_followers["followers"]))

        logging.info(
            msg=f'User {url} followers. Count: {len(user_followers["followers"])}')

        return user_followers

    # almost 17 minutes for 800 items
    def get_followed_by_user(self, url: str) -> Dict:
        """
        Collects all information about users followed
        by requested profile owner.

        :param url: link to a profile (https://www.instagram.com/username/).
        """

        user_data = self.get_user_info(url=url)
        self._can_parse_profile(user_data=user_data)

        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        after = ""

        user_follow = {
            "count": user_data["edge_follow"],
            "usernames": [],
            "followed": {},
        }
        user_id = user_data["id"]

        while True:
            params = {
                "query_hash": self.followed_by_user_query_hash,
                "id": user_id,
                "first": 50,
                "after": after if after else "",
            }

            data = self._make_request(
                url=query_url, params=params)["data"]["user"]["edge_follow"]

            for user in data["edges"]:
                user_follow["usernames"].append(
                    user["node"]["username"])

            if data["page_info"]["has_next_page"]:
                after = data["page_info"]["end_cursor"]
            else:
                break

        for username in user_follow["usernames"]:
            url_followed_by_user = f'{self.BASE_URL}{username}/'
            info = self.get_user_info(url=url_followed_by_user)
            user_follow["followed"][username] = info
            how_sleep(data_len=len(user_follow["followed"]))

        logging.info(
            msg=f'Followed by user {url}. Count: {len(user_follow["followed"])}')
        return user_follow

    @staticmethod
    def _collect_post_content(post: Dict) -> List:
        if post.get("edge_sidecar_to_children"):
            post_content = [
                (elem["node"]
                 .get("video_url") or elem["node"]
                 .get("display_url"))
                for elem in post["edge_sidecar_to_children"]["edges"]
            ]
        elif post.get("product_type") == "igtv":
            post_content = [post.get("video_url")]
        else:
            post_content = [post.get(
                "video_url") or post.get("display_url")]

        return post_content

    def _cookie_to_json(self) -> Dict:
        """
        Converts a cookie-string to a dictionary.
        """

        if isinstance(self.cookie, dict):
            return self.cookie

        cookie_dict = {}
        for cookie in self.cookie.split(";"):
            if cookie != "":
                cookie_dict[cookie.split("=")[0].strip()
                            ] = cookie.split("=")[1].strip()

        return cookie_dict

    @staticmethod
    def _can_parse_profile(user_data: Dict):
        """
        Check can or cannot parse a user's profile,
        depending on account privacy and is the viewer
        followed to that or not.

        :param user-data: dictionary with information about user account.
        :raises :class: `PrivateProfileError`
        if the declared statement occurred.
        """

        if isinstance(user_data, Dict):
            is_private = user_data["is_private"]
            followed_by_viewer = user_data["followed_by_viewer"]

            if is_private and not followed_by_viewer:
                logging.error("PrivateProfileError")
                raise PrivateProfileError

    def forming_post_data(self, post_data):
        post_content = self._collect_post_content(post=post_data)
        product_type = "tv/" if post_data.get("product_type") == "igtv" else "p/"

        if post_data["edge_media_to_caption"]["edges"]:
            description = post_data["edge_media_to_caption"]["edges"][0]["node"]["text"]
        else:
            description = None

        comments = post_data.get("edge_media_preview_comment", None) or post_data.get("edge_media_to_comment")

        post_info = {
            "description": description,
            "likes": post_data["edge_media_preview_like"]["count"],
            "comments": comments["count"],
            "owner_link": f"{self.BASE_URL}{post_data['owner']['username']}/",
            "owner_username": post_data['owner']['username'],
            "post_content": post_content,
            "post_content_len": len(post_content),
            "posted_at": post_data["taken_at_timestamp"],
            "shortcode": post_data["shortcode"],
            "post_link": (f'{self.BASE_URL}{product_type}{post_data["shortcode"]}/'),
        }

        return post_info
