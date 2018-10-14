# _*_ coding: utf-8 _*_
import datetime
from elasticsearch import Elasticsearch
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import time
import os
import demjson
import urllib.request
import json

es = Elasticsearch(['http://eslog.datahunter.cn:80'],http_auth=('eslog','DataHunter8'),chunk_size=1000,timeout=30)


mailInfo = {
        "from": "DataHunter<support@datahunter.cn>",
        #"to": "sunhui@datahunter.cn,make@datahunter.cn,nick.cheng@datahunter.cn,dengjialong@datahunter.cn,wangxiangui@datahunter.cn",
        "to": "wangxiangui@datahunter.cn",
        "hostname": "smtp.exmail.qq.com",
        "username": "support@datahunter.cn",
        "password": "6Y5ce9UT5FGD8bch",
        "mailencoding": "utf-8"
    }

# 获取服务器平台余额
def getAcount():
    try:
        url = "https://api.ucloud.cn/?Action=GetBalance&PublicKey=ucloudsupport%40mrocker.com1392263197892193080&Signature=f138c4830cfce5ff00405167e4aabc8c235491ca"
        data = urllib.request.urlopen(url).read()
        account = (json.loads(data))['AccountInfo']['Amount']
        return account
    except Exception as e:
        print(e)
        return -1


# timestamp转时间格式
def stampToStr(timestamp):
    # timestamp = 1462451334
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt

def firewall():
    try:
        firewall = "https://api.ucloud.cn/?Action=DescribeSecurityGroup&PublicKey=ucloudsupport%40mrocker.com1392263197892193080&Region=cn-north-03&Signature=83fe5ad712dee325c3c7bd8ddf8e8fe145529936"
        data = urllib.request.urlopen(firewall).read()
        print(data)
        js = json.loads(data)
        dataSet = js["DataSet"]
        dataSet.sort(key=lambda x: x["CreateTime"])
        f = ""
        for i in range(len(dataSet)):
            createTime = dataSet[i]["CreateTime"]
            firewallId = dataSet[i]["FirewallId"]
            time_point = stampToStr(int(createTime))
            Rule = dataSet[i]["Rule"]
            ports = ""
            for j in range(len(Rule)):
                port = Rule[j]["DstPort"]
                ports = ports + ";" + port
            print(time_point, firewallId, ports[1:])

            f = f + """
                            <tr>
                                <td width="100">""" + time_point + """</td>
                                <td width="100">""" + firewallId + """</td>
                                <td width="100">""" + ports[1:] + """</td>

                            </tr>"""

        return f
    except Exception as e:
        print(e)
        return ""



