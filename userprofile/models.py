#coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from oj.problem.models import Problem
from oj.contest.models import Contest



class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True,verbose_name = u'用户')
	name = models.CharField('姓名',max_length = 100,default='匿名天使',blank = True)
	classes = models.CharField('班级',max_length = 256,default='09计本1班',blank = True)
	submit_counts = models.PositiveIntegerField('提交总数', default = 0)
	accept_counts = models.PositiveIntegerField('正确提交数', default = 0)
	accept_problems = models.ManyToManyField(Problem, blank = True)
	accept_problems_counts = models.PositiveIntegerField('正确题数', default = 0)
	incontest = models.BooleanField(default = False, blank = True)
	contest = models.ForeignKey(Contest,blank = True,null=True)
#	contestuser = models.ForeignKey(ContestUser,blank=True,null=True)

	def __unicode__(self):
		return u'%s %s' % (self.user.username, self.name)

	class Admin:
		list_display = (u'user', 'accept_problems_counts', 'accept_counts', 'submit_counts')

	class Meta:
		ordering = ['-accept_problems_counts', 'submit_counts']
		verbose_name = verbose_name_plural = u'用户数据'

class ContestUser(models.Model):
	userprofile = models.ForeignKey(UserProfile,  null = True, blank=True,verbose_name = u'比赛用户')
	contest = models.ForeignKey(Contest, verbose_name = u'比赛', null = True, blank=True)
	submit_counts = models.PositiveIntegerField('提交总数', default = 0)
	accept_counts = models.PositiveIntegerField('正确提交数', default = 0)
	accept_problems = models.ManyToManyField(Problem, blank = True)
	accept_problems_counts = models.PositiveIntegerField('正确题数', default = 0)
	
	def __unicode__(self):
		return u'%d %s' %(self.id,self.contest.title)
	class Admin:
		list_display = (u'userprofile',u'contest' 'accept_problems_counts', 'accept_counts', 'submit_counts')
	
	class Meta:
		ordering = ['-accept_problems_counts', 'submit_counts']
		verbose_name = verbose_name_plural = u'用户比赛数据'
