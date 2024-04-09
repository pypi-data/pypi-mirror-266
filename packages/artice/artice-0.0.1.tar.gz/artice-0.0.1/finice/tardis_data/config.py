import os

from dotenv import load_dotenv

from finice.utils import touch_or_make_dir


class TardisConfig:
    api_key = None

    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("TARDIS_API_KEY")
        data_dir_str = os.environ.get("TARDIS_DATA_DIR", "./tardis_data")
        self.data_dir = touch_or_make_dir(data_dir_str) if data_dir_str else None


tardis_config = TardisConfig()
"""Global configuration for the tardis_fa package."""


__all__ = [
    'TaridsConfig',
    'tardis_config',
]
