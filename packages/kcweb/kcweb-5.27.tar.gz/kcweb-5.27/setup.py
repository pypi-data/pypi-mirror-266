
# python setup.py sdist upload
# twine upload --repository-url https://test.pypi.org/legacy/ dist/* #上传到测试
# pip install --index-url https://pypi.org/simple/ kcweb   #安装测试服务上的kcweb pip3 install kcweb==4.12.4 -i https://pypi.org/simple/
############################################# 
from setuptools import setup, find_packages,Extension
import os
def file_get_content(k):
    "获取文件内容"
    if os.path.isfile(k):
        f=open(k,'r',encoding="utf-8")
        con=f.read()
        f.close()
    else:
        con=''
    return con
confkcw={}
confkcw['name']='kcweb'                             #项目的名称 
confkcw['version']='5.27'							#项目版本
confkcw['description']='kcweb作为web开发而设计的高性能框架，采用全新的架构思想，注重易用性。遵循MIT开源许可协议发布，意味着个人和企业可以免费使用kcweb，甚至允许把你基于kcweb开发的应用开源或商业产品发布或销售'       #项目的简单描述
confkcw['long_description']="增加 kcweb 命令"     #项目详细描述
confkcw['license']='MIT License'                    #开源协议   mit开源
confkcw['url']=''
confkcw['author']='禄可集团-坤坤'  					 #名字
confkcw['author_email']='fk1402936534@qq.com' 	     #邮件地址
confkcw['maintainer']='坤坤' 						 #维护人员的名字
confkcw['maintainer_email']='fk1402936534@qq.com'    #维护人员的邮件地址
def get_file(folder='./',lists=[]):
    lis=os.listdir(folder)
    for files in lis:
        if not os.path.isfile(folder+"/"+files):
            if files=='__pycache__' or files=='.git':
                pass
            else:
                lists.append(folder+"/"+files)
                get_file(folder+"/"+files,lists)
        else:
            pass
    return lists
b=get_file("kcweb",['kcweb'])
setup(
    name = confkcw["name"],
    version = confkcw["version"],
    keywords = "kcweb"+confkcw['version'],
    description = confkcw["description"],
    long_description = confkcw["long_description"],
    license = confkcw["license"],
    author = confkcw["author"],
    author_email = confkcw["author_email"],
    maintainer = confkcw["maintainer"],
    maintainer_email = confkcw["maintainer_email"],
    url=confkcw['url'],
    packages =  b,
    # data_files=[('Scripts', ['kcweb/bin/kcw.exe'])],
    install_requires = ['gunicorn==20.0.4','pymongo>=3.10.0','Mako>=1.1.2','requests>=2.23.0','six>=1.12.0','watchdog>=0.9.0','websockets==8.1','urllib3==1.25.11'], #第三方包
    package_data = {
        '': ['*.html', '*.js','*.css','*.jpg','*.png','*.gif'],
    },
    entry_points = {
        'console_scripts':[
            'kcweb = kcweb.kcweb:executable'
        ]
    }
)