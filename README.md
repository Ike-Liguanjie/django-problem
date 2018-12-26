# 前言
其实想做这个东西很久了，以前在看过大佬用readme做知识点总结的时候就也想用这个做，刚好最近有机会看了一下markdown的语法，想想干脆现在就动手吧。<br>
做这个东西的主要目的是为了方便自己回顾一些自己用过但不常用的代码和知识点，免得下次再遇到的时候忘记了还要再去查。<br>
前期的目录结构会比较混乱，想到哪里写哪里，可以用Crtl+F进行查找，等后期内容多了，再对内容框架做一个梳理，就这样。<br>

# 目录
* [Django](#django)
    * [1 admin后台中富文本的实现(DjangoUeditor)](#1-admin后台中富文本的实现djangoueditor)  
    * [2 admin后台中导入导出功能的实现](#2-admin后台中导入导出功能的实现)
        * [1 导出功能](#导出功能)  
        * [2 导入功能](#导入功能)
 
# Django
## 1 admin后台中富文本的实现(DjangoUeditor)
 首先下载安装第三方库DjangoUeditor，py2可以直接用pip命令进行安装。因为作者已经很久不更新了，所以不支持py3，想在py3里使用的话请[点此下载](https://codeload.github.com/twz915/DjangoUeditor3/zip/master)安装。  
 下载安装完成后，就可以在项目中进行配置了。这里以一个网上书店APP作为例子，`步骤没有先后，但必须要保证没有遗漏。`  
 1.在项目根目录的`setting.py`文件的`INSTALLED_APPS`字段中，将DjangoUeditor加入，具体代码如下。  
 ```
 INSTALLED_APPS = [
     ……………………………………
    'DjangoUeditor',
]
```
2.在在项目根目录的`urls.py文`中配置editor的路由。  
```
urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url('ueditor/', include('DjangoUeditor.urls')),
]
```
3.在APP下的model.py中配置ueditor字段
```
from DjangoUeditor.models import UEditorField

class Book(object):
    book_name = models.CharField(max_length=32, verbose_name=u'书本名字')
    book_content = UEditorField(width=800, height=300, toolbars="full", imagePath="../static/images/",
                              filePath="../static/files/",
                              upload_settings={"imageMaxSize": 1204000}, verbose_name='商品介绍')
```
在UEditorField设置中  
width和height分别表示富文本的宽和高  
toolbars表示的是富文本的按钮数量，full表示全部。  
imagePath和filePath表示富文本保存的图片和文件的路径，这是基于`setting.py`中的`MEDIA_ROOT`目录下的，比如MEDIA_ROOT='/static/'，imagePath="/images/"，那么图片就会保存在项目根目录的'/static/images/'下面，'../'表示跳出一级目录。  
4.在APP下的admin.py中，对注册的admin字段进行设置
```
    list_display = ('book_name', 'book_content')
    style_fields = {'book_content': 'ueditor'}
```
5.引入静态文件
 将下载的安装包解压出来，在DjangoUeditor目录下有static和templates两个文件夹，将文件夹的文件全部拷贝到自己项目的static和templates目录下。至此富文本的功能就实现了，可以在后台对富文本内容进行配置了。
 
## 2 admin后台中导入导出功能的实现
`这里的导入导出功能都是基于xlrd，xlwt这两个模块来对Excel进行操作的，所以首先安装这两个模块，版本并无强制要求。`
### 导出功能
导出功能相对来说比较容易实现，甚至某些Django后台框架自带了导出功能，这里就简单说一下。  
利用admin的actions字段来新增一个导出功能的方法。  
首先在`admin.py`下面的`Admin类`里新增`actions`字段，例如
```
actions = [workbook_export]
```
然后去写workbook_export方法
```
def workbook_export(modeladmin, request, queryset):
    if queryset:
        return genarel_workbook_response(request, queryset)
    else:
        pass
```
`这里注意workbook_export只是方法名字，你可以叫别的名字，但一定要和actions字段里的值一致。`
然后可以对自定义的actions起一个名字。
```
workbook_export.short_description = u"导出所选的 书本信息"
```
剩下的就是编写`genarel_workbook_response`方法了。
```
def genarel_workbook_response(request, query_set):
    book = queryset_to_workbook(request, query_set)                     # 生成Excel文件
    stringio = StringIO.StringIO()
    book.save(stringio)                                                 # StringIO流
    response = HttpResponse()
    response['Content-Type'] = 'application/vnd.ms-excel'               # 文件类型
    xls_name = u"书本信息"
    response['Content-Disposition'] = 'attachment;filename={}'.format(u'%s.xls' % xls_name)
    stringio.seek(0)                                                    # 保存流
    response.write(stringio.getvalue())
    return response
```
这里的`xls_name`是返回的Excel名字，可以自己修改，生成Excel方法如下：
```
def queryset_to_workbook(request, queryset):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    if not list(queryset):
        sheet_name = u"空数据"
        book.add_sheet(sheet_name)
        return book
    sheet = book.add_sheet(u'书本信息', cell_overwrite_ok=True)
    sheet.write(0, 0, 'id')
    sheet.write(0, 1, 'keyword')
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i in range(len(queryset)):
        sheet.write(i+1, 0, queryset[i].id)
        sheet.write(i+1, 1, queryset[i].keyword)
    return book
```
至此 ，导出功能就已经实现了，可以在自定义的action中使用了。
### 导入功能
这里根据使用场景不同，分为两种方法。  
首先是新增model的时候，需要对某个字段进行批量导入，比如某个图书类型的时候，顺便批量导入这个类型的图书，常伴随有外键关系。  
这里先要对forms.py，对新增一个字段用来储存Excel的内容。
```
from django import forms
from .views import read_xls
from django.utils.safestring import mark_safe
from .models import Book


class AdminFileWidget(forms.FileInput):
    def __init__(self, attrs={}):
        super(AdminFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = list()
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        output.append(("""<strong>%s</strong>""" % (u'首列填入书名',)))
        return mark_safe(u''.join(output))


class BookAdminForm(forms.ModelForm):
    dict_datas = {}
    books_config = forms.FileField(widget=AdminFileWidget, label=u'书本批量导入', required=False)

    def __init__(self, *args, **kwargs):
        super(BookAdminForm, self).__init__(*args, **kwargs)
        if not kwargs.get('instance', None):
            self.fields['packs_config'] = forms.FileField(widget=AdminFileWidget, label=u'书本批量导入', required=False)

    def clean(self):
        super(BookAdminForm, self).clean()
        if self._errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        try:
            file_path = cleaned_data.get('books_config', )
            if file_path:
                self.dict_datas = read_xls(file_path.temporary_file_path())
        except Exception, e:
            self._errors['books_config'] = self.error_class([u"Excel 格式错误"])
        return cleaned_data

    class Meta:
        model = Book
```
这里创建了`books_config`用来获取上传的Excel文件，用read_xls方法来将Excel文件解析成dict形式，保存到dict_datas当中，下面是read_xls方法的编写。
```
import xlrd


def read_xls(xls_path):
    codes = []
    bk = xlrd.open_workbook(xls_path)
    table = bk.sheets()[0]
    nrows = table.nrows
    for i in range(0, nrows):
        codes.append(table.row_values(i))
    dic_packs = {'codes': codes}
    return dic_packs
```
现在就可以对APP的admin.py进行修改了。  
在admin类下面重写save_model方法
```
    def save_model(self, request, obj, form, change):
        super(BookAdmin, self).save_model(request, obj, form, change)
        try:
            codes = form.dict_datas['codes']
            now_time = datetime.now()
            user_id = request.user.id
            for i in codes:
                code = Book(book_name=i[0], book_content=i[1])
                code.save()
```
这样就保存成功了。  
另外一种场景是单纯想批量创建model，一个个填写太慢了，就用Excel做好内容直接导入。  
这种就需要编写额外的模板文件在后台新增上传按钮，这里不做说明，下面来看如何实现功能。  
首先编写forms.py来对上传的文件做验证。
```
from django import forms


def validate_excel(value):
    if value.name.split('.')[-1] not in ['xls', 'xlsx']:
        raise forms.ValidationError(('Invalid File Type: %(value)s'), params={'value': value},)


class UploadExcelForm(forms.Form):
    excel = forms.FileField(validators=[validate_excel])
```
新增views.py来接收上传的文件。
```
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from datetime import datetime
from .forms import UploadExcelForm
from .models import Book
import xlrd


class ImportView(View):

    def get(self, request):
        return render(request, 'batch_import.html', {})

    def post(self, request, *args, **kwargs):

        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            wb = xlrd.open_workbook(
                filename=None, file_contents=request.FILES['excel'].read())
        table = wb.sheets()[0]
        nrows = table.nrows
        for i in range(nrows):
            value = table.row_values(i)
            try:
                keyword_info = Vocabulary.objects.get(book_name=value[0])
            except:
                obj = Book(book_name=value[0], book_content=value[1])
                obj.save()

        return HttpResponse(u"批量上传成功！已存在的图书将不会重复上传！")
```
同时记得给该views.py设置路由来供后台访问，这样所有的编码就完成了。
