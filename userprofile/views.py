#coding=utf-8
# Create your views here.

import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import django.contrib.auth as auth
from oj.judge.models import Judge
from oj.volume.models import ProblemVolume
from oj.userprofile.models import UserProfile
from django.template import RequestContext
from oj.problem.models import Problem
from oj.contest.models import Contest
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm

def register(request):
	return render_to_response('userprofile/register.html', {'user':request.user})

def registercheck(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		username = request.REQUEST['username']
		password = request.REQUEST['password']
		password1 = request.REQUEST['password1']
		name = request.REQUEST['name']
		classes = request.REQUEST['classes']
		try:
			user =User.objects.get(username__exact = username)
			errors={u'用户已经存在':u''}
			return render_to_response('errors.html',RequestContext(request, {'errors': errors}))
		except:
			pass
		if password != password1:
			errors={u'两次密码不一致':''}
			return render_to_response('errors.html',RequestContext(request, {'errors': errors}))
		new_user=User(username=username)
		new_user.set_password(password)
		new_user.save()
		user=UserProfile()
		user.user=new_user
		user.name=name
		user.classes = classes
		user.save()
		new_user=auth.authenticate(username=username,password = password)
		auth.login(request, new_user)
		new_user.last_login = datetime.datetime.now()
		new_user.save()
		return render_to_response('message.html', {'message':u'注册成功','user':new_user,'userprofile':user})
	else:
		form = UserCreationForm()
	return render_to_response("userprofile/register.html", {'form': form,   })



def login(request):
	return render_to_response('userprofile/login.html', {'user':request.user})

def logincheck(request):
	username = request.REQUEST['username']
	password = request.REQUEST['password']
	user = auth.authenticate(username=username, password=password)
	if user is not None and user.is_active:
		auth.login(request, user)
		user.last_login = datetime.datetime.now()
		user.save()
		try:
			userprofile=UserProfile.objects.get(user__exact=user.id)
		except:
			userprofile = UserProfile(user=user)
			userprofile.save()
		return render_to_response('message.html', {'message':u'登录成功','user':request.user,'userprofile':userprofile,})
	else:
		return render_to_response('message.html', {'message':u'登录失败','user':request.user})



def logout(request):
	if not request.user.is_anonymous():
		auth.logout(request)
		message = u'注销成功'
	else:
		message = u'未登录'
	return render_to_response('userprofile/logout.html',{'message':message,'user':AnonymousUser()})

def changeuserprofile(request):
	if request.user is not None:
		userprofile = request.user.get_profile()
		if request.POST:
			password1=request.POST['password1']
			password2=request.POST['password2']
			name=request.POST['name']
			classes=request.POST['classes']
			user=UserProfile.objects.get(user__exact=request.user.id)
			if password1 == password2 :
				if password1!='':
					request.user.set_password(password1)
				if name!='':
					request.user.first_name=name
					user.name=name
				if classes!='':
					request.user.last_name=classes
					user.classes = classes
				request.user.save()
				user.save()
				return render_to_response('message.html', {'message':u'修改成功','user':request.user,'userprofile':userprofile,})
			else:
				errors={u'两次输入的密码要一致':u''}
				return render_to_response('errors.html',RequestContext(request, {'errors': errors,'userprofile':userprofile,}))
		else:
			return render_to_response('userprofile/changeuserprofile.html', {'user':request.user,'userprofile':userprofile,})

def userdetail(request, user_id):
	user = request.user
	if user.is_anonymous():
		return render_to_response('userprofile/login.html', {'user':user})
	userprofile=user.get_profile()
	userdetail=UserProfile.objects.get(user__exact=user_id)
	judges = Judge.objects.filter(result__exact = 'AC',user__exact=user_id).order_by('id')
	c=RequestContext(request, {'userdetail':userdetail,'user':user,'judges':judges,'userprofile':userprofile})
	return render_to_response('userprofile/user_detail.html',c ) 

def userlist(request):
	user = request.user
	if user.is_anonymous():
		return render_to_response('userprofile/login.html', {'user':user})
	users = User.objects.all()
	userprofiles = UserProfile.objects.all()
	userprofile = request.user.get_profile()
	c=RequestContext(request, {'user':user,'userprofile':userprofile,'users':users,'userprofiles':userprofiles})
	return render_to_response('userprofile/user_list.html', c )
	

def userlist(request):
	user = request.user
	if user.is_anonymous():
		return render_to_response('userprofile/login.html', {'user':user})
	userprofile = user.get_profile()
	userprofiles = UserProfile.objects.all()
	c=RequestContext(request, {'user':user,'userprofile':userprofile,'userprofiles':userprofiles,})
	return render_to_response('userprofile/user_list.html', c )

def regenerate(request):
	users = auth.models.User.objects.all()
	for user in users:
		profile, created = UserProfile.objects.get_or_create(user = user )
	acjudges = Judge.objects.filter(user__exact = user, result__exact = 'AC')
	profile.accept_counts = acjudges.count()
	profile.submit_counts = Judge.objects.filter(user__exact = user).count()
	profile.accept_problems_counts = len(acjudges.values('problem').distinct())
	profile.accept_problems = Problem.objects.in_bulk([x.problem.id for x in acjudges]).values()
	profile.save()
	return HttpResponseRedirect('/users/')

def userpermitproblem(user, problem):
	if user.is_anonymous():
		return False
	if user.is_superuser:
		return True
	volumes = ProblemVolume.objects.all()
	for vol in volumes:
		if vol.ispublic:
			return True
		if problem in vol.problem.all():
			for group in user.groups.all():
				if group in vol.permittedgroups.all():
					return True
	contests = Contest.objects.all()
	for contest in contests:
		if problem in contest.problem.all():
			for group in user.groups.all():
				if group in contest.permittedgroups.all():
					return True
	return False

def userpermitvolume(user, volume):
	if volume.ispublic:
		return True
	if user.is_anonymous():
		return False
	if user.is_superuser:
		return True
	for group in user.groups.all():
		if group in volume.permittedgroups.all():
			return True
	return False    

def userpermitcontest(user, contest):
	if contest.is_public:
		return True
	if user.is_anonymous():
		return False
	if user.is_superuser:
		return True
	for group in user.groups.all():
		if group in contest.permittedgroups.all():
			return True
	return False
