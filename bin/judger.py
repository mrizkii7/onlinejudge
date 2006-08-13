#!/usr/bin/python

import socket
import syslog
import os
import sys
import daemon
import threading
import time

listen_port = 10001
listen_ip = "127.0.0.1"
tmp_dir = "/tmp"

new_judge = threading.Event() #event for new judge coming

def test_judge(judge):
    judge.result='TESTING'
    judge.save()
    time.sleep(30);
    judge.result = 'AC'
    judge.save()

def check_judges():
    while 1:
        new_judge.clear()
        syslog.syslog("check judges, thread count:%d" % threading.activeCount())
        for judge in oj.judge.models.Judge.objects.filter(result__exact = 'WAIT'):
            threading.Thread(target=test_judge, args=(judge,)).start()
            syslog.syslog("new thread started")
        new_judge.wait()

def init_django():
    sys.path.append('../..')
    global oj
    oj = __import__('oj')
    sys.path.pop()
    os.environ['DJANGO_SETTINGS_MODULE'] = 'oj.settings'
    import oj.judge.models
    import oj.problem.models
    import oj.volume.models


def check_interval():
    new_judge.set()
    threading.Timer(10, check_interval).start()


def main():
    init_django()
    
    threading.Thread(target = check_judges).start()

    check_interval()

    # create listening socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((listen_ip, listen_port))
    s.listen(10)

    #accept a connection and notify check_thread 
    while 1:
        conn, addr = s.accept()
        new_judge.set()
        conn.send("1")
        conn.close()

if __name__ == '__main__':
    syslog.openlog('onlinejudge')
    daemon.rundaemon(main, pidfile='/home/czk/oj/bin/pydaemon.pid', logfile = '/home/czk/oj/bin/pydaemon.log',  datadir = '/home/czk/oj/bin')
