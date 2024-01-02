from src.paper_website.cnki.run_cnki import run_paper_main_info, run_lever2_page
import asyncio


class index:

    @staticmethod
    def index():
        flag = '6'
        if flag == '1':
            print("获取cnki论文基础数据")
            run_paper_main_info(0)

        if flag == '2':
            print("获取cnki论文详细数据")
            run_lever2_page()

