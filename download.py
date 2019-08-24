import re
import os
import time
import argparse

import requests
import urllib
from bs4 import BeautifulSoup
import tabulate

f_print = print


def errorExit(msg):
    f_print(msg)
    os.system("pause")
    exit()


def timeCvt(t):
    year, month, day = re.findall(r"([\w]+)\-([\w]+)-([\w]+)", t)[0]
    hour, minute = re.findall(r"([\w]+)\:([\w]+)", t)[0]
    year, month, day, hour, minute = [int(k) for k in (year, month, day, hour, minute)]
    if ("PM" in t) or ("pm" in t) or ("下午" in t):
        hour += 12
    return (year, month, day, hour, minute)


def today():
    return timeCvt(time.strftime("%Y-%m-%d %H:%M"))


def getSession(config_filename, confirm, semester):
    if 1:
        """ check semester """
        if len(semester) in [6, 7]:
            if not (semester[0:2].isdigit() and semester[2] == '-' and semester[3:5].isdigit() and semester[5] in '春夏秋'):
                f_print("学期格式不正确。正确示例: 18-19春，18-19春季")
                return
            if semester[-1] != '季':
                semester += '季'
        f_print('选择学期：[%s]' % (semester if semester else '所有'))

        """ Read username & password """
        try:
            config = open(config_filename, "rb")
        except IOError:
            errorExit("请创建user.txt文件")

        try:
            line = config.readline().decode("utf-8-sig").split()
            username = line[0]
            password = line[1]
            syncPath = line[2]
            studentId = "" if len(line) == 3 else line[3]
        except IndexError:
            errorExit("user.txt文件格式不正确啊")

        """ confirm """
        f_print("您的登录名为：" + username)
        flag = not confirm or input("是否继续？(y/n)").upper() == 'Y'
        if not flag:
            exit()
    if 1:
        session = requests.Session()
        s = session.get("http://sep.ucas.ac.cn/slogin?userName=" + username + "&pwd=" + password + "&sb=sb&rememberMe=1")
        bsObj = BeautifulSoup(s.text, "html.parser")
        nameTag = bsObj.find("li", {"class": "btnav-info", "title": "当前用户所在单位"})
        if nameTag is None:
            errorExit("登录失败，请核对用户名密码")
        name = nameTag.get_text()
        # 正则提取出 姓名 （单位还是提取不出来啊 不知道为啥）
        match = re.compile(r"\s*(\S*)\s*(\S*)\s*").match(name)
        f_print("\n")
        if(match):
            name = match.group(2)
            f_print("欢迎您," + name)
        else:
            errorExit("登录失败，请核对用户名密码重启软件")
        f_print(u"......................")
        f_print(u"获取信息中，稍安勿躁....")
        f_print(u"......................")

        # 课程网站
        s = session.get("http://sep.ucas.ac.cn/portal/site/16/801")
        bsObj = BeautifulSoup(s.text, "html.parser")
        if studentId == "":
            newUrl = bsObj.find("noscript").meta.get("content")[6:]
        else:
            newUrl = "http://course.ucas.ac.cn/portal?anotherUser=%s" % (studentId.lower())
            f_print("以学号%s身份登录" % (studentId))
            raise NotImplementedError
        s = session.get((newUrl))
        bsObj = BeautifulSoup(s.text, "html.parser")
        newUrl = bsObj.findAll(class_="Mrphs-toolsNav__menuitem--link ", title="我的课程 - 查看或加入站点")[0].get("href")

        s = session.get(newUrl)
        # 读取所有课程
        classList = []
        trList = BeautifulSoup(s.text, "html.parser").findAll("tr")
        # 去掉第一行
        del trList[0]
        for tr in trList:
            tdList = tr.findAll("td")
            className = tdList[0].find("input").get("title").lstrip("选择要退出的 ")
            if semester not in className:  # 筛选特定的学期
                continue
            if className[-len(semester):] == semester:
                className = className[:-len(semester)]
            classId = tdList[0].find("input").get("value")  # 课程id
            classWebsite = "http://course.ucas.ac.cn/portal/site/%s" % (classId)  # 课程url
            classTeacher = "教师未知"  # 课程老师
            classList.append((classId, className, classWebsite, classTeacher))
        f_print("您已选" + str(len(classList)) + "门课：")
        # 打印所有课程
        for c in classList:
            f_print(c[1] + "(" + c[3] + ")")
        return session, classList, syncPath


def download(url, fileName, className, session, ftype="file", dir=None, debug=False, newFilesList=[], depth=1):
    if depth == 1 and dir.rstrip("/")[-2:] != "课件":
        dir = dir + "/课件"
    if ftype == "folder":
        if not os.path.exists(dir):
            os.mkdir(dir)
        s = session.get(url)
        w = re.findall(r'<li class="(file|folder)"><a href="([^"]*)"', s.text)
        for sub_ftype, sub_fname in w:
            sub_fname = urllib.parse.unquote(sub_fname)  # 解码为中文
            sub_url = "/".join([url, sub_fname])
            sub_dir = dir if sub_ftype == "file" else "/".join([dir, sub_fname])
            updated = download(sub_url, sub_fname, className, session, ftype=sub_ftype, dir=sub_dir, newFilesList=newFilesList, depth=depth + 1, debug=debug)
            if updated and not type(updated) is bool:
                newFilesList.append("%s --> %s" % (className, updated))
        return True
    else:  # file
        file = dir.rstrip("/") + "/" + fileName
        # 没有课程文件夹则创建
        if not os.path.exists(dir):
            os.mkdir(dir)
        # 存在该文件，返回
        f_print("\t\t", "-" * 80)
        if os.path.exists(file):
            f_print("\t\t", "", fileName + "已存在，就不下载了")
            return False
        fname_display = file[dir.index(className):].lstrip("课件/" + className)
        f_print("\t\t", "☆", "开始下载", fname_display + u"...")

        if debug:
            # when debug == True, don't donwload
            with open(file, "wb") as data:
                data.write(bytes("Test Input".encode("utf-8")))
            return fname_display

        s = session.get(url)
        with open(file, "wb") as data:
            data.write(s.content)
        return fname_display


