import json
import os
from collections import OrderedDict
from pprint import pprint
from time import sleep

import click

from insta import InstaCrawler
from utils import (download_all, download_file, export_as_csv, export_as_json,
                   print_single_post_info_table, print_user_info_table)


@click.group()
def get_insta():
    """
    hello there.

    """
    click.echo("Starting")


@get_insta.command()
@click.option("-C", "--cookie", required=True,
              help="You can paste your cookie")
def cookie_user(cookie: str):
    inst = InstaCrawler(cookie=cookie)
    cookie_user = inst.get_cookie_user()

    print_user_info_table(user_info=cookie_user)


@get_insta.command()
@click.option("-u", "--username",
              required=True, help="Username Required")
@click.option("-C", "--cookie", help="You can paste your cookie")
def user_info(cookie: str, username: str):
    """
    This command provides you some information about the account.

    To get information you need to paste at least
    the username of the account you are interested in.

    Also you can paste cookie string.
    """

    inst = InstaCrawler(cookie=cookie)
    USER_URL = "https://www.instagram.com/{username}/"
    user_info = inst.get_user_info(url=USER_URL.format(username=username))

    print_user_info_table(user_info=user_info)


@get_insta.command()
@click.option("-u", "--url", required=True, help="URL Required")
@click.option("-C", "--cookie", help="You can paste your cookie")
def single_post(cookie: str, url: str):
    """
    This command provides you information about the post by url.
    """

    inst = InstaCrawler(cookie=cookie)
    links = inst.get_single_post(url=url)

    print_single_post_info_table(post_info=links)

    if click.confirm("\nDownload the post`s content?", abort=True):
        with click.progressbar(length=len(links["post_content"]),
                               label="Downloading content:",
                               width=100) as bar:
            total = 0
            for index, link in enumerate(links["post_content"]):
                name = f"{links['owner_username']}_{links['shortcode']}_{index + 1}{'.mp4' if '.mp4' in link else '.png'}"

                download_file(url=link, content_type="posts",
                              username=links["owner_username"], name=name)

                total += 1
                bar.update(total)

    click.echo("\nDone")


@get_insta.command()
@click.option("-ct", "--content-type",
              type=click.Choice(
                  ["posts", "stories", "highlights", "igtv", "all"],
                  case_sensitive=False))
@click.option("-u", "--username",
              required=True, help="Username Required")
@click.option("-C", "--cookie", help="You can paste your cookie")
def category(cookie: str, username: str, content_type: str):
    """
    all posts func help message
    """

    USER_URL = f"https://www.instagram.com/{username}"
    insta = InstaCrawler(cookie=cookie)

    data = {}
    if content_type == "posts":
        data[content_type] = insta.get_posts(url=USER_URL)
    if content_type == "stories":
        data[content_type] = insta.get_stories(url=USER_URL)
    if content_type == "reels":
        data[content_type] = insta.get_reels(url=USER_URL)
    if content_type == "igtv":
        data[content_type] = insta.get_all_igtv(url=USER_URL)
    if content_type == "all":
        data = {
            "posts": insta.get_posts(url=USER_URL),
            "stories": insta.get_stories(url=USER_URL),
            "highlights": insta.get_reels(url=USER_URL),
            "igtv": insta.get_all_igtv(url=USER_URL)
        }

    click.echo("Данные страницы получены.")
    if click.confirm("Сохранить данные в JSON?"):
        export_as_json(data=data, username=username, content_type="content")

    if click.confirm("csv"):
        headers_row = ["comments", "description", "likes",
                       "owner_link", "owner_username", "post_link",
                       "posted_at", "title", "shortcode", "post_content",
                       "post_content_len", "content_type"]
        export_as_csv(data=data, headers_row=headers_row,
                      username=username, content_type="content")

    if click.confirm("Загрузить содержимое?", abort=True):
        for ct, value in data.items():
            if value:
                click.echo(f'Начинаю скачивать категорию {ct}...')
                download_all(posts=value,
                             content_type=ct,
                             username=username)
            else:
                continue

    click.echo("Готово!")


if __name__ == "__main__":
    get_insta()
