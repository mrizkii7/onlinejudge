#coding=utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
import django.contrib.auth as auth
from oj.contest.models import Contest
from oj.userprofile.views import  userpermitcontest
from oj.userprofile.models import UserProfile,ContestUser
from oj.judge.models import Judge
from django.template import RequestContext

import datetime

def contest_list(request):
	user = request.user
#	if user.is_anonymous():
#		return render_to_response('userprofile/login.html', {'user':user})
#	userprofile = user.get_profile()

	contests = Contest.objects.all()
	c=RequestContext(request, {'user':user,'contests':contests,})
	return render_to_response('contest/contest_list.html', c )


def contestjudgelist(request,contest_id):
	user = request.user
	if user.is_anonymous():
		return render_to_response('userprofile/login.html', {'user':user})
	userprofile = user.get_profile()
	contest=Contest.objects.get(id__exact = contest_id)
	filter_option = {}
	option = {}
	page = int(request.GET.get('page', '1'))

	for filter_name in ['user', 'problem', 'result', 'language', 'contest' ]:
		filter_value = request.GET.get(filter_name)
	if filter_value:
		filter_option[filter_name+'__exact'] = filter_value
		option[filter_name] = filter_value


	alljudges = Judge.objects.filter(**filter_option).filter(incontest__exact=contest.id)
	pages = (alljudges.count()-1)/20+1
	judges = alljudges[20*(page-1):20*page]

	optionurl = "&".join( ["%s=%s"%(k, v) for (k, v) in option.items()] )
	c=RequestContext(request, 
		   {'user':user,'userprofile':userprofile,'object_list':judges, 'is_paginated':True, 'has_previous':(page > 1), 'has_next':(page<pages), 'page':page, 'pages':pages, 
			'next'    :optionurl+'&page=%s' % (page+1), 
			'previous':optionurl+'&page=%s' % (page-1)})
	return render_to_response('judge/judge_list.html',c )



def contest_detail(request, contest_id):
	user=request.user
	contest = Contest.objects.get(id__exact = contest_id)
	now = datetime.datetime.now()
	if userpermitcontest(user, contest) and now > contest.start_time and now < contest.end_time:
		userprofile = user.get_profile()
		c=RequestContext(request, {'user':user,'userprofile':userprofile,'contest':contest})
		return render_to_response('contest/contest_detail.html', c)
	else:
		errors = {'Permission not allowed':''}
		return render_to_response('errors.html', RequestContext(request, {'errors':errors}))



def contest_login(request, contest_id):
	user=request.user
	contest = Contest.objects.get(id__exact = contest_id)
	now = datetime.datetime.now()
	if userpermitcontest(user, contest) and now > contest.start_time and now < contest.end_time:
		userprofile = user.get_profile()
		userprofile.incontest = True
		userprofile.contest=contest
		try:
			contestuser = ContestUser.objects.get(userprofile__exact=userprofile.id,contest__exact = contest.id)
		except ContestUser.DoesNotExist:
			contestuser = ContestUser(userprofile=userprofile,contest=contest)
			contestuser.save()
#			userprofile.contestuser=contestuser
		userprofile.save()
		c=RequestContext(request, {'user':user,'userprofile':userprofile,'contest':contest})
		return render_to_response('contest/contest_detail.html', c)
	else:
		return render_to_response('message.html',{'message':u'不能参加比赛','user':user})

def contest_logout(request):
	user=request.user
	userprofile = user.get_profile()
	userprofile.incontest = False
	userprofile.save()
	return render_to_response('message.html',{'message':u'成功退出比赛','user':user,'userprofile':userprofile})

def contest_regenerate(request, contest_id):
	contest = Contest.objects.get(id__exact = contest_id)
	for problem in contest.problem.all():
		problem.accept_counts = Judge.objects.filter(problem__exact = problem, result__exact = 'AC').count()
	problem.submit_counts = Judge.objects.filter(problem__exact = problem).count()
	problem.save()
	return HttpResponseRedirect('/contest/%s/userlist/'%contest_id)

def contestuser_list(request):
	user = request.user
	if user.is_anonymous():
		return render_to_response('userprofile/login.html', {'user':user})
	userprofile = user.get_profile()
	contest=userprofile.contest
	contestusers=ContestUser.objects.filter(contest__exact=contest.id)
	c=RequestContext(request, {'user':user,'userprofile':userprofile,'contestusers':contestusers,})
	return render_to_response('contest/contestuser_list.html', c )


def contestuser_detail(request, contest_id,user_id):
	user = request.user
	if user.is_anonymous():
		return render_to_response('userprofile/login.html', {'user':user})
	userprofile=user.get_profile()
	userdetail=UserProfile.objects.get(user__exact=user_id)
	contestuser=ContestUser.objects.get(userprofile__exact=userdetail.id,contest__exact=contest_id)
	judges = Judge.objects.filter(result__exact = 'AC',user__exact=user_id,incontest__exact=contest_id).order_by('id')
	c=RequestContext(request, {'user':user,'judges':judges,'userprofile':userprofile,'contestuser':contestuser,'userdetail':userdetail})
	return render_to_response('contest/contestuser_detail.html',c ) 

def contestuserlist(request,contest_id):
	user = request.user
	if user.is_anonymous():
		return render_to_response('userprofile/login.html', {'user':user})
	userprofile = user.get_profile()
	contest=Contest.objects.get(id__exact=contest_id)
	if not userpermitcontest(user,contest):
		return render_to_response('message.html',{'message':u'非公开比赛','user':user,'userprofile':userprofile})
	contestusers=ContestUser.objects.filter(contest__exact=contest.id)
	c=RequestContext(request, {'user':user,'userprofile':userprofile,'contestusers':contestusers,'contest':contest})
	return render_to_response('contest/contestuser_list.html', c )