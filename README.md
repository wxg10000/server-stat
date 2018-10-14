
server-stat 部署
=======

说明：
----
    
    eslog部署分为两部分：server_stat report
        
        server_stat:将服务器的状态信息收集，并发送至elasticsearch
        report：将elasticsearch 将昨天的服务器状态信息进行汇总，并以邮件的方式发送给人员

安装步骤：
--------

    1.安装elasticsearch
    
        安装过程：略
    
    2.安装anaconda 或者 安装python3
    
        方式一 安装anaconda
        
            wget -c https://repo.continuum.io/archive/Anaconda3-5.1.0-Linux-x86_64.sh
            chmod +x Anaconda3-5.1.0-Linux-x86_64.sh
            执行 Anaconda3-5.1.0-Linux-x86_64.sh
            更改安装路径
        
        方式二 安装python3 及相关包
        
            apt install python3-pip
            pip3 install elasticsearch
            pip3 install psutil demjson


部署:
-----
    
  
    1.pip安装Elasticsearch，schedule，MIMEText，demjson
    
    2.启动脚本 start_server_stat.sh
    
       
        #!/bin/sh
        /data/stat/anaconda3/bin/python ./server_stat.py eslog 10.20.1.21  &
        ##将&去掉也可以用supervisor监控进程

    3. start_report.sh
    
        
        #!/bin/sh
        cd /data/stat
        /data/stat/anaconda3/bin/python ./report.py >>log/report.log
        echo "ok"
        
    4. docker 容器中部署
        apt-get install cron
        crontab -e  添加0 9 * * * /usr/bin/python3 /data/stat/report.py >> /data/stat/logs/report.log
        

监控进程：
--------
    运用supervisor监控运行
