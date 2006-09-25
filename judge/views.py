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
    if judge.user != request.user:
        errors = {'Permission not allowed, please log in as the author':''}
        return render_to_response('errors.html', {'errors':errors})
    return render_to_response('judge/judge_print.html', RequestContext(request, {'object':judge}))

