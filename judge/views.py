#coding=utf-8
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
	userprofile = request.user.get_profile()
	c=RequestContext(request, {'object':judge,'userprofile':userprofile})
	return render_to_response('judge/judge_print_exp.html', c)

def judge_print_ass(request, object_id):
	judge = Judge.objects.get(id__exact = object_id)
	if request.user.is_anonymous() or ( not request.user.is_superuser and judge.user != request.user):
		errors = {'Permission not allowed, please log in as the author':''}
		return render_to_response('errors.html', {'errors':errors})
	userprofile = request.user.get_profile()
	c=RequestContext(request, {'object':judge,'userprofile':userprofile})
	return render_to_response('judge/judge_print_ass.html', c)

def judge_detail(request, object_id):
	judge = Judge.objects.get(id__exact = object_id)
	if ((not request.user.is_anonymous()) and judge.user == request.user)or request.user.is_staff:
		return render_to_response('judge/judge_detail.html', RequestContext(request, {'judge':judge}))
	else:
		errors = {'Permission not allowed, please log in as the author':''}
		return render_to_response('errors.html', {'errors':errors})


def judge_rejudge(request, object_id):
	judge = Judge.objects.get(id__exact = object_id)
	if not request.user.is_superuser and judge.user != request.user:
		errors = {'Permission not allowed, please log in as the author':''}
		return render_to_response('errors.html', {'errors':errors})
	judge.result = "WAIT"
	judge.save()
	return HttpResponseRedirect('/judge/%s/' %object_id)
#    return render_to_response('judge/judge_detail.html', RequestContext(request, {'object': judge}))

def judge_list(request):
	user = request.user
	if user.is_anonymous():
		return render_to_response('userprofile/login.html', {'user':user})
	userprofile = user.get_profile()
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
	c=RequestContext(request, 
		   {'user':user,'userprofile':userprofile,'object_list':judges, 'is_paginated':True, 'has_previous':(page > 1), 'has_next':(page<pages), 'page':page, 'pages':pages, 
			'next'    :optionurl+'&page=%s' % (page+1), 
			'previous':optionurl+'&page=%s' % (page-1)})
	return render_to_response('judge/judge_list.html',c )
