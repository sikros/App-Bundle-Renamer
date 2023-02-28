import zipfile, plistlib,requests
import sys,re,os,json,shutil
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

def query_itunes_id(bundle_id):
    resp=requests.get("https://itunes.apple.com/cn/lookup?bundleId={}".format(bundle_id)) 
    return resp.json()

def query_itunes_name(bundle_name):
    resp=requests.get("https://itunes.apple.com/search?term={}&country=cn&entity=software".format(bundle_name))
    return resp.json()

def get_dir_ipa(work_dir):
    list=[]
    for root,dirs,files in os.walk(work_dir):
        for filename in files:
            if os.path.splitext(filename)[1] == '.ipa':
                list.append(os.path.join(root,filename))
        return list

def get_ipa_genre(file_info):                          
    bundle_info=query_itunes_id(file_info['CFBundleIdentifier'])    
    if bundle_info['resultCount']>0:
        bundle_genre=bundle_info['results'][0]['primaryGenreName']
    else:
        bundle_info=query_itunes_name(file_info['CFBundleDisplayName'])
        if bundle_info['resultCount']>0:
            bundle_genre=bundle_info['results'][0]['primaryGenreName']
        else:
            bundle_genre='Others'
    return bundle_genre


