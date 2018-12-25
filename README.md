# 前言
其实想做这个东西很久了，以前在看过大佬用readme做知识点总结的时候就也想用这个做，刚好最近有机会看了一下markdown的语法，想想干脆现在就动手吧。<br>
做这个东西的主要目的是为了方便自己回顾一些自己用过但不常用的代码和知识点，免得下次再遇到的时候忘记了还要再去查。<br>
前期的目录结构会比较混乱，想到哪里写哪里，可以用Crtl+F进行查找，等后期内容多了，再对内容框架做一个梳理，就这样。<br>

# 目录
> [Django](#django)
>> [1 admin后台中富文本的实现(DjangoUeditor)](#1-admin后台中富文本的实现djangoueditor)
 
# Django
## 1 admin后台中富文本的实现(DjangoUeditor)
 首先下载安装第三方库DjangoUeditor，py2可以直接用pip命令进行安装。因为作者已经很久不更新了，所以不支持py3，想在py3里使用的话请[点此下载](https://codeload.github.com/twz915/DjangoUeditor3/zip/master)安装。  
 下载安装完成后，就可以在项目中进行配置了。这里以一个网上书店APP作为例子，`步骤没有先后，但必须要保证没有遗漏。`  
 1.在项目根目录的`setting.py1文`件的`INSTALLED_APPS`字段中，将DjangoUeditor加入，具体代码如下。  
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
toolbars表示的是富文本的按钮，full表示全部
imagePath和filePath表示富文本保存的图片和文件的路径，这是基于`setting.py`中的`MEDIA_ROOT`目录下的，比如MEDIA_ROOT='/static/'，imagePath="/images/"，那么图片就会保存在项目根目录的'/static/images/'下面，'../'表示跳出一级目录。  
4.在APP下的admin.py中，对注册的admin字段进行设置
```
    list_display = ('book_name', 'book_content')
    style_fields = {'book_content': 'ueditor'}
```
5.引入静态文件
 将下载的安装包解压出来，在DjangoUeditor目录下有static和templates两个文件夹，将文件夹的文件全部拷贝到自己项目的static和templates目录下。至此富文本的功能就实现了，可以在后台对富文本内容进行配置了。

 
