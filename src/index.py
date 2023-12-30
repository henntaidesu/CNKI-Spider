from src.module.log import log
from src.paper_website.cnki.cnki import cnki_run
import asyncio


class index:

    def __init__(self):
        self.logger = log()

    @staticmethod
    def index():
        cnki_run(0)
