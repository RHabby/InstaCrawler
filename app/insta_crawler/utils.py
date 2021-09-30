import csv
import json
import os
from time import sleep
from typing import Dict, List

from prettytable import PrettyTable
import requests
from tqdm import tqdm


def export_as_json(data: Dict, username: str, prepocessed: bool = False):
    file_dir = os.path.join(os.getcwd(), "downloads", username)
    path_to_file = os.path.join(file_dir, f"{username}_data.json")

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    if not prepocessed:
        data = {
            key: [dict(item) for item in value]
            for key, value in data.items()
        }
    try:
        with open(path_to_file, "r", encoding="utf-8") as file:
            file_data = json.load(file)
        file_data.update(data)
    except Exception:
        file_data = data
    finally:
        with open(path_to_file, "w", encoding="utf-8") as file:
            json.dump(
                file_data,
                file,
                ensure_ascii=False,
                indent=4,
            )


def export_as_csv(data: List, headers_row: List,
                  username: str, content_type: str):
    file_dir = os.path.join(os.getcwd(), "downloads", username)
    path_to_file = os.path.join(file_dir, f"{username}_{content_type}.csv")

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(path_to_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(headers_row)

        for item in data:
            item = dict(item)
            row = [item[header] for header in headers_row]
            writer.writerow(row)


def download_file(url: str, content_type: str,
                  username: str, name: str) -> str:

    file_dir = os.path.join(os.getcwd(), "downloads", username, content_type)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    path_to_file = os.path.join(file_dir, name)
    if os.path.exists(path_to_file):
        return path_to_file
    else:
        chunk_size = 1024
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path_to_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
        return path_to_file


def download_all(posts: List[Dict],
                 content_type: str, username: str) -> None:
    undone = []
    total_links = sum([len(post.post_content) for post in posts])
    with tqdm(total=total_links) as pbar:
        for post in posts:
            shortcode = post.highlight_id if content_type == "highlights" else post.shortcode
            links = post.post_content
            for index, link in enumerate(links):
                name = (
                    f"{username}_{content_type}_{shortcode}_0{index+1}"
                    f"{'.mp4' if 'mp4' in link else '.png'}"
                )
                try:
                    download_file(
                        url=link,
                        content_type=content_type,
                        username=username,
                        name=name,
                    )
                    pbar.update(1)
                except requests.exceptions.HTTPError:
                    continue
                except Exception:
                    undone.append(
                        {
                            "username": username,
                            "content_type": content_type,
                            "link": link,
                            "name": name,
                        },
                    )
        for item in undone:
            download_file(
                username=item["username"],
                content_type=item["content_type"],
                url=item["link"],
                name=item["name"],
            )
            pbar.update(1)


def print_user_info_table(user_info: Dict) -> None:
    table = PrettyTable(padding_width=5)
    table.field_names = ["FIELD NAME", "INFO"]

    tds = {
        "Instagram URL": user_info["user_url"],
        "Username": user_info["username"],
        "Bio": fr'{user_info["bio"]}',
        "Full Name": user_info["full_name"].replace("\t", "-"),
        "Business Category": user_info["business_category_name"],
        "Category": user_info["category_name"],
        "Followers": user_info["followed_by"],
        "Follows": user_info["follow"],
        "Posts": user_info["posts_count"],
        "Reels": user_info["highlight_reel_count"],
        "IGTV": user_info["igtv_count"],
        "Is Private": user_info["is_private"],
        "ID": user_info["user_id"],
        "Ext URL": user_info["external_url"],
        "Followed by Viewer": user_info["followed_by_viewer"],
    }

    for field, info in tds.items():
        table.add_row([field, info])

    print(table.get_string(
        title=f"Info about {user_info['username']}`s instagram account"))


def print_single_post_info_table(post_info: Dict) -> None:
    table = PrettyTable(padding_width=3)
    table.field_names = ["FIELD NAME", "POST INFO"]
    table._max_width = {"POST INFO": 100}

    for field, info in post_info.items():
        post_links = []

        if field == "post_content":
            for i in range(len(post_info["post_content"])):
                post_links.append(
                    [f"link {i + 1}", f'{post_info["post_content"][i]}\n'])
            table.add_rows(post_links)
            continue

        table.add_row([field, f"{info}\n"])

    print(table.get_string(
        title=f"{post_info['owner_username']}`s instagram post"))


def how_sleep(data_len: int) -> None:
    if data_len % 1000 == 0:
        sleep(11)
    elif data_len % 100 == 0:
        sleep(9)
    elif data_len % 25 == 0:
        sleep(7)
    else:
        pass


def get_data_by_content_type(insta, content_type: str, user_url: str) -> Dict:
    data = {}
    if content_type == "posts":
        data[content_type] = insta.get_posts(url=user_url)
    elif content_type == "stories":
        data[content_type] = insta.get_stories(url=user_url)
    elif content_type == "highlights":
        data[content_type] = insta.get_highlights(url=user_url)
    elif content_type == "igtv":
        data[content_type] = insta.get_all_igtv(url=user_url)
    elif content_type == "all":
        data = {
            "posts": insta.get_posts(url=user_url),
            "stories": insta.get_stories(url=user_url),
            "highlights": insta.get_highlights(url=user_url),
            "igtv": insta.get_all_igtv(url=user_url),
        }

    return data


if __name__ == "__main__":
    pass
