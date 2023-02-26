import sys, re , os,json
import zipfile, plistlib
import requests,shutil

def analyze_ipa(ipa_path):
    ipa_file = zipfile.ZipFile(ipa_path)
    plist_path = find_plist_path(ipa_file)
    plist_data = ipa_file.read(plist_path)
    plist_root = plistlib.loads(plist_data)
    return plist_root

def find_plist_path(zip_file):
    name_list = zip_file.namelist()
    pattern = re.compile(r'Payload/[^/]*.app/Info.plist')
    for path in name_list:
        m = pattern.match(path)
        if m is not None:
            return m.group()

def print_ipa_info(plist_root):
    print ('Display Name: %s' % plist_root['CFBundleDisplayName'])
    print ('Bundle Identifier: %s' % plist_root['CFBundleIdentifier'])
    print ('Version: %s' % plist_root['CFBundleShortVersionString'])
    return plist_root['CFBundleDisplayName'],plist_root['CFBundleShortVersionString']

def query_appstore(bundle_id):
    resp=requests.get("https://itunes.apple.com/cn/lookup?bundleId={}".format(bundle_id)) 
    return resp.json()

def get_dir_ipa(work_dir):
    list=[]
    for root,dirs,files in os.walk(work_dir):
        for filename in files:
            if os.path.splitext(filename)[1] == '.ipa':
                list.append(os.path.join(root,filename))
        return list

if __name__ == '__main__':   
    if len(sys.argv) == 1:
        work_dir=input('请输入目录：')        
    else:
        work_dir = sys.argv[1]
    try:
        os.chdir(work_dir)
    except:
        print("No such file or directory")
        exit()
    ipafiles = get_dir_ipa(work_dir)
    if not ipafiles:
        print('Error: Can not find .ipk files in target dir')
        exit()
    

    for file in ipafiles:
        try:            
            file_path, file_name = os.path.split(file)
            file_info=analyze_ipa(file)     
            bundle_info=query_appstore(file_info['CFBundleIdentifier'])       

            if bundle_info['resultCount']>0:
                file_path = os.path.join(file_path,bundle_info['results'][0]['primaryGenreName'].replace(" ",""))
            print(file_path)
            os.makedirs(file_path,exist_ok=True)

            dst_file_name=os.path.join(file_path,"{}_{}@{}.ipa".format(file_info['CFBundleDisplayName'],file_info['CFBundleShortVersionString'],file_info['CFBundleIdentifier']).replace(" ", "_"))
            if os.path.exists(dst_file_name):
                raise AttributeError('目标文件{}已存在'.format(dst_file_name))
            shutil.move(file, dst_file_name.replace(' ',"_"))
 
        except Exception as e:
            print('%s重命名失败:%s'%(file,e))
            
