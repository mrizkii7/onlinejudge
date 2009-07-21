#coding=utf-8
from django.db import models

JUDGERULE_CHOICES = (
	('STRICT', u'严格比较输入输出'),
	('SPECIAL', u'使用特殊判题程序进行特殊判题'),
	('IGNOREWHITE', u'忽略所有空白'),
	('MANUAL', u'手动判题'),
)

class Problem(models.Model):
	title = models.CharField('标题', max_length=256)
	description = models.TextField('问题描述')
	input = models.TextField('输入')
	output = models.TextField('输出')
	sampleinput = models.TextField('输入样例')
	sampleoutput = models.TextField('输出样例')
	origin = models.TextField('出处', default = 'wzu', blank = True)
	hint = models.TextField('提示',  blank = True)
	memorylimit = models.PositiveIntegerField('内存限制(KB)', default = 32768, blank = True)
	timelimit = models.PositiveIntegerField('时间限制(ms)', default = 1000, blank = True)
	judgerule = models.CharField('判题规则', max_length = 100, choices = JUDGERULE_CHOICES, default='IGNOREWHITE')
	specialjudge = models.TextField('特殊判题程序', blank = True)

	accept_counts = models.PositiveIntegerField('成功提交次数', default = 0)
	submit_counts = models.PositiveIntegerField('提交次数', default = 0)

	def __unicode__(self):
		return u'%s %s'%(self.id, self.title) 

	class Admin:
		list_display = ('id', u'title', u'judgerule')

	class Meta:
		ordering = ['id']
		verbose_name = verbose_name_plural = u'问题'

class ProblemImage(models.Model):
	problem = models.ForeignKey(Problem, verbose_name = u'问题')
	image = models.ImageField(u'图片', upload_to = 'images')

	class Admin:
		list_display = (u'problem',)

	class Meta:
		verbose_name = verbose_name_plural = u'图片'

class ProblemTestData(models.Model):
	problem = models.ForeignKey(Problem, verbose_name = u'问题')
	inputdata = models.TextField('输入数据')
	outputdata = models.TextField('输出数据')

	def __unicode__(self):
		return u'%s %s' % (self.id, self.problem)

	def save(self):
		self.inputdata = self.inputdata.replace("\r\n", "\n")
		self.inputdata = self.inputdata.replace("\r", "\n")
		self.outputdata = self.outputdata.replace("\r\n", "\n")
		self.outputdata = self.outputdata.replace("\r", "\n")
		super(ProblemTestData, self).save()

	class Admin:
		list_display = (u'id', u'problem')
		list_filter = (u'problem',)

	class Meta:
		verbose_name = verbose_name_plural =u'测试数据'


