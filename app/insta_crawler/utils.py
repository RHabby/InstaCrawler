import csv
import json
import os
from time import sleep
from typing import Dict, List, OrderedDict

from prettytable import PrettyTable
import requests
from tqdm import tqdm


def export_as_json(data: Dict, username: str, content_type: str):
    file_dir = os.path.join(os.getcwd(), "downloads", username)
    path_to_file = os.path.join(file_dir, f"{username}_{content_type}.json")

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(path_to_file, "w", encoding="utf-8") as file:
        json.dump(
            dict(OrderedDict(data)),
            file,
            ensure_ascii=False,
            indent=4,
        )


def export_as_csv(data: Dict, headers_row: List,
                  username: str, content_type: str):
    file_dir = os.path.join(os.getcwd(), "downloads", username)
    path_to_file = os.path.join(file_dir, f"{username}_{content_type}.csv")

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(path_to_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(headers_row)

        for content_type, info in data.items():
            if isinstance(info, dict):
                for value in info.values():
                    row = [value[header] for header in headers_row]
                    writer.writerow(row)


def download_file(url: str, content_type: str,
                  username: str, name: str) -> str:
    file_dir = os.path.join(os.getcwd(), "downloads", username, content_type)
    path_to_file = os.path.join(file_dir, name)

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    if os.path.exists(path_to_file):
        return path_to_file
    else:
        # NOTE the stream=True parameter below
        chunk_size = 1024
        chunk_counter = 0
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path_to_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        chunk_counter += 1
        return path_to_file


def download_all(posts: OrderedDict[str, Dict],
                 content_type: str, username: str) -> None:
    undone = []
    total_links = sum([len(post["post_content"]) for post in posts.values()])

    with tqdm(total=total_links) as pbar:
        for addr, post in posts.items():
            links = post["post_content"]
            for index, link in enumerate(links):
                name = (fr"{username}_{content_type}_{addr.replace('/', '_')}_0{index+1}"
                        fr"{'.mp4' if 'mp4' in link else '.png'}")
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


def print_user_info_table(user_info):
    table = PrettyTable(padding_width=5)
    table.field_names = ["FIELD NAME", "INFO"]

    tds = {
        "Instagram URL": user_info["user_url"],
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
        "Followed by Viewer": user_info["followed_by_viewer"],
    }

    for field, info in tds.items():
        table.add_row([field, info])

    print(table.get_string(
        title=f"Info about {user_info['username']}`s instagram account"))


def print_single_post_info_table(post_info):
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


def how_sleep(data_len: int):
    if data_len % 1000 == 0:
        sleep(10)
    elif data_len % 100 == 0:
        sleep(5)
    elif data_len % 25 == 0:
        sleep(2)
    else:
        pass


if __name__ == "__main__":
    pass
