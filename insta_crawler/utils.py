import os

import requests


def download_file(url: str, content_type: str,
                  acc_name: str, name: str) -> str:
    file_dir = os.path.join(os.getcwd(), "downloads", acc_name, content_type)
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
