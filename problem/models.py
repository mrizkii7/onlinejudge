#coding=utf-8
from django.db import models

JUDGERULE_CHOICES = (
    ('STRICT', '严格比较输入输出'),
    ('SPECIAL', '使用特殊判题程序进行特殊判题'),
    ('IGNOREWHITE', '忽略所有空白'),
    ('MANUAL', '手动判题'),
)

class Problem(models.Model):
#    problemid = models.PositiveIntegerField('Problem ID', unique=True)
    title = models.CharField('标题', maxlength=256)
    description = models.TextField('问题描述')
    input = models.TextField('输入')
    output = models.TextField('输出')
    sampleinput = models.TextField('输入样例')
    sampleoutput = models.TextField('输出样例')
    origin = models.TextField('出处', blank = True)
    hint = models.TextField('提示', blank = True)
    memorylimit = models.PositiveIntegerField('内存限制(KB)', default = 32768, blank = True)
    timelimit = models.PositiveIntegerField('时间限制(ms)', default = 1000, blank = True)
    judgerule = models.CharField('判题规则', maxlength = 100, choices = JUDGERULE_CHOICES, default='IGNOREWHITE')
    specialjudge = models.TextField('特殊判题程序', blank = True)

    def __str__(self):
	return "%s %s"%(self.id, self.title)

    def accept_counts(self):
        from oj.judge.models import Judge
        return Judge.objects.filter(problem__exact = self, result__exact = 'AC').count()

    def submit_counts(self):
        from oj.judge.models import Judge
        return Judge.objects.filter(problem__exact = self).count()


    class Admin:
	list_display = ('id', 'title', 'judgerule')

    class Meta:
	ordering = ['id']
	verbose_name = verbose_name_plural = '问题'

class ProblemImage(models.Model):
    problem = models.ForeignKey(Problem, verbose_name = '问题')
    image = models.ImageField('图片', upload_to = 'images', core = True)

    class Admin:
        list_display = ('problem',)

    class Meta:
	verbose_name = verbose_name_plural = '图片'

class ProblemTestData(models.Model):
    problem = models.ForeignKey(Problem, verbose_name = '问题', edit_inline = True)
    inputdata = models.TextField('输入数据', core = True)
    outputdata = models.TextField('输出数据', core = True)

    def __str__(self):
	return '%s %s' % (self.id, self.problem)

    class Admin:
	list_display = ('id', 'problem')
	list_filter = ('problem',)

    class Meta:
	verbose_name = verbose_name_plural = '测试数据'


