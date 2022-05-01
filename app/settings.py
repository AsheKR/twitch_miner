import logging
from pathlib import Path

from starlette.config import Config

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = Path(BASE_DIR).parent

config = Config(Path(ROOT_DIR).joinpath(".env"))

logging.basicConfig(level=logging.INFO)

DEBUG = config("DEBUG", cast=bool, default=False)
