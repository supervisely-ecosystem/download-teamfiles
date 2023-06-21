import json
import os
import shutil
from urllib.parse import unquote, urlparse

import requests
from tqdm import tqdm

import src.globals as g
import supervisely as sly
from supervisely.app.widgets import (
    Button,
    Card,
    Checkbox,
    Container,
    DatasetThumbnail,
    Editor,
    Input,
    Progress,
    ProjectThumbnail,
    SlyTqdm,
    Text,
)

progress_bar = Progress(show_percents=False)

input_tf_dest_dir = Input(placeholder="Please input here destination directory in Team files")
editor = Editor(initial_text='{"archive.zip":"https://url.com/archive.zip"}')
button_download = Button(text="Download")


card_1 = Card(
    title="Download from url",
    content=Container(widgets=[input_tf_dest_dir, editor, button_download, progress_bar]),
)

progress_bar.hide()


@button_download.click
def download():
    data_dict = json.loads(editor.get_text())

    progress_bar.show()
    with progress_bar(
        message=f"Iterating dict with URLs", total=len(data_dict.values())
    ) as bigpbar:
        for file_name, url in data_dict.items():
            local_path = os.path.join(g.STORAGE_DIR, file_name)
            response = requests.get(url, stream=True)

            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024

            with tqdm(
                message=f"Downloading {file_name} to buffer",
                total=total_size,
                unit="B",
                unit_scale=True,
            ) as pbar:
                with open(local_path, "wb") as file:
                    for data in response.iter_content(block_size):
                        file.write(data)
                        pbar.update(len(data))

            tf_dst_path = os.path.join(input_tf_dest_dir.get_value(), file_name)
            with tqdm(
                message=f"Uploading {file_name} to Team files",
                total=total_size,
                unit="B",
                unit_scale=True,
            ) as pbar:
                g.api.file.upload(g.TEAM_ID, local_path, tf_dst_path, progress_cb=pbar)

            os.remove(local_path)
            bigpbar.update(1)
