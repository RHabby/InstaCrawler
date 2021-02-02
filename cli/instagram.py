import json
import os
from collections import OrderedDict
from pprint import pprint
from time import sleep

import click

from insta_crawler.exceptions import NoCookieError
from insta_crawler.insta import InstaCrawler
from insta_crawler.utils import (download_all, download_file, export_as_csv,
                                 export_as_json, print_single_post_info_table,
                                 print_user_info_table)


@click.group()
def get_insta():
    """
    Used to collect information and data from Instagram profile.

    """

    click.echo("\nStarting...")
    click.echo("OK, I am collecting some information...")
    click.echo("-" * 80)


@get_insta.command("cookie-user", short_help="cookie user info")
@click.option("-C", "--cookie", required=True,
              help="Cookie-string from your browser (ig_did and sessionid should be enough).")
def cookie_user(cookie: str):
    """
    Gives an information about cookie-user.

    \b
    EXAMPLE:
    python insta_crawler/cli.py cookie-user \\
    --cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
    """

    try:
        inst = InstaCrawler(cookie=cookie)
    except NoCookieError:
        click.echo("You forgot the cookie-string.")
        return

    cookie_user = inst.get_cookie_user()

    click.echo("There it is:")
    print_user_info_table(user_info=cookie_user)


@get_insta.command("user-info", short_help="user info by URL")
@click.option("-u", "--username", required=True,
              help="Username of the user you are interested in.")
@click.option("-C", "--cookie", required=True,
              help="Cookie-string from your browser (ig_did and sessionid should be enough).")
def user_info(cookie: str, username: str):
    """
    Gives information about the user by link to his profile.

    \b
    EXAMPLE:
    python insta_crawler/cli.py user-info \\
    --username="username" \\
    --cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
    """

    inst = InstaCrawler(cookie=cookie)
    USER_URL = "https://www.instagram.com/{username}/"
    user_info = inst.get_user_info(url=USER_URL.format(username=username))
    click.echo("There it is:")
    print_user_info_table(user_info=user_info)


@get_insta.command("post", short_help="post info by URL")
@click.option("-u", "--url", required=True, help="post URL")
@click.option("-C", "--cookie", required=True,
              help="Cookie-string from your browser (ig_did and sessionid should be enough).")
def post(cookie: str, url: str):
    """
    Gives information about the post by link to it.

    \b
    EXAMPLE:
    python insta_crawler/cli.py post \\
    --url="https://www.instagram.com/(p OR tv)/shortcode/" \\
    --cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
    """

    inst = InstaCrawler(cookie=cookie)
    links = inst.get_single_post(url=url)
    click.echo("There it is:")
    print_single_post_info_table(post_info=links)

    if click.confirm("\nWould you like to download the content of the post?",
                     abort=True):
        for index, link in enumerate(links["post_content"]):
            name = f"{links['owner_username']}_{links['shortcode']}_{index + 1}{'.mp4' if '.mp4' in link else '.png'}"

            download_file(url=link, content_type="posts",
                          username=links["owner_username"], name=name)

    click.echo("\nAll done")


@get_insta.command("category", short_help="full category info")
@click.option("-ct", "--content-type",
              type=click.Choice(
                  ["posts", "stories", "highlights", "igtv", "all"],
                  case_sensitive=False))
@click.option("-u", "--username", required=True,
              help="Username of the user you are interested in.")
@click.option("-C", "--cookie", required=True,
              help="Cookie-string from your browser ('ig_did' and 'sessionid' should be enough).")
