import sys
import time
import os
import re
import concurrent.futures
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from src.module.execution_db import Date_base
from src.module.UUID import UUID
from src.module.now_time import now_time
from src.model.cnki import Crawl, positioned_element, crawl_xpath, reference_papers, QuotePaper
from src.module.log import log
from src.module.read_conf import read_conf
from src.module.err_message import err
from src.module.read_conf import CNKI
import random

open_page_data = positioned_element()
crawl_xp = Crawl()
logger = log()
read_conf = read_conf()


def TrimString(Str):
    if '\n' in Str:
        Str = Str.replace('\n', ' ')
    # if ' ' in Str:
    #     Str = Str.replace(' ', '')
    # if '/' in Str:
    #     Str = Str.replace('/', ' ')
    if "'" in Str:
        Str = Str.replace("'", "\\'")
    if '"' in Str:
        Str = Str.replace('"', '\\"')
    return Str


def Trim_passkey(Str):
    Str = Str.replace(";", " ")
    return Str


def trim_quote(Str):
    Str = str(Str)
    Str = Str.replace(',', '').replace("'", "").replace('] ', '、')
    Str = Str.replace(' ', '')[2:][:-1]
    return Str


def extract_number(item):
    match = re.search(r"(\d+)\]", item)
    return int(match.group(1)) if match else float('inf')


def TrSQL(sql):
    sql = sql.replace("None", "NULL").replace("'NULL'", "NULL")
    return sql


def get_info(driver, xpath):
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element.text
    except:
        return None


def is_english_string(s):
    # 使用正则表达式判断字符串是否全为英文字符
    return bool(re.match('^[a-zA-Z\s.,;:!?\'"()]+$', s))


def get_choose_info(driver, xpath1, xpath2, str):
    try:
        if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath1))).text == str:
            return WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath2))).text
        else:
            return None
    except:
        return None


def is_leap_year(year):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    else:
        return False


def revise_cnki_date():
    cnki = CNKI()
    yy, mm, dd = cnki.read_cnki_date()
    dd -= 1
    if dd == 0:
        mm -= 1
        if mm in {1, 3, 5, 7, 8, 10, 12}:
            dd = 31
        elif mm == 2:
            if (yy % 4 == 0 and yy % 100 != 0) or (yy % 400 == 0):
                dd = 29
            else:
                dd = 28
        elif mm == 0:
            yy -= 1
            mm = 12
            dd = 31
        else:
            dd = 30

    cnki.write_cnki_date(str(yy), str(mm), str(dd))
    return True


