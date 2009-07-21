#coding=utf-8
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from oj.judge.models import Judge,JudgeForm
from oj.userprofile.models import ContestUser
from oj.problem.models import Problem,ProblemImage
from oj.volume.models import ProblemVolume
from oj.userprofile.views import userpermitproblem, userpermitcontest
from django import forms
from django.template import RequestContext
from oj.contest.models import Contest
from django.contrib.auth.models import User
from django import forms
import socket
import datetime

def problemdetail(request, problemid):
	problem = Problem.objects.get(id__exact = problemid)
	images = ProblemImage.objects.filter(problem__exact = problem)

	user=request.user
	if not userpermitproblem(user, problem):
		return render_to_response('message.html', {'message':u'非公开题目，无权查看。','user':user,})
	if user.is_anonymous():
		userprofile = ''
	else:
		userprofile = user.get_profile()
	c=RequestContext(request, {'user':user,'userprofile':userprofile,'object':problem, 'images':images})
	return render_to_response('problem/problemdetail.html', c)



def rejudge_problem(request, problemid):
	problems = Judge.objects.filter(problem__exact = problemid)
	for p in problems:
		p.result = 'WAIT'
		p.result_detail = ''
		p.save()
	return HttpResponseRedirect('/problem/%s/' %problemid)

def problemsubmit(request, problemid):
	if not request.user.is_authenticated():
		errors = {u'请先登录':''}
		return render_to_response('errors.html',RequestContext(request, {'errors': errors}))
	user=request.user
	userprofile=user.get_profile()
	problem = Problem.objects.get(id__exact=problemid)
	submittime = datetime.datetime.now()
	if not userpermitproblem(user, problem):
		errors = {u'Permission not allowed':''}
		return render_to_response('errors.html',RequestContext(request, {'errors': errors}))
	if(request.POST):
		submit_user= User.objects.get(id__exact=request.REQUEST['user'])
		sourcecode = request.REQUEST['sourcecode']
		language = request.REQUEST['language']
		incontest = request.REQUEST['incontest']
		if userprofile.incontest:
			try:
				contest=Contest.objects.get(id__exact = incontest)
			except:
				return render_to_response('message.html',{'message':u'提交失败，本题为比赛题目','user':user,'userprofile':userprofile}) 
			if contest!=userprofile.contest:
				return render_to_response('message.html',{'message':u'提交失败，不要更改比赛','user':user,'userprofile':userprofile}) 
			if not userpermitcontest(user, contest):
				return render_to_response('message.html',{'message':u'提交失败，你不能参加比赛','user':user,'userprofile':userprofile}) 
			if submittime < contest.start_time or submittime > contest.end_time:
				return render_to_response('message.html',{'message':u'提交失败，比赛已经结束','user':user,'userprofile':userprofile}) 
		elif len(incontest)>0:
			return render_to_response('message.html',{'message':u'提交失败，本题非比赛题目','user':user,'userprofile':userprofile}) 
		if submit_user != user :
			return render_to_response('message.html',{'message':u'提交失败，请用自己的帐户提交','user':user,'userprofile':userprofile}) 
		else:
			new_judge = Judge()
			new_judge.user = user
			new_judge.problem = problem
			new_judge.language = language
			new_judge.sourcecode = sourcecode
			new_judge.submittime = submittime
			new_judge.result = 'WAIT'
			new_judge.result_detail = ''
			if userprofile.incontest:
				new_judge.incontest = Contest.objects.get(id__exact = incontest)
				contestuser=ContestUser.objects.get(userprofile__exact=userprofile.id,contest__exact=contest.id)
				contestuser.submit_counts +=1
				contestuser.save()
			user.get_profile().submit_counts +=1
			user.get_profile().save()
			problem.submit_counts += 1
			problem.save()
			new_judge.save()
			return render_to_response('problem/problemsubmitresult.html',RequestContext(request, {}))
	else:
		userprofile = request.user.get_profile()
		if userprofile.incontest:
			contest = userprofile.contest
			new_judge = {'user':user.id,'problem':problem.id,'language':'c','incontest':contest.id}
		else:
			new_judge = {'user':user.id,'problem':problem.id,'language':'c'}
		form = JudgeForm(new_judge)
		c=RequestContext(request, {'form':form,'user':request.user,'userprofile':userprofile})
		return render_to_response('problem/problemsubmit.html',c)
