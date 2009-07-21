from django.conf.urls.defaults import *

from django.contrib.auth.models import User
from django.contrib.auth.views import login, logout

urlpatterns = patterns('oj.userprofile.views',
	(r'^login/$', 'login'),
	(r'^logout/$', 'logout'),
	(r'^logincheck/$', 'logincheck'),
	(r'^changeuserprofile/$', 'changeuserprofile'),
	(r'^register/$', 'register'),
	(r'^registercheck/$', 'registercheck'),
	(r'^$', 'userlist'),
	(r'^(?P<user_id>\d+)/$','userdetail'),
	(r'^regenerate/$', 'regenerate'),
)