def get_paper_title(driver, keyword, time_out, res_unm, date, paper_type, paper_day, date_str, paper_sum):
    title = None
    db_type = None
    authors = None
    source = None
    aa = None

    paper_db = read_conf.cnki_skip_db()
    cp = crawl_xpath()
    rp = reference_papers()
    qp = QuotePaper()

    count = 1
    new_paper_sum = 0

    xpath_information = crawl_xp.xpath_inf()
    sql = f"SELECT title FROM cnki_index where receive_time >= '{date} 00:00:00' and receive_time <= '{date} 23:59:59'"
    flag, paper_title = Date_base().select_all(sql)

    if res_unm > 6000:
        res_unm = 6000 - paper_sum

    # 当爬取数量小于需求时，循环网页页码
    while True:
        # 等待加载完全，休眠3S
        time.sleep(3)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        try:
            title_list = WebDriverWait(driver, time_out).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
        except:
            try:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(15)
                title_list = WebDriverWait(driver, time_out).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
            except:
                return True

        # 循环网页一页中的条目
        for i in range((count - 1) % paper_sum + 1, paper_sum + 1):

            if res_unm < count:
                logger.write_log("已获取完数据")

                date_str = list(date_str)
                date_str[paper_type] = '1'
                date_str = str(date_str)
                date_str = date_str[1:][:-1].replace(',', '').replace("'", "").replace(" ", "")

                sql = f"UPDATE `Paper`.`cnki_page_flag` SET `flag` = '{date_str}' WHERE `date` = '{paper_day}'"
                Date_base().update_all(sql)
                if date_str == '111100000':
                    flag = revise_cnki_date()

                if flag is True:
                    return True

            print(f"正在爬取第{count - new_paper_sum}条基础数据,跳过{new_paper_sum}"
                  f"条(第{(count - 1) // paper_sum + 1}页第{i}条 总第{count}条 共{res_unm}条):")

            try:
                term = (count - 1) % paper_sum + 1  # 本页的第几个条目
                xpaths = crawl_xp.xpath_base(term)

                if paper_type == 0:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
                    title, authors, source, date, quote, down_sun, aa = [future.result() for future in
                                                                         future_elements]

                elif paper_type == 1:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
                    title, authors, source, db_type, date, quote, down_sun = [future.result() for future in
                                                                              future_elements]
                    date = f"{date}-01-01"

                elif paper_type == 2:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
                    title, authors, source, db_type, date, quote, down_sun = [future.result() for future in
                                                                              future_elements]
                elif paper_type == 3:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
                    title, authors, source, date, quote, down_sun, aa = [future.result() for future in future_elements]


                if '增强出版' in title:
                    title = title[:-5]

                if '网络首发' in title:
                    title = title[:-5]

                if_title = None
                for ii in paper_title:
                    if ii[0] == title:
                        print(f"数据已存在 : {title}")
                        if_title = True
                        break

                if if_title is True:
                    new_paper_sum += 1
                    if i == 50:
                        time.sleep(3)
                    continue

                # 期刊
                if paper_type == 0:
                    db_type = '1'
                # 报纸
                elif paper_type == 3:
                    db_type = '0'

                elif db_type == '硕士':
                    db_type = '2'

                elif db_type == '博士':
                    db_type = '3'

                elif db_type == '图书':
                    db_type = '4'

                elif db_type == '中国会议':
                    db_type = 'a'
                elif db_type == '国际会议':
                    db_type = 'b'

                elif db_type == '国家标准':
                    db_type = 'c'
                elif db_type == '国家标准':
                    db_type = 'd'

                else:
                    db_type = '9'

                uuid = UUID()
                sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
                        f"(`UUID`, `title`, `receive_time`, `start`, `db_type`) "
                        f"VALUES ('{uuid}', '{title}', '{date}', '0', '{db_type}');")

                sql3 = TrSQL(sql3)
                flag = Date_base().insert_all(sql3)
                if flag == '重复数据':
                    logger.write_log(f"重复数据 ： {title}, UUID : {uuid}")
                    continue

                if not quote.isdigit():
                    quote = '0'
                if not down_sun.isdigit():
                    down_sun = '0'

                print(f"\n"
                      f"标题:    {title}\n"
                      f"作者:    {authors}\n"
                      f"文章来源: {source}\n"
                      f"数据来源: {db_type}\n"
                      f"引用次数: {quote}\n"
                      f"下载次数: {down_sun}\n")

                logger.write_log(f"已获取 ： {title}, UUID : {uuid}")

            except Exception as e:
                err(e)
                continue

            finally:
                count += 1
            continue_flag = False
            # time.sleep(1)

        time.sleep(3)
        # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.HOME)
        WebDriverWait(driver, time_out).until(EC.presence_of_element_located((By.XPATH, cp['paper_next_page']))).click()


