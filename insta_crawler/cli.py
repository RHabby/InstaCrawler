from pprint import pprint
from time import sleep

import click
from prettytable import PrettyTable, ALL
from insta import InstaCrawler
from utils import download_file, download_all


@click.group()
def cli():
    """
    hello there.

    """
    click.echo("Starting")


@cli.command()
@click.option("-C", "--cookie",
              help="You can paste your cookie")
@click.option("-u", "--username",
              required=True, help="Username Required")
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

    table = PrettyTable(padding_width=5)
    table.field_names = ["FIELD NAME", "INFO"]

    tds = {
        "Instagram URL": USER_URL.format(username=username),
        "Username": user_info["username"],
        "Bio": fr'{user_info["bio"]}',
        "Full Name": user_info["full_name"].replace("\t", "-"),
        "Business Category": user_info["business_category_name"],
        "Category": user_info["category_name"],
        "Followers": user_info["edge_followed_by"],
        "Follows": user_info["edge_follow"],
        "Posts": user_info["posts_count"],
        "Reels": user_info["highlight_reel_count"],
        "IGTV": user_info["igtv_count"],
        "Is Private": user_info["is_private"],
        "ID": user_info["id"],
        "Ext URL": user_info["external_url"],
    }

    for field, info in tds.items():
        table.add_row([field, info])

    print(table.get_string(title=f"Info about {username}`s instagram account"))


@cli.command()
@click.option("-C", "--cookie", help="You can paste your cookie")
@click.option("-u", "--url", required=True, help="URL Required")
def single_post(cookie: str, url: str):
    """
    This command provides you information about the post by url.
    """

    inst = InstaCrawler(cookie=cookie)
    links = inst.get_single_post(url=url)

    table = PrettyTable(padding_width=3)
    table.field_names = ["FIELD NAME", "POST INFO"]
    table._max_width = {"POST INFO": 100}

    for field, info in links.items():
        post_links = []

        if field == "post_content":
            for i in range(len(links["post_content"])):
                post_links.append(
                    [f"link {i + 1}", f'{links["post_content"][i]}\n'])
            table.add_rows(post_links)
            continue

        table.add_row([field, f"{info}\n"])

    print(table.get_string(
        title=f"{links['owner_username']}`s instagram post"))

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


@cli.command()
@click.option("-C", "--cookie",
              help="You can paste your cookie")
@click.option("-u", "--username",
              required=True, help="Username Required")
@click.option("-ct", "--content-type",
              type=click.Choice(
                  ["posts", "stories", "highlights", "igtv", "all"],
                  case_sensitive=False))
def ctgry(cookie: str, username: str, content_type: str):
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

    for ct, value in data.items():
        if value:
            click.echo(f'Начинаю скачивать категорию {ct}...')
            download_all(posts=value,
                         content_type=ct,
                         username=username)
        else:
            continue

    click.echo("\nГотово!")


if __name__ == "__main__":
    cli()
