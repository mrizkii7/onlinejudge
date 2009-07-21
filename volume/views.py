#coding=utf-8
from django.shortcuts import render_to_response
import django.contrib.auth as auth
from oj.volume.models import ProblemVolume
from oj.userprofile.views import  userpermitvolume
from django.template import RequestContext
from django.http import HttpResponseRedirect
from oj.judge.models import Judge
from oj.contest.models import Contest

def index(request):
	volumes = ProblemVolume.objects.all()
	user=request.user
	if not user.is_anonymous():
		userprofile=user.get_profile()
	else:
		userprofile=''
	contests=Contest.objects.all()
	c=RequestContext(request, {'volumes':volumes,'contests':contests,'user':user,'userprofile':userprofile})
	return render_to_response('index.html', c )

def volume_list(request):
	volume = ProblemVolume.objects.all()
	user=request.user
	if not user.is_anonymous():
		userprofile=user.get_profile()
	else:
		userprofile=''
	c=RequestContext(request, {'object_list':volume,'user':user,'userprofile':userprofile})
	return render_to_response('volume/problemvolume_list.html', c )

def volume_detail(request, object_id):
	volume = ProblemVolume.objects.get(id__exact = object_id)
	user=request.user
	if not user.is_anonymous():
		userprofile=user.get_profile()
	else:
		userprofile= ''
	if userpermitvolume(request.user, volume):
		c=RequestContext(request, {'object':volume,'user':user,'userprofile':userprofile})
		return render_to_response('volume/problemvolume_detail.html', c)
	else:
		errors = {'Permission not allowed':''}
		c=RequestContext(request, {'errors':errors})
		return render_to_response('errors.html', c)

def volume_regenerate(request, object_id):
	volume = ProblemVolume.objects.get(id__exact = object_id)
	for problem in volume.problem.all():
		problem.accept_counts = Judge.objects.filter(problem__exact = problem, result__exact = 'AC').count()
	problem.submit_counts = Judge.objects.filter(problem__exact = problem).count()
	problem.save()
	return HttpResponseRedirect('/volume/%s/'%object_id)


