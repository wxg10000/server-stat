# _*_ coding: utf-8 _*_
import datetime
from elasticsearch import Elasticsearch
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import time
import os
import demjson

es = Elasticsearch(['http://10.20.1.21:9200'],chunk_size=1000,timeout=30)


mailInfo = {
        "from": "es-log<support@***.cn>",
        "to": "***@***.cn",
        "hostname": "smtp.exmail.qq.com",
        "username": "*******",
        "password": "*******",
        "mailencoding": "utf-8"
    }
class Report(object):
    def __init__(self):
        print("------------report-------------")
    def sendsmtp(self,sub,html):
        try:
            smtp = smtplib.SMTP(mailInfo["hostname"], 25)
            smtp.set_debuglevel(1)
            smtp.ehlo(mailInfo["hostname"])
            smtp.login(mailInfo["username"], mailInfo["password"])
            msg = MIMEText(html, "html", mailInfo["mailencoding"])
            msg["Subject"] = Header(sub, mailInfo["mailencoding"])
            msg["from"] = mailInfo["from"]
            msg["to"] = mailInfo["to"]
            smtp.sendmail(mailInfo["from"], mailInfo["to"].split(','), msg.as_string())
            smtp.quit()
            return True
        except Exception:
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
        cmd = "curl -XPOST http://10.20.1.21:9200/_sql -d " \
              "'select host,max(cpu),avg(cpu),avg(mem),avg(disk),avg(disk_data),max(bw),avg(cpu_count) from server_stat where stamp>=" + str(
            yesterday) + " and stamp<" + str(today) + "group by host order by avg(disk)'" \
                                                      " -H 'Content-Type:application/json'"

        result = self.execCmd(cmd)
        text = demjson.decode(result)
        buckets = text['aggregations']['host']['buckets']

        d = ''  # 表格内容
        for i in range(len(buckets)):
            host = buckets[i]['key']
            avg_disk = round(buckets[i]['AVG(disk)']['value'], 2)
            avg_disk_data = round(buckets[i]['AVG(disk_data)']['value'], 2)
            max_bw = round(buckets[i]['MAX(bw)']['value'], 2)
            avg_mem = round(buckets[i]['AVG(mem)']['value'], 2)
            avg_cpu = round(buckets[i]['AVG(cpu)']['value'], 2)
            max_cpu = round(buckets[i]['MAX(cpu)']['value'], 2)
            cpu_count = int(buckets[i]['AVG(cpu_count)']['value'])
            #print(host, avg_cpu, avg_disk, avg_disk_data, max_bw, max_cpu, avg_mem, cpu_count)

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
        html = """\
            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            <html>   
            <body>
                 <div id="container">
                    <p><strong>汇报服务器监测信息:</strong></p>
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
            print(now, "发送成功")
            break
        else:
            now = datetime.datetime.now()
            if n<3:
                print(now, "第%d次发送失败，5分钟后重试一次" % n)
            else:
                print(now,"3次重试发送失败，停止发送！")
            time.sleep(300)
            n = n+1







