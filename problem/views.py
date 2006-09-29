#coding=utf-8
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from oj.judge.models import Judge
from oj.problem.models import Problem
from oj.volume.models import ProblemVolume
from oj.userprofile.views import userpermitproblem
from django import forms
from django.template import RequestContext

import socket
import datetime

def problemdetail(request, problemid):
    problem = Problem.objects.get(problemid__exact = problemid)
    if not userpermitproblem(request.user, problem):
        errors = {'Permission not allowed':''}
        return render_to_response('errors.html',{'errors':errors})
    return render_to_response('problem/problemdetail.html', RequestContext(request, {'object':problem}))

def notify_judger():
    try:
        HOST = '127.0.0.1'  # The judger host
        PORT = 10001        # The same port as used by the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
    finally:
        s.close()


def problemsubmit(request, problemid):
    manipulator = Judge.AddManipulator()
    user = request.user
    problem = Problem.objects.get(problemid__exact = problemid)
    if not userpermitproblem(user, problem):
        errors = {'Permission not allowed':''}
        return render_to_response('errors.html', RequestContext(request, {'errors':errors}))
    
    if(request.POST):
        submittime = datetime.datetime.now()
        
        new_data = request.POST.copy()

        new_data['user'] = user.id
        new_data['problem'] = problem.id
        new_data['submittime_date'] = str(submittime.date())
        new_data['submittime_time'] = str(submittime.time().strftime('%H:%M:%S'))
        new_data['result'] = 'WAIT'
        new_data['result_detail'] = ''

        errors = manipulator.get_validation_errors(new_data)
        if errors:
            return render_to_response('errors.html', RequestContext(request, {'errors': errors}))
        else:
            manipulator.do_html2python(new_data)
            manipulator.save(new_data)
            notify_judger()
            return render_to_response('problem/problemsubmitresult.html', RequestContext(request, {}))
    else:
        errors = {}
        new_data = {'language':'c++'}
        problem = Problem.objects.get(problemid__exact=problemid)
        form = forms.FormWrapper(manipulator, new_data, errors)
        return render_to_response('problem/problemsubmit.html', RequestContext(request, {'problem':problem, 'form': form}))