def get_paper_info(driver, keyword, time_out, uuid, title1, db_type, receive_time, start, dbt):
    paper_db = read_conf.cnki_skip_db()

    cp = crawl_xpath()
    rp = reference_papers()
    qp = QuotePaper()

    count = 1
    xpath_information = crawl_xp.xpath_inf()

    new_paper_sum = 0

    # 等待加载完全，休眠3S
    time.sleep(3)

    title_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "fz14")))
    # 循环网页一页中的条目

    for i in range((count - 1) % 20 + 1, 21):

        term = (count - 1) % 20 + 1  # 本页的第几个条目
        xpaths = crawl_xp.xpath_base(term)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_elements = [executor.submit(get_info, driver, xpath) for xpath in xpaths]
        title, authors, source, date, ndb_type, quote, down_sun = [future.result() for future in future_elements]

        if '增强出版' in title:
            title = title[:-5]
        if '网络首发' in title:
            title = title[:-5]

        if db_type == '期刊':
            db_type = '1'
        elif db_type == '报纸':
            db_type = '0'
        elif db_type == '硕士':
            db_type = '2'
        elif db_type == '博士':
            db_type = '3'
        elif db_type == '图书':
            db_type = '4'
        elif db_type == '特色期刊':
            db_type = '5'
        elif db_type == '刊辑':
            db_type = '6'
        elif db_type == '中国会议':
            db_type = 'a'
        elif db_type == '国际会议':
            db_type = 'b'
        elif db_type == '国家标准':
            db_type = 'c'
        elif db_type == '国家标准':
            db_type = 'd'
        else:
            db_type = '9'

        sql3_flag = False
        if title == title1:
            sql3_flag = True


        try:
            term = (count - 1) % 20 + 1  # 本页的第几个条目
            xpaths = crawl_xp.xpath_base(term)

            # 点击条目
            title_list[i - 1].click()

            # 获取driver的句柄
            n = driver.window_handles

            # driver切换至最新生产的页面
            driver.switch_to.window(n[-1])
            time.sleep(3)

            # 拉取页面到最低端
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

            # 开始获取页面信息
            # 点击展开
            try:
                WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.XPATH, cp['WebDriverWait']))
                ).click()
            except:
                pass

            # 获取作者单位
            # print('正在获取作者单位')
            try:
                institute = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                    (By.XPATH, cp['institute']))).text
                if '.' in institute:
                    institute = re.sub(r'\d*\.', ';', institute)[1:].replace(' ', '')
            except:
                institute = None
            print(f"作者单位 : {institute}")

            # print('正在获取摘要')
            try:
                abstract = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.CLASS_NAME, cp['abstract']))).text
            except:
                abstract = None
                driver.refresh()
            print(f"摘要 : {abstract}")

            # 获取关键词
            # print('获取关键词')
            try:
                classification_zh = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.CLASS_NAME, cp['keywords']))).text[:-1]
                classification_zh = Trim_passkey(classification_zh).replace('  ', ';')
            except:
                classification_zh = None
                # print("无法获取关键词")

            print(f"关键词 : {classification_zh}")

            # 获取专辑
            # print('获取专辑')
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '专辑：') for xpath1, xpath2 in
                           xpath_information]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            publication = next((result for result in results if result is not None), None)
            if publication is None:
                logger.write_log(f"获取专辑错误 ： {title}")
            print(f"专辑 : {publication}")

            # 获取专题
            # print('获取专题')
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '专题：') for xpath1, xpath2 in
                           xpath_information]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            topic = next((result for result in results if result is not None), None)
            print(f"专题 : {topic}")

            # 拉取页面到最低端
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

            # 获取分类号 版名
            # print('获取分类号')
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '分类号：') for xpath1, xpath2 in
                           xpath_information]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            classification_number = next((result for result in results if result is not None), None)
            if classification_number is None:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '版名：') for xpath1, xpath2
                               in
                               xpath_information]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                classification_number = next((result for result in results if result is not None), None)
                # 获取版号
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, '版号：') for xpath1, xpath2
                               in
                               xpath_information]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                number = next((result for result in results if result is not None), None)
                if classification_number:
                    classification_number = f"{classification_number}-{number}"
                else:
                    classification_number = number
            if classification_number is None:
                logger.write_log(f"获取分类号错误 ： {title}")
            print(f"分类号 : {classification_number}")

            # 获取DOI
            # print('获取DOI')
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(get_choose_info, driver, xpath1, xpath2, 'DOI：') for xpath1, xpath2 in
                           xpath_information]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            DOI = next((result for result in results if result is not None), None)
            # if DOI is None:
            #     logger.write_log(f"DOI ： {title}")
            print(f"DOI: {DOI}")

            # 获取资金资助
            # print('获取资金资助')
            try:
                funding = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.CLASS_NAME, cp['funds']))).text
                funding = funding.replace(' ', '').replace('；', ';')
            except:
                funding = None
            print(f"资金资助 : {funding}")

            # print('获取论文大小')
            paper_size_flag = 0
            while True:
                paper_size_flag += 1
                paper_size = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                    (By.XPATH, cp[f'paper_size{paper_size_flag}']))).text
                if '大小' in paper_size:
                    paper_size = int(paper_size[3:][:-1])
                    break
                if paper_size_flag > 8:
                    paper_size = None
                    break
            print(f"论文大小 : {paper_size}k")

            # print('获取论文页数')
            paper_page_flag = 0
            while True:
                paper_page_flag += 1
                page_sum = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                    (By.XPATH, cp[f'paper_size{paper_page_flag}']))).text
                if '页数' in page_sum:
                    page_sum = int(page_sum[3:])
                    break
                if paper_page_flag > 8:
                    page_sum = None
                    break
            print(f"论文页数 : {page_sum}")

            level = None
            if '报' in db_type or '报纸' in db_type:
                try:
                    level = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                        (By.XPATH, cp['level']))).text
                    # paper_size = int(paper_size[3:][:-1])
                except:
                    level = None
            print(f"报纸层级 : {level}")

            # 拉取页面到最低端
            # driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

            # 判断是否有参考文献
            rn = qp.reference_name()
            pl_list = qp.paper_list()
            journal_reference = None
            try:
                if_journal_reference = WebDriverWait(driver, time_out).until(EC.presence_of_element_located(
                    (By.XPATH, cp['if_literature_reference']))).text
                if if_journal_reference:
                    print("存在引文网络")

            except:
                if_journal_reference = None
                print("该论文无引用文章")

            # if_journal_reference = None
            if if_journal_reference == '引文网络':
                el = WebDriverWait(driver, time_out).until(EC.element_to_be_clickable((By.XPATH, cp['references'])))
                el.click()
                paper_flag = 0

                while True:
                    if paper_flag == len(pl_list):
                        break
                    paper_list = None
                    continue_flag = False
                    # 期刊参考文件页数
                    try:
                        paper_sum = WebDriverWait(driver, time_out).until(
                            EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                        paper_sum = int(paper_sum.find_element(By.ID, 'pc_JOURNAL').text)
                    except:
                        paper_sum = None
                        paper_flag += 1
                        continue_flag = True
                    if continue_flag is True:
                        try:
                            # print(f"$$$本论文没有引用{rn[paper_flag]} Paper$$$")
                            continue
                        except:
                            break

                    if paper_sum:
                        print(f"存在引用{rn[paper_flag]} {paper_sum} 篇")
                        journal_paper_sum = int((paper_sum / 10) + 1)
                        flag = 0
                        paper_list = []
                        while True:
                            # 获取参考文献

                            li_elements = WebDriverWait(driver, time_out).until(
                                EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                            li_elements = li_elements.find_elements(By.TAG_NAME, 'li')

                            for li in li_elements:
                                li_text = li.text.replace('[', ';', 1)
                                paper_list.append(li_text)

                            flag += 1
                            if flag > paper_sum:
                                break

                            try:
                                if_next_page = WebDriverWait(driver, time_out).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                                if_next_page = if_next_page.find_element(By.CLASS_NAME, 'next').text
                            except:
                                break
                            if if_next_page == '下一页':
                                el = WebDriverWait(driver, time_out).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, rp[rn[paper_flag]])))
                                # 滚动到元素可见位置
                                next_button = el.find_element(By.CLASS_NAME, 'next')
                                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                                # 然后点击元素
                                next_button.click()
                                time.sleep(3)

                        for iii in paper_list:
                            print(f"[{iii[1:]}")

                    paper_list = trim_quote(paper_list)
                    pl_list[paper_flag] = paper_list
                    paper_flag += 1

            # print("获取文章目录")
            try:
                article_directory = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.CLASS_NAME, cp['catalog']))).text
                print(f"文章目录 : \n{article_directory}")
            except:
                article_directory = None
                print(f"文章目录 : {article_directory}")

            # url = driver.current_url[46:][:-32]
            # 获取下载链接
            # try:
            #     down_url = WebDriverWait(driver, 0).until(EC.presence_of_all_elements_located
            #                                               ((By.CLASS_NAME, "btn-dlpdf")))[0].get_attribute('href')
            #     down_url = urljoin(driver.current_url, down_url)
            # except:
            #     down_url = None

            # print("获取内页标题")
            try:
                new_title = WebDriverWait(driver, time_out).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
                new_title = new_title.text
            except:
                new_title = None
            print(f"内页标题 : {new_title}")

            insert_time = now_time()

            title_en = None
            classification_en = None
            update_time = now_time()

            if sql3_flag is True:
                sql3 = (f"UPDATE `Paper`.`cnki_index` SET "
                        f"`receive_time` = '{date}', "
                        f"`start` = '1', "
                        f"`db_type` = '{db_type}' "
                        f"WHERE `UUID` = '{uuid}';")
            else:
                uuid = UUID()
                sql3 = (f"INSERT INTO `Paper`.`cnki_index`"
                        f"(`UUID`, `title`, `receive_time`, `start`, `db_type`) "
                        f"VALUES ('{uuid}', '{title}', '{date}', '1', '{db_type}');")

            sql1 = (
                f"INSERT INTO `Paper`.`index`(`UUID`, `web_site_id`, `classification_en`,`classification_zh`,"
                f"`source_language`, `title_zh`, `title_en`, `update_time`, `insert_time`, `from`, `state`, "
                f"`authors`, `Introduction`, `receive_time`, `Journal_reference`, `Comments`, `size`, `DOI`, "
                f"`version`, `withdrawn`) "
                f" VALUES ('{uuid}', '{uuid}', '{classification_en}', '{classification_zh}', "
                f" 'cn', '{new_title}', '{title_en}', '{update_time}', '{insert_time}', 'cnki', '00', "
                f" '{authors}', NULL, '{date}', NULL, NULL, {paper_size}, '{DOI}', NULL, NULL);")

            sql2 = (f"INSERT INTO `Paper`.`cnki_paper_information`"
                    f"(`UUID`, `institute`, `paper_from`, `db_type`, `down_sun`, `quote`, `insert_time`, "
                    f"`update_time`, `funding`, `album`, `classification_number`, "
                    f"`article_directory`, `Topics`, `level`, `page_sum`, `journal`, "
                    f"`master`, `PhD`, `international_journals`, `book`, "
                    f"`Chinese_and_foreign`, `newpaper`) "
                    f"VALUES "
                    f"('{uuid}', '{institute}', '{source}', '{db_type}',' {down_sun}', '{quote}', '{insert_time}',"
                    f" '{update_time}', '{funding}', '{publication}', '{classification_number}',"
                    f" '{article_directory}', '{topic}', '{level}', '{page_sum}', '{pl_list[0]}',"
                    f" '{pl_list[1]}', '{pl_list[2]}', '{pl_list[3]}', '{pl_list[4]}',"
                    f" '{pl_list[5]}', '{pl_list[6]}');")

            sql1 = TrSQL(sql1)
            sql2 = TrSQL(sql2)
            sql3 = TrSQL(sql3)

            Date_base().insert_all(sql1)
            Date_base().insert_all(sql2)
            Date_base().update_all(sql3)

            logger.write_log(f"已获取 ： {new_title}, UUID : {uuid}")
            break


        except Exception as e:
            logger.write_log(f"错误 ： {new_title}, UUID : {uuid}")
            err(e)