class Report(object):
    def __init__(self):
        print("------------report-------------")

    def sendsmtp(self,sub,html):
        try:

            smtp = smtplib.SMTP_SSL(mailInfo["hostname"], 465)
            smtp.ehlo()
            smtp.login(mailInfo["username"], mailInfo["password"])
            msg = MIMEText(html, "html", mailInfo["mailencoding"])
            msg["Subject"] = Header(sub, mailInfo["mailencoding"])
            msg["from"] = mailInfo["from"]
            msg["to"] = mailInfo["to"]
            smtp.sendmail(mailInfo["from"], mailInfo["to"].split(','), msg.as_string())
            smtp.quit()
            return True
        except Exception as e:
            print(e)
            return False

    #获取昨天和今天的时间戳值

    def getStamp(self,args):
        str = args.strftime('%Y-%m-%d 00:00:00')
        # 转换成时间数组
        timeArray = time.strptime(str, "%Y-%m-%d %H:%M:%S")
        # 转换成时间戳
        stamp = time.mktime(timeArray)
        return stamp

    def getStamps(self):
        today = datetime.date.today()
        stamp1 = self.getStamp(today)
        yesterday = today - datetime.timedelta(days=1)
        stamp2 = self.getStamp(yesterday)
        return stamp1,stamp2


    def makeSub(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        sub = str(yesterday)+" 服务器监测信息"
        return sub

    def execCmd(self,cmd):
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text

    def sendEmail(self):
        today, yesterday = self.getStamps()
        cmd = 'curl -u eslog:DataHunter8 -X POST "http://eslog.datahunter.cn/_xpack/sql?format=json" -H \'Content-Type: application/json\' -d\' {"query": "select host,max(cpu),avg(cpu),avg(mem),avg(disk),avg(disk_data),max(bw),avg(cpu_count) from server_stat  where stamp>=\'' + str(
            yesterday) + '\' and stamp<\'' + str(today) + '\' group by host "}\''
        print(cmd)
        result = self.execCmd(cmd)
        # print(result)
        text = demjson.decode(result)
        print(text)
        buckets = text['rows']

        accout = getAcount()

        d = ''  # 表格内容
        f = ''
        for i in range(len(buckets)):
            host = buckets[i][0]
            max_cpu = round(buckets[i][1], 2)
            avg_cpu = round(buckets[i][2], 2)
            avg_mem = round(buckets[i][3], 2)
            avg_disk = round(buckets[i][4], 2)
            avg_disk_data = round(buckets[i][5], 2)
            max_bw = round(buckets[i][6], 2)
            cpu_count = int(buckets[i][7])
            print(host, avg_cpu, avg_disk, avg_disk_data, max_bw, max_cpu, avg_mem, cpu_count)

            color1 = 'black'
            color2 = 'black'
            if avg_disk >= 60:
                color1 = 'red'
            if avg_disk_data >= 60:
                color2 = 'red'

            d = d + """
                     <tr>
                        <td>""" + str(host) + """</td>
                        <td>""" + str(max_cpu) + """</td>
                        <td width="100">""" + str(avg_cpu) + """</td>
                        <td width="100">""" + str(avg_mem) + """</td>
                        <td width="100"><font color = """ + color1 + ">""" + str(avg_disk) + """</font></td>
                        <td width="100"><font color = """ + color2 + ">""" + str(avg_disk_data) + """</font></td>
                        <td width="100">""" + str(max_bw) + """</td>
                        <td width="100">""" + str(cpu_count) + """</td>
                    </tr>"""

        f = f + """
                <tr>
                    <td width="100">""" + str(accout) + """</td>
                    <td width="100">""" + str("") + """</td>
                </tr>"""

        html = """\
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            <html>
            <body>
                 <div id="container">
                    <p><strong>服务器状态信息:</strong></p>
                    <div id="content">
                        <table width="800" border="2" bordercolor="black" cellspacing="0" cellpadding="0">
                            <tr>
                              <td width="100" align="center"><strong>服务器</strong></td>
                              <td width="100" align="center"><strong>CPU峰值(%)</strong></td>
                              <td width="100" align="center"><strong>CPU均值(%)</strong></td>
                              <td width="100" align="center"><strong>内存使用(%)</strong></td>
                              <td width="100" align="center"><strong>磁盘使用(%)</strong></td>
                              <td width="100" align="center"><strong>data使用(%)</strong></td>
                              <td width="100" align="center"><strong>带宽Gbps</strong></td>
                              <td width="100" align="center"><strong>CPU数量</strong></td>
                            </tr>""" + d + """
                        </table>
                    </div>
                    <p><strong>服务器平台余额信息:</strong></p>
                    <div id="content">
                        <table width="800" border="2" bordercolor="black" cellspacing="0" cellpadding="0">
                            <tr>
                              <td width="100" align="center"><strong>ucloud平台(元)</strong></td>
                              <td width="100" align="center"><strong>ali平台(元)</strong></td>
                            </tr>""" + f + """
                        </table>
                    </div>
                    <p><strong>服务器防火墙监测信息:</strong></p>
                    <div id="content">
                        <table width="800" border="2" bordercolor="black" cellspacing="0" cellpadding="0">
                            <tr>
                              <td width="200" align="center"><strong>创建时间</strong></td>
                              <td width="200" align="center"><strong>防火墙ID</strong></td>
                              <td width="400" align="center"><strong>端口</strong></td>
                            </tr>""" + firewall() + """
                        </table>
                    </div>
                </div>
            </body>
            </html>
                         """

        sub = self.makeSub()
        if self.sendsmtp(sub,html):
            return True
        else:
            return False


if __name__ == '__main__':
    report = Report()
    n = 1
    while n <= 3:
        if report.sendEmail():
            now = datetime.datetime.now()
            print(now, "success")
            break
        else:
            now = datetime.datetime.now()
            if n<3:
                print(now, "The %d times send failed，5 minutes later try again" % n)
            else:
                print(now,"3 retry send failed,stop sending！")
            time.sleep(300)
            n = n+1
