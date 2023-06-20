import src.globals as g
import src.utils as u

import shutil
import supervisely as sly
from urllib.parse import urlparse, unquote
import requests
from tqdm import tqdm
import json
import os

from supervisely.app.widgets import (
    Input,
    Container,
    Card,
    Text,
    Button,
    Progress,
    DatasetThumbnail,
    ProjectThumbnail,
    Editor,
    SlyTqdm,
    Checkbox
)

progress_bar = Progress(show_percents=False)



input_tf_dest_dir = Input(placeholder='Please input here result directory in team files')
editor = Editor(initial_text='{"url_name":"https://url.com/archive.zip"}')
button_download = Button(text='Download')



# progress_bar_download = SlyTqdm()

card_1 = Card(
    title="Download from url",
    content=Container(
        widgets=[
            input_tf_dest_dir,
            editor,
            button_download,
            progress_bar
        ]
    ),
)

progress_bar.hide()
# thumbnail.hide()


@button_download.click
def download():

    data_dict = json.loads(editor.get_text())

    # url = "http://example.com/file.txt"  # Replace with the URL of the file you want to download
    tf_destination_directory = os.path.join(g.STORAGE_DIR, 'downloads')  # Replace with the desired path to save the file

    progress_bar.show()
    with progress_bar(message=f"Iterating dict with URLs", total=len(data_dict.values())) as bigpbar:

        for name, url in data_dict.items():

            parsed_url = urlparse(url)
            file_name = os.path.basename(parsed_url.path)
            file_name = unquote(file_name) 
            destination_path = os.path.join(tf_destination_directory, name, file_name)

            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            response = requests.get(url, stream=True)

            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024

            with tqdm(message=f"Downloading {name} to buffer", total=total_size, unit='B', unit_scale=True) as pbar:
                with open(destination_path, 'wb') as file:
                    for data in response.iter_content(block_size):
                        file.write(data)
                        pbar.update(len(data))
                        
            tf_dst_path = os.path.join(input_tf_dest_dir.get_value(), file_name)
            with tqdm(message=f"Uploading {name} to Team files", total=total_size, unit='B', unit_scale=True) as pbar:
                g.api.file.upload(g.TEAM_ID,destination_path, tf_dst_path, progress_cb=pbar)

            shutil.rmtree(path=os.path.dirname(destination_path))

            bigpbar.update(1)



