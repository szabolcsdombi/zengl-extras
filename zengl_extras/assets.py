import os

import requests
from progress.bar import Bar

CDN = "https://f003.backblazeb2.com/file/zengl-data/examples"
DOWNLOADS = os.path.abspath("downloads")


class Loader:
    def __init__(self, filename, total_size):
        print(f"Downloading {filename}")
        self.bar = Bar("Progress", fill="-", suffix="%(percent)d%%", max=total_size)

    def update(self, chunk_size):
        self.bar.next(chunk_size)

    def finish(self):
        self.bar.finish()


def get(filename):
    full_path = os.path.join(DOWNLOADS, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    if os.path.isfile(full_path):
        return full_path
    with requests.get(f"{CDN}/{filename}", stream=True) as request:
        if not request.ok:
            raise Exception(request.text)
        total_size = int(request.headers.get("Content-Length"))
        loader = Loader(filename, total_size)
        with open(full_path + ".temp", "wb") as f:
            chunk_size = (total_size + 100 - 1) // 100
            for chunk in request.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                loader.update(len(chunk))
        os.rename(full_path + ".temp", full_path)
        loader.finish()
    return full_path
