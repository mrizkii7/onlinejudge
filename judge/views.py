from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from oj.judge.models import Judge
from oj.problem.models import Problem
from oj.volume.models import ProblemVolume
from django import forms
from django.template import RequestContext



def judge_print(request, object_id):
    judge = Judge.objects.get(id__exact = object_id)
#    user =  auth.models.User.objects.get(id__exact = judge.user)
    if not request.user.is_superuser and judge.user != request.user:
        errors = {'Permission not allowed, please log in as the author':''}
        return render_to_response('errors.html', {'errors':errors})
    return render_to_response('judge/judge_print.html', RequestContext(request, {'object':judge}))

def judge_rejudge(request, object_id):
    judge = Judge.objects.get(id__exact = object_id)
    if not request.user.is_superuser and judge.user != request.user:
        errors = {'Permission not allowed, please log in as the author':''}
        return render_to_response('errors.html', {'errors':errors})
    judge.result = "WAIT"
    judge.save()
    return HttpResponseRedirect('/oj/judge/%s/' %object_id)
#    return render_to_response('judge/judge_detail.html', RequestContext(request, {'object': judge}))

def judge_filter(request):
    page = int(request.GET.get('page', '1'))
    user = request.GET.get('user')
    problem = request.GET.get('problem')
    result = request.GET.get('result')
    language = request.GET.get('language')
    alljudges = Judge.objects.filter(user__exact = user, problem__exact = problem, result__exact = result, 
                   language__exact = language)
    pages = (alljudges.count()-1)/20+1
    judges = alljudges[20*(page-1):20*page]

    option = []
    if user:
        option.append("user=%s" % user)
    if problem:
        option.append('problem=%s' % problem)    
    if result:
        option.append('result=%s' % result)
    if language:
        option.append('language=%s' % language)
    optionurl = "&".join(option)

    return render_to_response('judge/judge_list.html', RequestContext(request, 
           {'object_list':judges, 'is_paginated':True, 'has_previous':(page > 1), 'has_next':(page<pages), 'page':page, 'pages':pages, 
            'next'    :optionurl+'&page=%s' % (page+1), 
            'previous':optionurl+'&page=%s' % (page-1)}) )
