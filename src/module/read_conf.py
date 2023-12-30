import pymysql
import configparser


class read_conf:
    config = None

    def __init__(self):
        # 如果配置信息尚未加载，则加载配置文件
        if not read_conf.config:
            read_conf.config = self._load_config()

    def _load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini', encoding='utf-8')
        return self.config

    def database(self):
        host = self.config.get('database', 'host')
        port = self.config.get('database', 'port')
        port = int(port)
        user = self.config.get('database', 'user')
        password = self.config.get('database', 'password')
        data_base = self.config.get('database', 'database')
        db = pymysql.connect(host=host, port=port, user=user, password=password, database=data_base)
        return db

    def log_level(self):
        level = self.config.get('LogLevel', 'level')
        return level

    def cnki_paper(self):
        web_zoom = self.config.get('cnki paper passkey', 'web_zoom')
        keyword = self.config.get('cnki paper passkey', 'keyword')
        papers_need = int(self.config.get('cnki paper passkey', 'papers_need'))
        return web_zoom, keyword, papers_need

