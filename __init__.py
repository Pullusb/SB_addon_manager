bl_info = {
"name": "SB addons manager",
"description": "Allow to download/manage addons of defined repository",
"author": "Samuel Bernou",
"version": (0, 1, 0),
"blender": (2, 80, 0),
"location": "editor > menu/panel > name",
"warning": "WIP, don't expect it to work as for now",
"doc_url": "",
"category": "Development",
}

import bpy
import os
from os.path import exists, join, basename, dirname
import re
import urllib.request
import ast
import json
from distutils.version import LooseVersion, StrictVersion
import addon_utils
from pprint import pprint

def dl_dir(fp):
    '''If fp exists, return path to addon_dl folder inside (create this folder if not exits)'''
    if exists(fp):
        fp = join(fp, 'addons_dl')
        if not exists(fp):
            os.makedirs(fp)
        return fp
    else:
        return None

def unzip(zipadress, delzip=True):
    '''Extract passed zip file in the same directory
    if delzip is True, zip is deleted after extracting.
    '''
    import zipfile
    zip_ref = zipfile.ZipFile(zipadress, 'r')#path_to_zip_file
    zip_ref.extractall(dirname(zipadress))#directory_to_extract_to
    zip_ref.close()
    if delzip:
        os.remove(zipadress)

def gen_filename(url):
    '''Because damn urlib is not capable of just keeping the original filename !(rage)'''
    if url.endswith('.py'):
        return basename(url)
    elif url.endswith('.zip'):
        return url.split('/')[-3] + '.zip'
    else:
        print ('!! not py or zip >>', basename(url))
        return None

def download_addons_from_json(addonslist):
    # Get addon list (maybe later use a yaml or json to keep informations)
    with open(addonslist, 'r') as fd:
        ads = json.load(fd)
    print('ads: ', ads)

    if ads:
        ads = ads['addons']
        from urllib.request import urlretrieve
        basefp = r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager'#os.getcwd()

        fp = dl_dir(basefp)
        os.chdir(fp)
        if not fp:
            raise

        for addon in ads:
            name = addon['name']
            url = addon['url']

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
#rx_version = re.compile(r'(?:\"|\')version(?:\"|\')\s?:\s?\(\s?(\d{1,3})\s?,\s?(\d{1,3})\s?,\s?(\d{1,3})\s?\)')#3 groups
rx_version = re.compile(r'(?:\"|\')version(?:\"|\')\s?:\s?\(\s?(\d{1,3})\s?,\s?(\d{1,3})\s?,\s?(\d{1,3})\s?\)')


    #f'{reversion.group(1)}.{reversion.group(2)}.{reversion.group(3)}'
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

def check_update(addon, url):
    '''check current addon against web'''
    webinfo = get_addon_infos(url)
    if not webinfo:
        print('info not found')
        return
    
    reversion = rx_version(webinfo)
    if reversion:
        if not reversion.group(1):
            print('could not found version group for webversion')
            return
        version = reversion.group(1).replace(',', '.').replace(' ', '')
        print('version: ', version)


    if LooseVersion(version) > LooseVersion(current_version):
        ## Do_stuff
        pass
    else:
        print('current version is OK')


class SBAM_OT_manage_addons(bpy.types.Operator):
    bl_idname = "dev.manage_addons"
    bl_label = "SB addon manager"
    bl_description = "Operator to download / update addon from targeted repository"
    bl_options = {"REGISTER"}

    bpy.types.Scene.line_in_debug_print = bpy.props.BoolProperty(
    name="include line num", description='include line number in print', default=False)

    """ @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR' """

    def execute(self, context):
        ## check list of existing addons 
        # print(self.addons_list)
        '''## for new, non downloaded addons
        #choosing where to put the scripts (addon_utils.paths() give a list of all addons path available)
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
        
        return {"FINISHED"}

    def invoke(self, context, event):
        # get addon list
        jsonfp = join(dirname(__file__), 'addons_listing.json')#in the future point to other lists
        if not exists(jsonfp):
            print(f'Source list not found at : {jsonfp}')
            return {"CANCELLED"}
        
        print(f'loading json: {jsonfp}')
        with open(jsonfp,'r') as fd:
            data_file = json.load(fd)

        self.addon_list = data_file['addons']
        
        # check if web can be accessed (even if not can manage enable/disable ? or different operator)
        pref_addons = bpy.context.preferences.addons
        
        not_there = []
        disabled = []
        enabled = []

        for addon in self.addon_list:
            ## addon keys : name, url, description, sources, demo
            if addon['filename'] not in pref_addons:
                not_there.append(addon['filename'])
                continue
            
            loaded_default, loaded_state = addon_utils.check(addon['filename'])
            print(f"{addon['name']}: load -> default: {loaded_default} state: {loaded_state}")
            
            if not loaded_default:
                disabled.append(addon['filename'])
                continue
            
            enabled.append(addon['filename'])
            # print()
        
        if not not_there and not disabled:
            print('No missing addons or disabled addon !')
        
        print('\nnot_there')
        pprint(not_there)

        print('\ndisabled')
        pprint(disabled)
        
        print('\nenabled')
        pprint(enabled)
        ## if addon not exist yet, ask were to put with addon_utils.paths()
        
        # self.selected_location = event.shift
        return self.execute(context)

# Parsing isn't Working
# info = get_addon_infos(r'https://raw.githubusercontent.com/Pullusb/SB_ActiveSwap/master/SB_Active_swap.py')

#For 2.8


# check if addon are installed:
# addon_utils.check(addon_name) -- return  (loaded_default, loaded_state)


# download_addons_from_json(r'./addons_listing.json')
# download_addons_from_json(r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager\addons_listing.json')

#For 2.7
#download_addons_from_list(r'./addons_links_27.txt')

'''
print(info['name'])
print(info['version'])
'''


#info = get_addon_infos(r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager\addons_links.txt')

#info = get_addon_infos(r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager\addons_dl\SB_1234Select.py')
# i2 = get_addon_infos(r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager\addons_dl\curveRig.py')
# i2 = get_addon_infos(r'G:\WORKS\Prog\blender\SB_Blender_addons\Addons_manager\addons_dl\TapTapSwap.py')
#i2 = get_addon_infos(r'https://raw.githubusercontent.com/Pullusb/SB_ActiveSwap/master/SB_Active_swap.py')


#print(info['version'] > i2['version'])
classes = (
SBAM_OT_manage_addons,
)

### --- REGISTER ---

register, unregister = bpy.utils.register_classes_factory(classes)

'''#detailed
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
'''

if __name__ == "__main__":
    register()