#coding=utf-8
from django.db import models

# Create your models here.

JUDGERULE_CHOICES = (
    ('STRICT', 'strict judge input and output'),
    ('SPECIAL', 'special judge using a specific program'),
    ('IGNOREWHITE', 'ignore white spaces in output'),
    ('MANUAL', 'manually judged'),
)

class Problem(models.Model):
#    problemid = models.PositiveIntegerField('Problem ID', unique=True)
    title = models.CharField('Title', maxlength=256)
    description = models.TextField('Description')
    input = models.TextField('Input')
    output = models.TextField('Output')
    sampleinput = models.TextField('Sample Input')
    sampleoutput = models.TextField('Sample Output')
    origin = models.TextField('Origin', blank = True)
    hint = models.TextField('Hint', blank = True)
    memorylimit = models.PositiveIntegerField('Memory Limit(KB)', default = 32768, blank = True)
    timelimit = models.PositiveIntegerField('Time Limit(ms)', default = 1000, blank = True)
    judgerule = models.CharField('Judge rule', maxlength = 100, choices = JUDGERULE_CHOICES, default='STRICT')
    specialjudge = models.TextField('Special Judge Program', blank = True)

    def __str__(self):
	return "%s %s"%(self.id, self.title)

    class Admin:
	pass

    class Meta:
	ordering = ['id']
	verbose_name = 'Problem'

class ProblemImage(models.Model):
    problem = models.ForeignKey(Problem)
    image = models.ImageField('Image', upload_to = 'images', core = True)

    class Admin: pass

    class Meta:
	verbose_name = 'Problem Image'

class ProblemTestData(models.Model):
    problem = models.ForeignKey(Problem, edit_inline = True)
    inputdata = models.TextField('Input Data', core = True)
    outputdata = models.TextField('Output Data', core = True)

    def __str__(self):
	return '%s %s' % (self.id, self.problem)

    class Admin:
	pass

    class Meta:
	verbose_name = 'Test Data'


