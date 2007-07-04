from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from oj.judge.models import Judge
from oj.problem.models import Problem
from oj.volume.models import ProblemVolume
from django import forms
from django.template import RequestContext

def judge_print_exp(request, object_id):
    judge = Judge.objects.get(id__exact = object_id)
    if request.user.is_anonymous() or ( not request.user.is_superuser and judge.user != request.user):
        errors = {'Permission not allowed, please log in as the author':''}
        return render_to_response('errors.html', {'errors':errors})
    return render_to_response('judge/judge_print_exp.html', RequestContext(request, {'object':judge}))

def judge_print_ass(request, object_id):
    judge = Judge.objects.get(id__exact = object_id)
    if request.user.is_anonymous() or ( not request.user.is_superuser and judge.user != request.user):
        errors = {'Permission not allowed, please log in as the author':''}
        return render_to_response('errors.html', {'errors':errors})
    return render_to_response('judge/judge_print_ass.html', RequestContext(request, {'object':judge}))

def judge_detail(request, object_id):
    judge = Judge.objects.get(id__exact = object_id)
    if request.user.is_anonymous() or ( not request.user.is_superuser and judge.user != request.user):
        errors = {'Permission not allowed, please log in as the author':''}
        return render_to_response('errors.html', {'errors':errors})
    return render_to_response('judge/judge_detail.html', RequestContext(request, {'object':judge}))


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
    filter_option = {}
    option = {}
    page = int(request.GET.get('page', '1'))

    for filter_name in ['user', 'problem', 'result', 'language', 'contest' ]:
        filter_value = request.GET.get(filter_name)
	if filter_value:
	    filter_option[filter_name+'__exact'] = filter_value
	    option[filter_name] = filter_value


    alljudges = Judge.objects.filter(**filter_option)
    pages = (alljudges.count()-1)/20+1
    judges = alljudges[20*(page-1):20*page]

    optionurl = "&".join( ["%s=%s"%(k, v) for (k, v) in option.items()] )

    return render_to_response('judge/judge_list.html', RequestContext(request, 
           {'object_list':judges, 'is_paginated':True, 'has_previous':(page > 1), 'has_next':(page<pages), 'page':page, 'pages':pages, 
            'next'    :optionurl+'&page=%s' % (page+1), 
            'previous':optionurl+'&page=%s' % (page-1)}) )
