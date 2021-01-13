import os
from pprint import pprint
from typing import OrderedDict, Dict

import requests


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
    for addr, post in posts.items():
        if content_type == "igtvs":
            links = [post["post_content"]["post_content"]]
        else:
            links = post["post_content"]

        for index, link in enumerate(links):
            name = fr"{username}_{content_type}_{addr.replace('/', '_')}_0{index+1}{'.mp4' if 'mp4' in link else '.png'}"
            try:
                download_file(
                    url=link,
                    content_type=content_type,
                    username=username,
                    name=name,
                )
            except requests.exceptions.HTTPError:
                continue
            except Exception:
                undone.append(
                    {
                        "username": username,
                        "content_type": content_type,
                        "link": link,
                        "name": name,
                    }
                )

    for item in undone:
        pprint(undone)
        download_file(
            username=item["username"],
            content_type=item["content_type"],
            url=item["link"],
            name=item["name"],
        )


if __name__ == "__main__":
    pass
