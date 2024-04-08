# -*- coding: utf-8 -*-

from pathlib import Path
from tuxsuite.requests import get


def download(build, output):
    output = Path(output)
    output.mkdir(exist_ok=True)
    build_dir = output / build.uid
    build_dir.mkdir(exist_ok=True)
    url = build.status["download_url"] + "?export=json"
    # for private builds
    headers = {"Authorization": build.headers["Authorization"]}
    files = get(url, headers=headers).json()
    # TODO parallelize?
    for f in files["files"]:
        url = f["Url"]
        dest = build_dir / Path(url).name
        with dest.open("wb") as f:
            download_file(url, f, headers)


def download_file(url, dest, headers=""):
    r = get(url, stream=True, headers=headers)
    for chunk in r.iter_content(chunk_size=128):
        dest.write(chunk)
