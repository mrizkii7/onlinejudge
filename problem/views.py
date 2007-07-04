#coding=utf-8
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from oj.judge.models import Judge
from oj.problem.models import Problem,ProblemImage
from oj.volume.models import ProblemVolume
from oj.userprofile.views import userpermitproblem, userpermitcontest
from django import forms
from django.template import RequestContext
from oj.contest.models import Contest

import socket
import datetime

def problemdetail(request, problemid):
    problem = Problem.objects.get(id__exact = problemid)
    images = ProblemImage.objects.filter(problem__exact = problem)

    if not userpermitproblem(request.user, problem):
        errors = {'Permission not allowed':''}
        return render_to_response('errors.html',{'errors':errors})
    return render_to_response('problem/problemdetail.html', RequestContext(request, {'object':problem, 'images':images}))

def notify_judger():
    try:
        HOST = '127.0.0.1'  # The judger host
        PORT = 10001        # The same port as used by the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
    finally:
        s.close()

def rejudge_problem(request, problemid):
    problems = Judge.objects.filter(problem__exact = problemid)
    for p in problems:
    	p.result = 'WAIT'
	p.result_detail = ''
	p.save()
    notify_judger()
    return HttpResponseRedirect('/oj/problem/%s/' %problemid)

def problemsubmit(request, problemid):
    manipulator = Judge.AddManipulator()
    user = request.user
    problem = Problem.objects.get(id__exact = problemid)
    if not userpermitproblem(user, problem):
        errors = {'Permission not allowed':''}
        return render_to_response('errors.html', RequestContext(request, {'errors':errors}))
    
    if(request.POST):
        submittime = datetime.datetime.now()
        
        new_data = request.POST.copy()

        if new_data['incontest']:
	    contest = Contest.objects.get(id__exact = new_data['incontest'])
	    if not userpermitcontest(user, contest) or submittime < contest.start_time or submittime > contest.end_time:
	        errors = {'Permission not allowed':''}
	        return render_to_response('errors.html', RequestContext(request, {'errors':errors}))



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
	    user.get_profile().submit_counts +=1
	    user.get_profile().save()
	    problem.submit_counts += 1
	    problem.save()

            return render_to_response('problem/problemsubmitresult.html', RequestContext(request, {}))
    else:
        errors = {}
        new_data = {'language':'c++'}
        problem = Problem.objects.get(id__exact=problemid)
        form = forms.FormWrapper(manipulator, new_data, errors)
        return render_to_response('problem/problemsubmit.html', RequestContext(request, {'problem':problem, 'form': form}))

