from django.conf.urls.defaults import *

from oj.problem.models import Problem

urlpatterns = patterns('',
    (r'^(?P<problemid>\d+)/$', 'oj.problem.views.problemdetail'),

    (r'^(?P<problemid>\d+)/submit/$', 'oj.problem.views.problemsubmit'),

    (r'^(?P<problemid>\d+)/status/$','oj.problem.views.problemstatus'),
    (r'^(?P<problemid>\d+)/rejudge/$', 'oj.problem.views.rejudge_problem'),

)

