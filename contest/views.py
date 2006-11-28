from django.shortcuts import render_to_response
import django.contrib.auth as auth
from oj.contest.models import Contest
from oj.userprofile.views import  userpermitcontest
from django.template import RequestContext

def contest_list(request):
    contest = Contest.objects.all()
    return render_to_response('contest/contest_list.html', RequestContext(request, {'object_list':contest}) )

def contest_detail(request, object_id):
    contest = Contest.objects.get(id__exact = object_id)
    if userpermitcontest(request.user, contest):
        return render_to_response('contest/contest_detail.html', RequestContext(request, {'object':contest}))
    else:
        errors = {'Permission not allowed':''}
        return render_to_response('errors.html', RequestContext(request, {'errors':errors}))

