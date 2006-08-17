#!/usr/bin/python
#coding=utf-8

import socket
import syslog
import os
import sys
import threading
import time
import signal
import commands

import daemon

listen_port = 10001
listen_ip = "127.0.0.1"
tmp_dir = "/tmp/judger/"
clk_tck = float(os.sysconf(os.sysconf_names['SC_CLK_TCK']))


new_judge = threading.Event() #event for new judge coming

extname = {
    'c++':'cc',
    'c': 'c',
    'python':'py',
    'java':'java',
}

def set_judge_result(judge, result, description = ''):
    judge.result = result
    judge.result_detail = description
    judge.save()

def strict_equal(judge, testcase, output):
    return testcase.outputdata == output


def test_judge(judge):

    set_judge_result(judge, 'TESTING')

    basename = 'judge_%s' % judge.id

    base_filename = '%s%s'%(tmp_dir, basename)

    # generate source file
    source_filename = base_filename + '.' + extname[judge.language]
    sourcefile = open(source_filename, 'w')
    sourcefile.write(judge.sourcecode)
    sourcefile.close()

    # compile program
    log_filename = base_filename + '.log'
    exe_filename = base_filename + '.exe'
    if judge.language == 'c++':
        compile_command = 'g++ %s -o %s -ansi -fno-asm -O2 -Wall -lm --static -DONLINE_JUDGE &>%s' % (source_filename, exe_filename, log_filename)
        if(os.system(compile_command)):
            logfile = open(log_filename)
            set_judge_result(judge, 'CE', logfile.read())
            logfile.close()
            return
    elif judge.language == 'c':
        compile_command = 'gcc %s -o %s -ansi -fno-asm -O2 -Wall -lm --static -DONLINE_JUDGE &>%s' % (source_filename, exe_filename, log_filename)
        if(os.system(compile_command)):
           logfile = open(log_filename)
           set_judge_result(judge, 'CE', logfile.read())
           logfile.close()
           return
    elif judge.language == 'python':
        set_judge_result(judge, 'JE', 'Not implemented yet')
        return
    elif judge.language == 'java':
        set_judge_result(judge, 'JE', 'Not implemented yet')
        return
    else:
        set_judge_result(judge, 'JE', 'Language no supported')
        return
    

    # run program

    output_filename = base_filename + '.out'
    input_filename = base_filename + '.in'
    #run_command = '%s' %(exe_filename, input_filename, output_filename)

    
    # compare result
    for testcase in oj.problem.models.ProblemTestData.objects.filter(problem__exact = judge.problem):
        input_file = open(input_filename,'w')
        input_file.write(testcase.inputdata)
        input_file.close()
        pid = os.fork()
        if pid == 0:
            input_file = open(input_filename, 'r')
            output_file = open(output_filename, 'w')
            os.dup2(input_file.fileno(), sys.stdin.fileno())
            os.dup2(output_file.fileno(), sys.stdout.fileno())
            os.execl(exe_filename, exe_filename)
            
        elif pid > 0:
            time_usage = 0
            memory_usage = 0
            time_limit_exceeded = False
            memory_limit_exceeded = False
            while 1:
                newpid, status = os.waitpid(pid, os.WNOHANG)
                if newpid != 0:
                    break
                   
                statfile = open('/proc/%d/stat'%pid, 'r')
                statvalue = statfile.read().split()
                statfile.close()
                
                time_usage = max(time_usage, int(statvalue[13]) + int(statvalue[14])) #user cputime+system cputime
                memory_usage = max(memory_usage, int(statvalue[22]))
                if time_usage / clk_tck > judge.problem.timelimit / 1000.0:
                    time_limit_exceeded = True
                if memory_usage > judge.problem.memorylimit * 1024:
                    memory_limit_exceeded = True
                if time_limit_exceeded or memory_limit_exceeded:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.1)
                    os.kill(pid, signal.SIGKILL)
                    
                time.sleep(judge.problem.timelimit / 10000.0)
            
            if os.WIFSIGNALED(status) and not time_limit_exceeded and not memory_limit_exceeded:
                # todo signal name unknown yet                
                set_judge_result(judge, 'RE', 'Signal %d raised' % os.WTERMSIG(status))
                return
            
            check_command = 'dump-acct -r /var/account/pacct | grep %s' % basename
            check_output = commands.getoutput(check_command)
            values = check_output.split('|')
            time_usage = (float(values[2])+float(values[3]))/clk_tck
            memory_usage = max(memory_usage, float(values[7])/4 * 1024)
            if time_limit_exceeded or time_usage > judge.problem.timelimit / 1000.0:
                set_judge_result(judge, 'TLE', 'time usage over %f'%time_usage)
                return

            if memory_limit_exceeded or memory_usage > judge.problem.memorylimit*1024:
                set_judge_result(judge, 'MLE', 'memory usage over %f' %memory_usage)
                return
            output_file = open(output_filename, 'r')
            output = output_file.read()
            if judge.problem.judgerule == 'STRICT':
                if not strict_equal(judge, testcase, output):
                    set_judge_result(judge, 'WA', 'Test case #')
                    output_file.close()
                    return
            elif judge.problem.judgerule == 'SPECIAL':
                set_judge_result(judge, 'JE')
                return
            elif judge.problem.judgerule == 'IGNOREWHITE':
                set_judge_result(judge, 'JE')
                return
            else:
                set_judge_result(judge, 'JE')
                return

    set_judge_result(judge, 'AC')
    output_file.close()


def check_judges():
    while 1:
        new_judge.clear()
        #syslog.syslog("check judges, thread count:%d" % threading.activeCount())
        for judge in oj.judge.models.Judge.objects.filter(result__exact = 'WAIT'):
            threading.Thread(target=test_judge, args=(judge,)).start()
            #syslog.syslog("new thread started")
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
