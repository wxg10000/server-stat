# _*_ coding: utf-8 _*_
import datetime

import os
from elasticsearch import Elasticsearch
import psutil
import sys
import time
import logging

logging.basicConfig(filename='log/server_stat.log',filemode="w",level=logging.INFO)
def getTime():
    time_point = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')
    # 转换成时间数组
    timeArray = time.strptime(time_point, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    stamp = time.mktime(timeArray)
    return time_point,stamp


def getArgs():
    host = sys.argv[1]
    ip = sys.argv[2]
    return host,ip

def getBW():
    ## 计算带宽
    bys = psutil.net_io_counters()
    bw = round(bys.bytes_recv*8/1024/1024/1024,2)
    return bw

def publish():
    #_es = Elasticsearch(['http://10.20.1.21:9200'],chunk_size=1000,timeout=30)
    _es = Elasticsearch(['http://eslog.datahunter.cn:80'], http_auth=('eslog', 'DataHunter8'), chunk_size=1000,timeout=30)

    while (True):
        # cpu均值
        cpu = psutil.cpu_percent(interval=60)
        # cpu物理数
        cpu_count = psutil.cpu_count(logical=True)
        # 内存使用率
        vm = psutil.virtual_memory()
        mem = vm.percent
        # 磁盘使用率
        d = psutil.disk_usage('/')
        disk = d.percent
        # data磁盘使用率
        da = psutil.disk_usage('/data')
        disk_data = da.percent
        time_point, stamp = getTime()
        bw = getBW()
        host, ip = getArgs()
        now = datetime.datetime.now()
        flag = _es.index(
            index="server_stat", doc_type="server_stat",
            body={
                "time_point": now,
                "stamp": stamp,
                "cpu": cpu,
                "cpu_count": cpu_count,
                "mem": mem,
                "disk": disk,
                "disk_data": disk_data,
                "bw": bw,
                "host": host,
                "ip": ip
            }
        )
        if flag:
            logging.info(str(now) + " 发布成功！")
        else:
            logging.DEBUG(str(now) + " 发布失败！")

if __name__ == '__main__':
    publish()