def downloadCourseware(session, classList, syncPath):
    newFilesList = []
    f_print("\n")
    f_print("开始下载课件......")
    for c in classList:
        f_print("\t", "正在下载课程：%s" % (c[1]))
        course_id = c[0]
        className = c[1].replace("\\", "/").replace("/", "-")

        url_2 = "http://course.ucas.ac.cn/access/content/group/%s" % (course_id)
        classPath = os.path.join(syncPath, className)
        if not os.path.exists(classPath):
            os.mkdir(classPath)
        download(url_2, "课件", className, session, ftype="folder", dir=classPath, newFilesList=newFilesList, debug=False)

    f_print("\n")
    f_print("本次更新文件：")
    if len(newFilesList) == 0:
        f_print("\t", "无")
    else:
        for msg in newFilesList:
            f_print("\t", msg)
    f_print()
    f_print("课件下好了，滚去学习吧！\n")


def scanHomework(session, classList):
    """ scan homework """
    f_print("\n")
    f_print("查找作业......")
    for c in classList[0:]:
        f_print("\t", "查看课程：%s" % (c[1]))
        url_main = c[2]
        s = session.get(url_main)
        courseToolNavs = BeautifulSoup(s.text, "html.parser").findAll(class_="Mrphs-toolsNav__menuitem--link ")
        # 作业发布页
        homeworkPage = [c for c in courseToolNavs if "在线发布、提交和批改作业" in c.get("title")][0].get("href")
        s = session.get(homeworkPage)
        rows = BeautifulSoup(s.text, "html.parser").findAll("div", class_="table-responsive")
        if not rows:
            continue
        rows = rows[0].findAll("tr")
        table = []
        for i, row in enumerate(rows[1:]):
            tds = row.findAll("td")
            homework = {}
            homework["Title"] = tds[1].find("a").get_text().strip()
            homework["Status"] = tds[2].get_text().replace("已提交", "Submitted").replace("上午", "AM ").replace("下午", "PM ").strip()
            homework["Open"] = tds[3].get_text().replace("上午", "AM ").replace("下午", "PM ").strip()
            homework["Due"] = tds[4].find("span").get_text().replace("上午", "AM ").replace("下午", "PM ").strip()
            homework["Tip"] = "Finished" if today() >= timeCvt(homework['Due']) else \
                "Submitted" if "Submitted" in homework["Status"] \
                else "Todo"
            table.append(homework)
        table.sort(key=lambda row: (timeCvt(row['Open']), timeCvt(row['Due'])))
        tabstr = "\t\t" + tabulate.tabulate(table, headers="keys", tablefmt="grid").replace("\n", "\n\t\t")
        f_print(tabstr)


def downloadHelper(config_filename, confirm=False, semester=""):
    f_print(u"=============================")
    f_print(u"    课件自动下载脚本 v1.0")
    f_print(u"=============================")
    session, classList, syncPath = getSession(config_filename, confirm, semester)
    downloadCourseware(session, classList, syncPath)


def homeworkHelper(config_filename, confirm=False, semester=""):
    f_print(u"=============================")
    f_print(u"    作业提示脚本 v1.0         ")
    f_print(u"=============================")
    """ check semester """
    if len(semester) in [6, 7]:
        if not (semester[0:2].isdigit() and semester[2] == '-' and semester[3:5].isdigit() and semester[5] in '春夏秋'):
            errorExit("学期格式不正确。正确示例: 18-19春，18-19春季")
        if semester[-1] != '季':
            semester += '季'

    session, classList, syncPath = getSession(config_filename, confirm, semester)
    scanHomework(session, classList)


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Settings')
    parser.add_argument('--homework', help='作业查看', action="store_true", default=False)
    parser.add_argument('--download', help='课件下载', action="store_true", default=False)
    parser.add_argument('-i', help='用户信息文件', default="./user.txt", type=str)
    parser.add_argument('-semester', help='学期，默认为所有', default="", type=str)
    parser.add_argument('--test', help='测试用', action="store_true", default=False)
    args = parser.parse_args()
    return args


def main(args):
    global f_print
    nrun = 0
    if args.test:
        f_print(today())
    if args.download:
        downloadHelper(config_filename=args.i, confirm=False, semester=args.semester)
        nrun += 1
    if args.homework:
        homeworkHelper(config_filename=args.i, confirm=False, semester=args.semester)
        nrun += 1
    if nrun == 0:
        f_print("No match options. Exit...")


if __name__ == "__main__":
    args = parse_args()
    main(args)
