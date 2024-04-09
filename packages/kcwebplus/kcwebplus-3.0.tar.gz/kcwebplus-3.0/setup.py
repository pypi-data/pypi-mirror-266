
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
confkcw['name']='kcwebplus'                             #项目的名称 
confkcw['version']='3.0'							#项目版本
confkcw['description']='该版本需python版本>=3.8'       #项目的简单描述
confkcw['long_description']="该版本需python版本>=3.8"     #项目详细描述
confkcw['license']='MIT License'                    #开源协议   mit开源
confkcw['url']=''
confkcw['author']='百里-坤坤'  					 #名字
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
b=get_file("kcwebplus",['kcwebplus'])
setup(
    name = confkcw["name"],
    version = confkcw["version"],
    keywords = "kcwebplus"+confkcw['version'],
    description = confkcw["description"],
    long_description = confkcw["long_description"],
    license = confkcw["license"],
    author = confkcw["author"],
    author_email = confkcw["author_email"],
    maintainer = confkcw["maintainer"],
    maintainer_email = confkcw["maintainer_email"],
    url=confkcw['url'],
    packages =  b,
    # data_files=[('Scripts', ['kcwebplus/bin/kcw.exe'])],
    install_requires = ['kcweb>=5.27','pyOpenSSL==23.2.0','chardet==4.0.0','apscheduler==3.6.3','qrcode==6.1','pillow==8.4.0','psutil==5.7.0','oss2==2.12.1','websocket-client==1.3.1'], #第三方包
    package_data = {
        '': ['*.html', '*.js','*.css','*.jpg','*.png','*.gif','server','server.sh'],
    },
    entry_points = {
        'console_scripts':[
            'kcwebplus = kcwebplus.kcwebplus:executable'
        ]
    }
)