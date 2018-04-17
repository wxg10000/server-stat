#!/bin/bash
proc="server_stat"
pid=`ps -ef|grep $proc |grep -v grep |awk 'NR==1{print $2}'`
py=`ps -ef|grep $proc |grep -v grep |awk 'NR==1{print $8}'`
datestamp=$(date +%m-%d-%H:%M)

#if [ -n "$pid" ]; then
if [ ${py} == '/data/stat/anaconda3/bin/python' ];then
        echo "$datestamp $proc ok, pid=${pid}"
else
        echo "$datestamp $proc not found, try restart"
        sleep 1
        cd /data/stat && ./start_server_stat.sh
fi
