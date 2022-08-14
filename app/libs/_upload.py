import shutil
from datetime import date

from app.core import settings
from mega import Mega


class Upload:
    def __init__(self):
        self.api = Mega()

        if settings.mega_username and settings.mega_password:
            self.login(settings.mega_username, settings.mega_password)

    def login(self, username, password):
        self.api.login(username, password)

    def upload(self):
        filename = f"assets-{date.today()}"

        shutil.make_archive(filename, "zip", root_dir="./assets")

        uploaded = self.api.upload(f"{filename}.zip")

        return self.api.get_upload_link(uploaded)


upload = Upload()
