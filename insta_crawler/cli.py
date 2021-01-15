from pprint import pprint
from time import sleep

import click
from prettytable import PrettyTable, ALL
from insta import InstaCrawler
from utils import download_file


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


@ cli.command()
def posts():
    """
    all posts func help message
    """
    click.echo("posts")


@ cli.command()
def stories():
    """
    all available stories func help message
    """
    click.echo("stories")


@ cli.command()
def reels():
    """
    all reels func help message
    """
    click.echo("reels")


@ cli.command()
def igtvs():
    """
    all igtvs func help message
    """
    click.echo("igtvs")


if __name__ == "__main__":
    cli()
