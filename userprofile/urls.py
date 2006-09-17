from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^changepassword/$', 'oj.userprofile.views.changepassword'),
    (r'^login/$', 'oj.userprofile.views.login'),
    (r'^logincheck/$', 'oj.userprofile.views.logincheck'),
    (r'^logout/$', 'oj.userprofile.views.logout'),
    (r'^$','oj.userprofile.views.userlist'),
    (r'^(?P<user_id>\d+)/$','oj.userprofile.views.userdetail'),

)
