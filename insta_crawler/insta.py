from collections import OrderedDict
from datetime import datetime as dt
from typing import Dict, Union
from pprint import pprint

import requests
from fake_useragent import UserAgent


class InstaCrawler:
    BASE_URL: str = "https://www.instagram.com/"
    STORIES_URL: str = "https://i.instagram.com/"
    GRAPHQL_QUERY: str = "graphql/query/"
    STORIES_QUERY: str = "api/v1/feed/reels_media/"

    all_posts_query_hash: str
    user_reels_query_hash: str
    followers_query_hash: str
    followed_by_user_query_hash: str

    cookie: str

    def __init__(self, cookie):
        self.cookie = cookie or {}
        self.all_posts_query_hash = "003056d32c2554def87228bc3fd9668a"
        self.user_reels_query_hash = "d4d88dc1500312af6f937f7b804c68c3"
        self.user_igtvs_query_hash = "bc78b344a68ed16dd5d7f264681c4c76"
        self.cookie_user_timeline_hash = "b1245d9d251dff47d91080fbdd6b274a"
        self.followers_query_hash = "c76146de99bb02f6415203be841dd25a"
        self.followed_by_user_query_hash = "d04b0a864b4b54837c0d870b0e77e076"
        self.x_ig_app_id = "936619743392459"

    def _make_request(self, url: str,
                      params: Dict[str, str],
                      headers: Dict[str, str] = {}) -> Dict:
        data = requests.get(
            url=url,
            params=params,
            cookies=self._cookie_to_json(),
            headers=headers,
        )
        data.raise_for_status()
        return data.json()

    def get_cookie_user(self):
        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        params = {
            "query_hash": self.cookie_user_timeline_hash,
        }
        cookie_user_username = self._make_request(query_url, params=params)[
            "data"]["user"]["username"]

        user_url = f"{self.BASE_URL}{cookie_user_username}/"
        cookie_user_info = self.get_user_info(url=user_url)

        return cookie_user_info

    def get_user_info(self, url: str) -> Dict[str, str]:
        params = {"__a": 1}
        user_data = self._make_request(url, params)["graphql"]

        user_data = user_data.get("user") or user_data.get(
            "shortcode_media")["owner"]

        user_info = {
            "bio": user_data.get("biography"),
            "external_url": user_data.get("external_url"),
            "edge_followed_by": user_data.get("edge_followed_by").get(
                "count"
            ) if user_data.get("edge_followed_by") else None,
            "edge_follow": user_data.get("edge_follow").get(
                "count"
            ) if user_data.get("edge_follow") else None,
            "full_name": user_data.get("full_name"),
            "highlight_reel_count": user_data.get("highlight_reel_count"),
            "id": user_data.get("id"),
            "is_business_account": user_data.get("is_business_account"),
            "business_category_name": user_data.get("business_category_name"),
            "category_name": user_data.get("category_name"),
            "is_private": user_data.get("is_private"),
            "username": user_data.get("username"),
            "igtv_count": user_data.get("edge_felix_video_timeline").get(
                "count"
            ) if user_data.get("edge_felix_video_timeline") else None,
            "posts_count": user_data.get("edge_owner_to_timeline_media").get(
                "count"
            ) if user_data.get("edge_owner_to_timeline_media") else None,
            "profile_pic_hd": user_data.get("profile_pic_url_hd"),
            "followed_by_viewer": user_data.get("followed_by_viewer"),
            "user_url": url,
        }

        return user_info

    def get_single_post(self, url: str) -> Dict[str, Union[str, list]]:
        params = {"__a": "1"}

        post_data = self._make_request(url, params)[
            "graphql"]["shortcode_media"]

        if post_data.get("edge_sidecar_to_children"):
            post_content = [
                (elem["node"]
                 .get("video_url") or elem["node"]
                 .get("display_url"))
                for elem in post_data["edge_sidecar_to_children"]["edges"]
            ]
        elif post_data.get("product_type") == "igtv":
            post_content = [post_data.get("video_url")]
        else:
            post_content = [post_data.get(
                "video_url") or post_data.get("display_url")]

        post_info = {
            "description": post_data["edge_media_to_caption"]["edges"][0]["node"]["text"],
            "likes": post_data["edge_media_preview_like"]["count"],
            "comments": post_data["edge_media_preview_comment"]["count"],
            "owner_link": f"{self.BASE_URL}{post_data['owner']['username']}",
            "owner_username": post_data['owner']['username'],
            "post_content": post_content,
            "post_content_len": len(post_content),
            "post_link": url,
            "posted_at": dt.utcfromtimestamp(
                post_data["taken_at_timestamp"]).strftime("%H:%M %d-%m-%Y"),
            "shortcode": post_data["shortcode"]
        }

        return post_info

    def get_reels(self, url: str) -> OrderedDict:
        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        params = {
            "query_hash": self.user_reels_query_hash,
            "user_id": self.get_user_info(url)["id"],
            "include_chaining": "true",
            "include_reel": "true",
            "include_suggested_users": "false",
            "include_logged_out_extras": "false",
            "include_highlight_reels": "true",
            "include_live_status": "true",
        }

        reels_data = self._make_request(query_url, params=params)[
            "data"]["user"]

        reels = OrderedDict()
        for reel in reels_data["edge_highlight_reels"]["edges"]:
            reel_content = self.get_stories(
                reel_id=f'highlight:{reel["node"]["id"]}'
            )

            username = reels_data["reel"]["owner"]["username"]

            post_content = [
                post["post_content"][0]
                for post in reel_content.values()
            ]

            reels[reel["node"]["id"]] = {
                "comments": None,
                "description": None,
                "likes": None,
                "owner_link": f'{self.BASE_URL}{username}',
                "owner_username": username,
                "id": reel["node"]["id"],
                "post_content": post_content,
                "post_content_len": len(post_content),
                "post_link": f'{self.BASE_URL}stories/highlights/{reel["node"]["id"]}',
                "posted_at": None,
                "title": reel["node"]["title"],
                "shortcode": None,
            }

        return reels

    def get_posts(self, url: str) -> OrderedDict:
        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        posts = OrderedDict()
        after = ""

        while True:
            params = {
                "query_hash": self.all_posts_query_hash,
                "id": self.get_user_info(url)["id"],
                "first": "50",
                "after": after if after else None,
            }

            posts_data = self._make_request(
                url=query_url, params=params
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
                        (post.get("video_url") or post.get("display_url"))
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
                break

        return posts

    def get_all_igtv(self, url: str) -> OrderedDict:
        query_url = f"{self.BASE_URL}{self.GRAPHQL_QUERY}"
        igtvs = OrderedDict()
        after = ""

        while True:
            params = {
                "query_hash": self.user_igtvs_query_hash,
                "id": self.get_user_info(url)["id"],
                "first": "50",
                "after": after if after else "",
            }

            igtv_data = self._make_request(
                url=query_url, params=params
            )["data"]["user"]["edge_felix_video_timeline"]

            for igtv in igtv_data["edges"]:
                igtv = igtv["node"]

                post_link = f'{self.BASE_URL}tv/{igtv["shortcode"]}'
                post_info = self.get_single_post(url=post_link)

                igtvs[igtv["shortcode"]] = {
                    "comments": post_info["comments"],
                    "description": igtv["edge_media_to_caption"]["edges"][0]["node"]["text"],
                    "likes": igtv["edge_liked_by"]["count"],
                    "owner_link": post_info["owner"],
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
                break

        return igtvs

    def get_stories(self,
                    url: str = "",
                    reel_id: str = "") -> OrderedDict:
        query_url = f"{self.STORIES_URL}{self.STORIES_QUERY}"

        params = {
            "reel_ids": reel_id if reel_id else self.get_user_info(url)["id"],
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
                    storie["image_versions2"]["candidates"][0]["url"]
                ]
            else:
                stories[storie["id"]]["post_content"] = [
                    storie["video_versions"][0]["url"]
                ]

        return stories

    def _cookie_to_json(self) -> Dict:
        if isinstance(self.cookie, dict):
            return self.cookie

        cookie_dict = {}
        for cookie in self.cookie.split(";"):
            if cookie != "":
                cookie_dict[
                    cookie.split("=")[0].strip()] = cookie.split("=")[1].strip()

        return cookie_dict


if __name__ == "__main__":
    pass
