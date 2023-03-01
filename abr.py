#!/usr/bin/python3
import sys,re,os,json,shutil,getopt
import webbrowser
from ipa import *
def help():
    readme="""
App Bundle Renamer , IPA包文件重命名,自动分类工具。
用法： abr [源目录] [目标目录] [名称模版] -...

源目录: 放置.ipa文件的原位置
目标目录: 重命名后文件要移动到的位置，默认与源目录相同
名称模版: 可定义参数为<name>:app名称,<version>:app版本,<identifier>app的bundle-identifier。若不了解具体用法保持默认即可
参数：
    -h , --help : 显示本帮助信息
    -w , --web : 打开作者主页 
    -nc , --no-category : 不对

    """
    print (readme)
    sys.exit()

def web():    
    url="https://www.iosr.cc/"
    webbrowser.open(url)
    sys.exit()
    
if __name__ == '__main__':   
    print("App Bundle Renamer \n Code by sikro@52pojie")
    argvs=sys.argv[1:]
    src_dir=dst_dir=template=""
    opt=[]
    for argv in argvs:
        if not argv.startswith("-"):
            if not src_dir:
                src_dir=argv
            elif not dst_dir:
                dst_dir=argv
            elif not template:
                template=argv
        else:
            opt.append(argv[1:])
    #Print help document
    if "h" in opt or "-help" in opt:
        help()
    if "w" in opt or "-web" in opt:
        web()
    
    if not src_dir:        
        src_dir=input('请输入源目录：')        
    else:
        print('源路径:{}'.format(src_dir))
    if not dst_dir:
        dst_dir=src_dir
    print('目标路径:{}'.format(dst_dir))
    if not template:
        template="<name>_<version>@<identifier>.ipa"
    print('命名模版:{}'.format(template))
    try:
        os.chdir(src_dir)
    except Exception as e:
        print(format(e))
        sys.exit()

    #List ipa files
    ipafiles = get_dir_ipa(src_dir)
    if not ipafiles:
        print('[Error] No .ipa files in target dir')
        sys.exit()
    
    #Analyze ipa file infomation
    for file in ipafiles:    
        file_path, file_name = os.path.split(file)
        file_info=analyze_ipa(file) 
        if "n" in opt or "-no-category" in opt:
            dst_file_path=dst_dir
        else:
            bundle_genre=get_ipa_genre(file_info)
            print(bundle_genre)
            dst_file_path=os.path.join(dst_dir,bundle_genre)
    
        #Now begin
        os.makedirs(dst_file_path,exist_ok=True)
        dst_file_name=template.replace("<name>",file_info['CFBundleDisplayName']).replace(    
            "<version>",file_info['CFBundleShortVersionString']).replace("<identifier>",file_info['CFBundleIdentifier'])
        if not dst_file_name.endswith(".ipa"):
            dst_file_name = ".".join(dst_file_name,"ipa")        
        dst_file=os.path.join(dst_file_path,dst_file_name)
        print("{}->{}".format(file_name,dst_file),end="")
        try:
            if os.path.exists(dst_file):
                raise AttributeError('目标文件已存在')
            shutil.move(file, dst_file) 
            print("✅")
        except Exception as e:
            print("❌")
            print(e)
            
