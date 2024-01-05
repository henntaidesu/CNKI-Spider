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

    def cnki_skip_db(self):
        newpaper = self.config.get('cnki skip jump', '报纸')
        journal = self.config.get('cnki skip jump', '期刊')
        journal_A = self.config.get('cnki skip jump', '特色期刊')
        master = self.config.get('cnki skip jump', '硕士')
        PhD = self.config.get('cnki skip jump', '博士')

        if newpaper == "True":
            newpaper = True
        else:
            newpaper = False

        if journal == "True":
            journal = True
        else:
            journal = False

        if journal_A == "True":
            journal_A = True
        else:
            journal_A = False

        if master == "True":
            master = True
        else:
            master = False

        if PhD == "True":
            PhD = True
        else:
            PhD = False

        return [newpaper, journal, master, PhD]


class CNKI:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini', encoding='utf-8')

    def read_cnki_date(self):
        year = int(self.config.get('cnki date', 'year'))
        moon = int(self.config.get('cnki date', 'moon'))
        day = int(self.config.get('cnki date', 'day'))
        return year, moon, day

    def write_cnki_date(self, year, moon, day):
        self.config.set('cnki date', 'year', year)
        self.config.set('cnki date', 'moon', moon)
        self.config.set('cnki date', 'day', day)
        with open('conf.ini', 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)