def category(cookie: str, username: str, content_type: str):
    """
    Collects all content and information about posts
    or highlights or stories or igtvs or all together
    on the user page.

    \b
    EXAMPLE:
    python insta_crawler/cli.py category \\
    --content-type="(posts OR stories OR highlights OR igtv OR all)" \\
    --username="username" \\
    --cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
    """

    USER_URL = f"https://www.instagram.com/{username}"
    insta = InstaCrawler(cookie=cookie)

    data = {}
    if content_type == "posts":
        data[content_type] = insta.get_posts(url=USER_URL)
    if content_type == "stories":
        data[content_type] = insta.get_stories(url=USER_URL)
    if content_type == "reels":
        data[content_type] = insta.get_highlights(url=USER_URL)
    if content_type == "igtv":
        data[content_type] = insta.get_all_igtv(url=USER_URL)
    if content_type == "all":
        data = {
            "posts": insta.get_posts(url=USER_URL),
            "stories": insta.get_stories(url=USER_URL),
            "highlights": insta.get_highlights(url=USER_URL),
            "igtv": insta.get_all_igtv(url=USER_URL)
        }

    click.echo("All data has been collected")
    click.echo("-" * 80)
    if click.confirm("Would you like to save the content of the post as JSON?"):
        export_as_json(data=data, username=username, content_type="content")
    click.echo("-" * 80)

    if click.confirm("Would you like to save the content of the post as CSV?"):
        headers_row = ["comments", "description", "likes",
                       "owner_link", "owner_username", "post_link",
                       "posted_at", "title", "shortcode", "post_content",
                       "post_content_len"]
        export_as_csv(data=data, headers_row=headers_row,
                      username=username, content_type="content")
    click.echo("-" * 80)

    if click.confirm("Would you like to download the content of the post?", abort=True):
        for ct, value in data.items():
            if value:
                click.echo(f'I am downloading {ct} content now...')
                download_all(posts=value,
                             content_type=ct,
                             username=username)
                click.echo("-" * 80)
            else:
                continue

    click.echo("All done!")


@get_insta.command("followers", short_help="user followers")
@click.option("-u", "--username", required=True,
              help="Username of the user you are interested in.")
@click.option("-C", "--cookie", required=True,
              help="Cookie-string from your browser (ig_did and sessionid should be enough).")
def followers(cookie: str, username: str):
    """
    Collects all information about user followers.

    \b
    EXAMPLE:
    python insta_crawler/cli.py followers \\
    --username="username" \\
    --cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
    """

    USER_URL = f"https://www.instagram.com/{username}"

    insta = InstaCrawler(cookie=cookie)
    followers = insta.get_followers(url=USER_URL)

    click.echo("All data has been collected")
    click.echo("-" * 80)
    if click.confirm("Would you like to save the content of the post as JSON?"):
        export_as_json(data=followers, username=username,
                       content_type="followers")
    click.echo("-" * 80)

    if click.confirm("Would you like to save the content of the post as CSV?"):
        headers_row = ["bio", "external_url", "edge_followed_by",
                       "edge_follow", "full_name", "highlight_reel_count",
                       "id", "is_business_account", "business_category_name",
                       "category_name", "is_private", "username", "igtv_count",
                       "posts_count", "profile_pic_hd", "followed_by_viewer",
                       "user_url"]
        export_as_csv(data=followers, headers_row=headers_row,
                      username=username, content_type="followers")

    click.echo("-" * 80)
    click.echo("All done!")


@get_insta.command("followed-by-user", short_help="profiles followed by user")
@click.option("-u", "--username", required=True,
              help="Username of the user you are interested in.")
@click.option("-C", "--cookie", required=True,
              help="Cookie-string from your browser (ig_did and sessionid should be enough).")
def followed_by_user(cookie: str, username: str):
    """
    Collects all information about users followed
    by requested profile owner.

    \b
    EXAMPLE:
    python insta_crawler/cli.py followed-by-user \\
    --username="username" \\
    --cookie="ig_did=XXXXXXXX-YYYY-CCCC-AAAA-ZZZZZZZZZZZZ; sessionid=1111111111111111111111111;"
    """

    USER_URL = f"https://www.instagram.com/{username}"

    insta = InstaCrawler(cookie=cookie)
    user_follow = insta.get_followed_by_user(url=USER_URL)

    click.echo("All data has been collected")
    click.echo("-" * 80)

    if click.confirm("Would you like to save the content of the post as JSON?"):
        export_as_json(data=user_follow, username=username,
                       content_type="followed_by")
    click.echo("-" * 80)

    if click.confirm("Would you like to save the content of the post as CSV?"):
        headers_row = ["bio", "external_url", "edge_followed_by",
                       "edge_follow", "full_name", "highlight_reel_count",
                       "id", "is_business_account", "business_category_name",
                       "category_name", "is_private", "username", "igtv_count",
                       "posts_count", "profile_pic_hd", "followed_by_viewer",
                       "user_url"]
        export_as_csv(data=user_follow, headers_row=headers_row,
                      username=username, content_type="followed_by")

    click.echo("-" * 80)
    click.echo("All done!")


if __name__ == "__main__":
    get_insta()
