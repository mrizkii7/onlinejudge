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

def login(request):
    return render_to_response('userprofile/login.html', {'user':request.user})

def logincheck(request):
    username = request.REQUEST['username']
    password = request.REQUEST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
	user.last_login = datetime.datetime.now()
	user.save()
	return render_to_response('userprofile/logincheck.html', {'success':True,'user':request.user})
    else:
        return render_to_response('userprofile/logincheck.html', {'success':False,'user':request.user})

def logout(request):
    if not request.user.is_anonymous():
	auth.logout(request)
	message = 'Logout Success'
    else:
	message = 'Not Login'

    return render_to_response('userprofile/logout.html',{'message':message,'user':request.user})

def changepassword(request):
    if request.user is not None:
        if request.POST:
            if request.POST['password1'] == request.POST['password2']:
                request.user.set_password(request.POST['password1'])
                request.user.save()
                return render_to_response('userprofile/logincheck.html', {'success':True,'user':request.user})
            else:
                return render_to_response('userprofile/logincheck.html', {'success':False,'user':request.user})
        else:
            return render_to_response('userprofile/changepassword.html', {'user':request.user})

def userdetail(request, user_id):
    user = UserProfile.objects.get(user__exact = user_id)
    return render_to_response('userprofile/user_detail.html',RequestContext(request, {'object':user}) ) 

def userlist(request):
    users = UserProfile.objects.all()
    return render_to_response('userprofile/user_list.html', RequestContext(request, {'object_list':users}) )

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
    return HttpResponseRedirect('/oj/users/')

def userpermitproblem(user, problem):
    if user.is_anonymous():
        return False
    if user.is_superuser:
        return True
    volumes = ProblemVolume.objects.all()
    for vol in volumes:
        if problem in vol.problem.all():
            for group in user.groups.all():
                if group in vol.permittedgroups.all():
                    return True
    return False
    
def userpermitvolume(user, volume):
    if user.is_anonymous():
        return False
    if user.is_superuser:
        return True
    for problem in volume.problem.all():
        for group in user.groups.all():
            if group in volume.permittedgroups.all():
                return True
    return False    

def userpermitcontest(user, contest):
    return True
