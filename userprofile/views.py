# Create your views here.

from django.shortcuts import render_to_response
import django.contrib.auth as auth
from oj.judge.models import Judge
from oj.volume.models import ProblemVolume

def login(request):
    return render_to_response('userprofile/login.html', {'user':request.user})

def logincheck(request):
    username = request.REQUEST['username']
    password = request.REQUEST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None:
        auth.login(request, user)
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

def userdetail(request, user_id):
    user = auth.models.User.objects.get(id__exact = user_id)
    judges = Judge.objects.filter(user__exact = user)
    acjudges = judges.select_related().filter(result__exact = 'AC')
    profile = {'acceptcounts': acjudges.count(),
               'submitcounts': judges.count()}
    return render_to_response('userprofile/userdetail.html',{'object':user, 'profile':profile, 'accepted':acjudges,'user':request.user }) 

def userlist(request):
    object_list = auth.models.User.objects.all()
    return render_to_response('userprofile/userlist.html', {'object_list':object_list,'user':request.user})


def userpermitproblem(user, problem):
    if user.is_anonymous():
        return False
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
    if problem in volume.problem.all():
        for group in user.groups.all():
            if group in volume.permittedgroups.all():
                return True
    return False    
