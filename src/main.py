import supervisely as sly
import os

from supervisely.app.widgets import Container

from src.ui import card_1


layout = Container(
    widgets=[card_1], 
    direction="vertical"
)

app = sly.Application(layout=layout)

