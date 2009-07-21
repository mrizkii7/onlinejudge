from django.conf.urls.defaults import *

#from oj.contest.models import Contest

urlpatterns = patterns('oj.contest.views',
	(r'^$', 'contest_list'), 
	(r'^(?P<contest_id>\d+)/login/$', 'contest_login'),
	(r'^logout/$', 'contest_logout'),
#	(r'^userlist/$', 'contestuser_list'),
#	(r'^judge/$', 'contestjudge_list'),
	(r'^(?P<contest_id>\d+)/regenerate/$', 'contest_regenerate'),
	(r'^(?P<contest_id>\d+)/userlist/$', 'contestuserlist'),
	(r'^(?P<contest_id>\d+)/judgelist/$', 'contestjudgelist'),
	(r'^(?P<contest_id>\d+)/users/(?P<user_id>\d+)/$', 'contestuser_detail'),
#	(r'^(?P<contest_id>\d+)/$', 'contest_detail'), 
)
