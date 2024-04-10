from kcweb.common import *
import getopt
PATH=os.getcwd()
sys.path.append(PATH)
import subprocess
def __get_cmd_par():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["project=","app=","modular=","plug=","user=","pwd=","host=","port=","timeout=","processcount=",
        "install","uninstall","pack","upload","cli"])
        # print(opts)
        # print(args)
        server=False
        if 'server' in args:
            server=True
        help=False
        if 'help' in args:
            help=True
       
        project='kcwebplus'  #项目名称
        appname='app'  #应用名
        modular='intapp' #模块名
        plug=''  #插件名
        username=''
        password=''
        host='0.0.0.0'
        port=39001
        timeout='600'
        processcount='4'

        install=False
        uninstall=False
        pack=False
        upload=False
        cli=False
        
        if '--cli' in args:
            cli=True
        i=0
        for data in opts:
            # if '--project' == data[0]:
            #     project=data[1]
            # if '--app' == data[0]:
            #     appname=data[1]
            if '--modular' == data[0]:
                modular=data[1]
            elif '--plug' == data[0]:
                plug=data[1]
            elif '--user' == data[0]:
                username=data[1]
            elif '--pwd' == data[0]:
                password=data[1]
            elif '--host' == data[0]:
                host=data[1]
            elif '--port' == data[0]:
                port=data[1]
            elif '--timeout' == data[0]:
                timeout=data[1]
            elif '--processcount' == data[0]:
                processcount=data[1]
            
            elif '--help' == data[0]:
                help=True
            elif '--install' == data[0]:
                install=True
            elif '--uninstall' == data[0]:
                uninstall=True
            elif '--pack' == data[0]:
                pack=True
            elif '--upload' == data[0]:
                upload=True
            elif '--cli' == data[0]:
                cli=True
            i+=1
    except Exception as e:
        print("\033[1;31;40m有关kcwebplus命令的详细信息，请键入 kcwebplus help",e)
        return False
    else:
        return {
            'server':server,
            'project':project,'appname':appname,'modular':modular,'username':username,'password':password,'plug':plug,'host':host,'port':port,'timeout':timeout,'processcount':processcount,
            'help':help,'install':install,'uninstall':uninstall,'pack':pack,'upload':upload,'cli':cli,
            'index':i
        }
