import os
from os.path import exists, join, basename, dirname
import re
import urllib.request
import ast

def dl_dir(fp):
    if exists(fp):
        fp = join(fp, 'addons_dl')
        if not exists(fp):
            os.makedirs(fp)
        return fp
    else:
        return None

def unzip(zipadress, delzip=True):
    import zipfile
    zip_ref = zipfile.ZipFile(zipadress, 'r')#path_to_zip_file
    zip_ref.extractall(dirname(zipadress))#directory_to_extract_to
    zip_ref.close()
    if delzip:
        os.remove(zipadress)

def gen_filename(url):
    '''because damn urlib is not capable of just keeping the original filename !(rage)'''
    if url.endswith('.py'):
        return basename(url)
    elif url.endswith('.zip'):
        return url.split('/')[-3] + '.zip'
    else:
        print ('!! not py or zip >>', basename(url))
        return None

def download_addons_from_list(urlist):
    # Get addon list (maybe later use a yaml or json to keep informations)
    ads = []
    with open(urlist, 'r') as fd:
        for line in fd:
            if line.strip() and ' -- ' in line and not line.startswith('#'):
                # print (line)
                addon=line.split('--')
                print(addon[0].strip(),'>',addon[1].strip())
                ads.append([addon[0].strip(),addon[1].strip()])


    if ads:
        from urllib.request import urlretrieve
        basefp = dirname(__file__)#os.getcwd()

        fp = dl_dir(basefp)
        os.chdir(fp)
        if not fp:
            raise

        for addon in ads:
            name = addon[0]
            url = addon[1]

            filename = gen_filename(url)
            dfile = join(fp, filename)
            try:
                print('downloading', name)
                urlretrieve(url, dfile)

                if exists(dfile):
                    if url.endswith('.zip'):
                        unzip(dfile)
                else:
                    print("problem ! not found:", dfile)
            except:
                # self.report({'ERROR'}, "Failed to download, maybe check your internet connection?")
                print ("Failed to download, maybe check your internet connection?")
                print ("URL:", url, "\nDownload Path:", dfile)
                #return {'CANCELLED'}

rx = re.compile(r'bl_info ?= ?(\{.*?\})', re.S)
# rx = re.compile(r'bl_info ?= ?\{', re.S)

#download_addons_from_list('liste_liens_addons.txt')
def parse_info(t):
    ''' get bl_infos
    name
    author
    version
    blender
    location
    description
    warning
    wiki_url
    tracker_url
    category
    '''
    rex = rx.search(str(t))
    if rex:
        blinfo_text = rex.group(1)
        #print(blinfo_text)
        #print(type(blinfo_text))
        #print(infodic)

        #infodic = ast.literal_eval(blinfo_text)
        onelined = "'" + blinfo_text.replace('\n', '').replace('   ','').replace('\r','').strip() + "'"
        print('LINE',onelined)
        bl_info = ast.literal_eval(onelined)#may be better but simple
        print(bl_info)
        print(type(bl_info))
        return(bl_info)

    else:
        print('could not match infos')
        return None



def get_addon_infos(adress):
    '''get a url or a file to read and return a dic with infos'''
    info = None
    if adress.startswith('http'):#url
        if adress.endswith('.py'):
            pass#(use raw adress directly)

        elif adress.endswith('.zip'):#means multifile, access init.py to check
            # https://github.com/Pullusb/SceneSettings/archive/master.zip > https://raw.githubusercontent.com/Pullusb/SceneSettings/master/__init__.py
            adress = adress.split('archive/')[0].replace('https://github.com/', 'https://raw.githubusercontent.com/') + 'master/__init__.py'

        elif 'github' in adress: # must be the repo url
            # https://github.com/Pullusb/snippetsLibrary
            adress = adress.replace('https://github.com/', 'https://raw.githubusercontent.com/') + '/master/__init__.py'

        else:#problem
            print ('!! url not py or zip >>', basename(adress))
            return None

        print (adress)
        with urllib.request.urlopen(adress) as response:
            rawtext = response.read()
            # print(rawtext)
            info=parse_info(rawtext)

    else:#local
        with open(adress) as fd:
            rawtext=fd.read()
            info=parse_info(rawtext)

    return info



#For 2.8

'''
#choosing where to put the scripts
#First in script secondary directory if any specified
addon_dir = bpy.context.preferences.filepaths.script_directory
if not addon_dir:

    #Second in roaming directory
    addon_dir = join(bpy.utils.resource_path('USER'), "scripts", "addons")
    if not exists(addon_dir):

        #Last if path not found in local installation addons (alongside native addons)
        addon_dir = join(bpy.utils.resource_path('LOCAL'), "scripts", "addons")

if not exists(addon_dir):
    print("addon directory cannot be found")

'''
# print('__file__: ', __file__)
download_addons_from_list(join(dirname(__file__), 'addons_links.txt'))

#For 2.7
#download_addons_from_list(r'./addons_links_27.txt')


#### TODO
#make a blender version that can instakl auto


'''
Parsing isn't Working
info = get_addon_infos(r'https://raw.githubusercontent.com/Pullusb/SB_ActiveSwap/master/SB_Active_swap.py')
print(info['name'])
print(info['version'])
'''


#info = get_addon_infos(r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager\addons_links.txt')

#info = get_addon_infos(r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager\addons_dl\SB_1234Select.py')
# i2 = get_addon_infos(r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager\addons_dl\curveRig.py')
# i2 = get_addon_infos(r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager\addons_dl\TapTapSwap.py')
#i2 = get_addon_infos(r'https://raw.githubusercontent.com/Pullusb/SB_ActiveSwap/master/SB_Active_swap.py')


#print(info['version'] > i2['version'])
