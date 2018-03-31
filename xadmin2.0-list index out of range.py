# -*- coding:utf-8 -*-

'''

在使用xadmin创建Model后,如果创建的数据表中含有DatetimeField的字段
那么在进入xadmin管理后台对数据进行操作的时候
会报出list out of range错误

查看报错信息发现指向 venv\lib\site-packages\xadmin\widgets.py in render, line 80
根据目录找到该文件下的代码
def render(self, name, value, attrs=None):
        input_html = [ht for ht in super(AdminSplitDateTime, self).render(name, value, attrs).split('\n') if ht != '']
        # return input_html
        return mark_safe('<div class="datetime clearfix"><div class="input-group date bootstrap-datepicker"><span class="input-group-addon"><i class="fa fa-calendar"></i></span>%s'
                         '<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div>'
                         '<div class="input-group time bootstrap-clockpicker"><span class="input-group-addon"><i class="fa fa-clock-o">'
                         '</i></span>%s<span class="input-group-btn"><button class="btn btn-default" type="button">%s</button></span></div></div>' % (input_html[0], _(u'Today'), input_html[1], _(u'Now')))

input_html[0]就是导致问题出现的原因,因为input只有一个值,从错误信息中找出input的值如下:
['<input type="text" name="create_time_0" class="date-field form-control '
 'admindatewidget" size="10" required id="id_create_time_0" /><input '
 'type="text" name="create_time_1" class="time-field form-control '
 'admintimewidget" size="8" required id="id_create_time_1" />']

仔细阅读代码后发现:
input_html = [ht for ht in super(AdminSplitDateTime, self).render(name, value, attrs).split('\n') if ht != '']
上面这行代码是希望将input_html用'\n'将两个标签切开,但由于代码中不含有'\n',导致分割失败.
但当初作者这么写肯定是可以拆开的,为什么现在突然就不行了呢?

继续查找两个标签的生成代码,发现来源于模板 venv\Lib\site-packages\django\forms\templates\django\forms\widgets\multiwidget.html
其中 {% spaceless %}{% for widget in widget.subwidgets %}{% include widget.template_name %}{% endfor %}{% endspaceless %}
注:spaceless标签的用法是
{% spaceless %}..内容..{% spaceless %}
用以删除内容的所有tab和换行

看到这里就明白了,猜测很可能是Django后续版本中添加了这个标签.
阅读Django的代码提交记录,发现果然如此,提交记录如下:
https://github.com/django/django/commit/47681af34447e5d45f3fdb316497cdf9fbd0b7ce
https://github.com/django/django/commit/c1d57615ac60171a73e1922a48ebc27fe513357e

验证了猜测之后,那么该如何解决这个问题呢?
有两个解决办法:

一:修改Django模块,将spaceless标签删除
这个办法可以解决这个越界问题,但是既然Django添加了这个标签,贸然修改可能会引起其他地方的某些错误,所以不才欧勇

二:改变input_html的拆分规则
将原代码
input_html = [ht for ht in super(AdminSplitDateTime, self).render(name, value, attrs).split('\n') if ht != '']

修改为:
input_html = [ht for ht in super(AdminSplitDateTime, self).render(name, value, attrs).split('\><') if ht != '']
input_html[0] += '\>'
input_html[1] += '<'

这种只修改了拆分规则,不会影响其他的,修改完保存之后再访问xadmin管理页面发现,问题解决.

参考资料:
https://blog.csdn.net/yuhan963/article/details/79167743
'''