def executable():
    cmd_par=__get_cmd_par()
    if not cmd_par:
        exit()
    if cmd_par['help']:
        try:
            cs=sys.argv[2:][0]
        except:
            cs=None
        print("\033[1;31;40m有关某个命令的详细信息，请键入 kcwebplus help 命令名")
        print("\033[36m执行 kcwebplus help server             可查看server相关命令")
        print("\033[36m执行 kcwebplus help modular                可查看赋值相关命令")
        print("\033[36m执行 kcwebplus help install            可查看安装相关命令")
        print("\033[36m执行 kcwebplus help pack               可查看打包相关命令")
        print("\033[36m执行 kcwebplus help upload             可查看上传相关命令")
        print("\033[36m执行 kcwebplus help uninstall          可查看卸载相关命令\n")
        if 'server' == cs:
            print("\033[32mkcwebplus --host 0.0.0.0 --port 39001 --processcount 4 --timeout=600 server   启动web服务")
            print("\033[32mhost、port、processcount、timeout并不是必须的，如果要使用默认值，您可以使用下面简短的命令来启动服务")
            print("\033[32mkcwebplus server\n")
        if 'modular' == cs:
            print("\033[32mkcwebplus --modular intapp --plug plug --install    进行安装")
            print("\033[1;31;40m初始化一个web应用示例,通常情况下modular、plug、install同时使用")
            print("\033[32mmodular、plug并不是必须的，如果要使用默认值，您可以使用下面简短的命令来安装")
            print("\033[32mkcwebplus install\n")
        if 'install' == cs:
            print("\033[32mkcwebplus --install                                                           安装一个默认的应用")
            print("\033[32mkcwebplus --modular base --install                                  在app应用中安装一个base模块")
            print("\033[32mkcwebplus --modular base --plug plug1 --install                     在app应用base模块中安装一个plug1插件")
            print("\033[32mkcwebplus --modular intapp --plug plug1 --user 181*** --install     在app应用intapp模块中安装一个指定用户的plug1插件")
        if 'pack' == cs:
            print("\033[32mkcwebplus --modular api --pack                打包一个模块")
            print("\033[32mkcwebplus --modular api --plug plug1 --pack   可以打包一个插件\n")
        if 'upload' == cs:
            print("\033[32mkcwebplus --modular intapp --user 181*** --pwd pwd123 --upload                上传一个intapp模块")
            print("\033[32mkcwebplus --modular intapp --plug plug1 --user 181*** --pwd pwd123 --upload   向intapp模块中上传一个plug1插件")
            print("\033[1;31;40m注意：181*** 和 pwd123 是您的用户或密码")
        if 'uninstall' == cs:
            print("\033[32mkcwebplus --modular api --uninstall                  卸载app/api模块")
            print("\033[32mkcwebplus --modular api --plug plug1 --uninstall     卸载app/api/plug1插件\n")
    else:
        # print(cmd_par)
        if cmd_par['cli']:#通过命令行执行控制器的方法
            from kcweb import web
            import app as application
            app=web(__name__,application)
            try:
                RAW_URI=sys.argv[1]
            except:pass
            else:
                if RAW_URI=='--cli':
                    RAW_URI=''
                app.cli(RAW_URI)
        elif cmd_par['server']:#启动web服务
            if get_sysinfo()['uname'][0]=='Linux':
                types=sys.argv[len(sys.argv)-1]
                if types=='-stop' or types=='-start':
                    pass
                else:
                    print("启动参数错误，支持 -start和-stop")
                    exit()
                try:
                    f=open("pid",'r')
                    pid=f.read()
                    f.close()
                    if pid:
                        os.system("kill "+pid)
                except:pass
                if __name__ == 'kcwebplus.kcwebplus':
                    try:
                        Queues.delwhere("code in (2,3)")
                    except:pass
                    if types=='-start':
                        cmd = ['gunicorn','-w', cmd_par['processcount'], '-b', cmd_par['host']+':'+str(cmd_par['port']),'-t',cmd_par['timeout'], 'server:'+cmd_par['appname']]
                        process=subprocess.Popen(cmd)
                        f=open("pid",'w')
                        f.write(str(process.pid))
                        f.close()
                        os.system("nohup kcwebplus intapp/index/pub/clistartplan --cli > server.log 2>&1 &")
                        exit()
            else:
                from kcweb import web
                import app as application
                app=web(__name__,application)
                if __name__ == "kcwebplus.kcwebplus":
                    try:
                        Queues.delwhere("code in (2,3)")
                    except:pass
                    # print(cmd_par)
                    app.run(host=cmd_par['host'],port=int(cmd_par['port']))
        else:
            if cmd_par['install']:#插入 应用、模块、插件
                if cmd_par['appname'] and cmd_par['modular']:
                    if os.path.exists('./'+cmd_par['project']):
                        print(cmd_par['project']+"文件夹已存在")
                        exit()
                    server=create(cmd_par['appname'],cmd_par['modular'],project=cmd_par['project'])
                    t=server.installmodular(cli=True,package='kcwebplus')
                    if cmd_par['plug']:
                        res=server.installplug(cmd_par['plug'],cli=True,username=cmd_par['username'])
                        print(res)
                        if not res[0]:
                            exit()
                    else:
                        if '应用创建成功' in t[1]:
                            if get_sysinfo()['uname'][0]=='Linux':
                                if os.path.exists(cmd_par['project']):
                                    remppath=os.path.split(os.path.realpath(__file__))[0]
                                    # print('remppath',remppath)
                                    if not os.path.isfile("./"+cmd_par['project']+"/server"):
                                        shutil.copy(remppath+'/server',cmd_par['project'])
                                    if not os.path.isfile("./"+cmd_par['project']+"/server.sh"):
                                        shutil.copy(remppath+'/server.sh',cmd_par['project'])
                            print("创建应用成功，接下来进入入项目目录 在终端中执行：kcwebplus server 运行项目")
                        else:
                            print(t)
                else:
                    print("\033[1;31;40m安装时 必须指定应该app和modular，参考命令： kcwebplus --app app --modular api")
                    exit()
            if cmd_par['pack']:#打包 模块、插件
                if cmd_par['appname'] and cmd_par['modular']:
                    server=create(cmd_par['appname'],cmd_par['modular'],project=cmd_par['project'])
                    if cmd_par['plug']:
                        res=server.packplug(plug=cmd_par['plug'])
                    else:
                        res=server.packmodular()
                    print(res)
                    if not res[0]:
                        exit()
                else:
                    print("\033[1;31;40m打包时 必须指定应该app和modular，参考命令： kcwebplus --app app --modular api")
                    exit()
            if cmd_par['upload']:#上传 模块、插件
                if cmd_par['appname'] and cmd_par['modular']:
                    server=create(cmd_par['appname'],cmd_par['modular'],project=cmd_par['project'])
                    if cmd_par['plug']:
                        res=server.packplug(plug=cmd_par['plug'])
                        if res[0]:
                            res=server.uploadplug(cmd_par['plug'],cmd_par['username'],cmd_par['password'],cli=True)
                        else:
                            print(res)
                            exit()
                    else:
                        res=server.packmodular()
                        if res[0]:
                            res=server.uploadmodular(cmd_par['username'],cmd_par['password'],cli=True)
                        else:
                            print(res)
                            exit()
                    print(res)
                    if not res[0]:
                        exit()
                else:
                    print("\033[1;31;40m上传时 必须指定应该app和modular，参考命令： kcwebplus --app app --modular api")
                    exit()
            if cmd_par['uninstall']:#卸载 模块、插件
                if cmd_par['appname'] and cmd_par['modular']:
                    server=create(cmd_par['appname'],cmd_par['modular'],project=cmd_par['project'])
                    if cmd_par['plug']:
                        res=server.uninstallplug(plug=cmd_par['plug'])
                    else:
                        res=server.uninstallmodular()
                    print(res)
                    if not res[0]:
                        exit()
                else:
                    print("\033[1;31;40m卸载时 必须指定应该app和modular，参考命令： kcwebplus --app app --modular api")
                    exit()