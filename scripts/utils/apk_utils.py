# -*- coding: utf-8 -*-
import os
import xml.dom.minidom
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import SubElement

import click
from click import secho

from utils import cli_utils
from utils import conf_utils
from utils import file_utils
from utils import log_utils
from utils import unity_utils

__author__ = 'Kevin Sun <sun-w@klab.com>'

ANDROID_NS = 'http://schemas.android.com/apk/res/android'


def decompile_apk(source, target_dir, apk_tool="apktool_2.10.0.jar"):
    full_apk_file = file_utils.get_full_path(source)
    target_dir = file_utils.get_full_path(target_dir)
    apk_tool = file_utils.get_full_tool_path(apk_tool)
    if file_utils.exists(target_dir):
        file_utils.del_file_folder(target_dir)
    if not file_utils.exists(target_dir):
        os.makedirs(target_dir)
    cmd = '"%s" -jar -Xms512m -Xmx1024m "%s" -q d -b -f "%s" -o "%s"' % \
          (file_utils.get_java_cmd(), apk_tool, full_apk_file, target_dir)
    ret = cli_utils.exec_cmd(cmd)
    return ret

def decompile_apk_nodex(source, target_dir, apk_tool="apktool_2.10.0.jar"):
    full_apk_file = file_utils.get_full_path(source)
    target_dir = file_utils.get_full_path(target_dir)
    apk_tool = file_utils.get_full_tool_path(apk_tool)
    if file_utils.exists(target_dir):
        file_utils.del_file_folder(target_dir)
    if not file_utils.exists(target_dir):
        os.makedirs(target_dir)
    cmd = '"%s" -jar -Xms512m -Xmx1024m "%s" -s -q d -b -f "%s" -o "%s"' % \
          (file_utils.get_java_cmd(), apk_tool, full_apk_file, target_dir)
    ret = cli_utils.exec_cmd(cmd)
    return ret


def protect_so(so_file, ext=".so"):
    so_file_path = so_file + ext
    so_file_output = so_file + "-npx" + ext
    upx_tool_path = file_utils.get_full_tool_path("kc-upx")
    cmd = '%s --android-shlib -o %s %s' % \
          (upx_tool_path, so_file_output, so_file_path)
    ret = cli_utils.exec_cmd(cmd)
    return ret


def mono_encrypt(path, ver):
    work_dir = os.path.dirname(path)
    decompile_dir = work_dir + "/decompile"
    ret = decompile_apk(path, decompile_dir)
    if ret:
        msg = "[FAIL] decompile fail base_apk:%s decompile dir:%s" % (path, decompile_dir)
        secho(msg, fg='red')
        raise Exception(msg)

    unity_utils.encrypt_unity(ver, decompile_dir)


def recompile_apk(source_folder, apk_file, apk_tool="apktool_2.10.0.jar"):
    ret = 1
    os.chdir(file_utils.cur_dir)
    source_folder = file_utils.get_full_path(source_folder)
    apk_file = file_utils.get_full_path(apk_file)
    apk_tool = file_utils.get_full_tool_path(apk_tool)
    if file_utils.exists(source_folder):
        cmd = '"%s" -jar -Xms2048m -Xmx8192m "%s" -q b -f "%s" -o "%s"' % \
              (file_utils.get_java_cmd(), apk_tool, source_folder, apk_file)
        ret = cli_utils.exec_cmd(cmd)
    else:
        click.secho("[Fail] apk_utils.recompile_apk source folder is not exist:" + source_folder, fg='red')
    return ret


def addapk2dex(apk, dex, dex_tool="dexAdd.jar"):
    dex_tool_path = file_utils.get_full_tool_path(dex_tool)
    cmd = '"%s" -jar -Xms512m -Xmx2048m "%s" "%s" "%s"' % \
          (file_utils.get_java_cmd(), dex_tool_path, apk, dex)
    ret = cli_utils.exec_cmd(cmd)
    return ret


def jar2dex(src_dir, dst_dir, dex_tool="dx.jar"):
    dex_tool_path = file_utils.get_full_tool_path("dx.jar")
    cmd = file_utils.get_java_cmd() + ' -jar -Xms512m -Xmx1024m "%s" --dex --output="%s" ' % (
        dex_tool_path, dst_dir + "/classes.dex")
    for f in os.listdir(src_dir):
        if f.endswith(".jar"):
            cmd = cmd + " " + os.path.join(src_dir, f)
    libs_path = os.path.join(src_dir, "libs")
    if file_utils.exists(libs_path):
        for f in os.listdir(libs_path):
            if f.endswith(".jar"):
                cmd = cmd + " " + os.path.join(src_dir, "libs", f)
    ret = cli_utils.exec_cmd(cmd)
    return ret


def dex2smali(dex_file, target_dir, dex_tool="baksmali-2.5.2.jar"):
    dex_file = file_utils.get_full_path(dex_file)
    bak_smali_tool = file_utils.get_full_tool_path(dex_tool)
    target_dir = file_utils.get_full_path(target_dir)
    if not os.path.exists(dex_file):
        msg = "[Fail] the dexfile is not exists. path:%s" % dex_file
        secho(msg, fg='red')
        raise Exception(msg)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    cmd = '"%s" -jar "%s" disassemble -o "%s" "%s"' % (file_utils.get_java_cmd(), bak_smali_tool, target_dir, dex_file)
    ret = cli_utils.exec_cmd(cmd)
    return ret


def smali2dex(source_dir, dex_file, dex_tool="smali-2.5.2.jar"):
    dex_file = file_utils.get_full_path(dex_file)
    dex_tool = file_utils.get_full_tool_path(dex_tool)
    source_dir = file_utils.get_full_path(source_dir)
    if not os.path.exists(source_dir):
        msg = "[Fail] the smali folder is not exists. path:%s" % source_dir
        secho(msg, fg='red')
        raise Exception(msg)
    cmd = '"%s" -jar "%s" assemble -o "%s" "%s"' % (file_utils.get_java_cmd(), dex_tool, dex_file, source_dir)
    ret = cli_utils.exec_cmd(cmd)
    return ret


def rename_third_package_name(decompile_dir, package_name):
    android_manifest_file = decompile_dir + "/AndroidManifest.xml"
    android_manifest_file = file_utils.get_full_path(android_manifest_file)
    ET.register_namespace('android', ANDROID_NS)
    tree = ET.parse(android_manifest_file)
    root = tree.getroot()
    application_node = root.find('application')
    activity_node_list = application_node.findall('activity')
    if activity_node_list is not None:
        for a_node in activity_node_list:
            # 替换查找qq钱包等类的标记的 scheme属性
            filter_nodes = a_node.findall('intent-filter')
            if filter_nodes is not None:
                for if_node in filter_nodes:
                    _fixed_wallet(if_node.find('data'), package_name)

            # 替换微信taskAffinity属性
            aff_key = '{' + ANDROID_NS + '}taskAffinity'
            affiTask = a_node.get(aff_key)
            if affiTask is not None:
                a_node.set(aff_key, affiTask.replace('{packagename}', package_name))

            # 替换微信name属性
            name_key = '{' + ANDROID_NS + '}name'
            nameTask = a_node.get(name_key)
            if nameTask is not None:
                a_node.set(name_key, nameTask.replace('{packagename}', package_name))

    # 处理provide 特殊包名
    provider_node_list = application_node.findall('provider')
    if provider_node_list is not None:
        for p_node in provider_node_list:
            key = '{' + ANDROID_NS + '}authorities'
            auth_val = p_node.get(key)
            if auth_val is not None:
                p_node.set(key, auth_val.replace('{packagename}', package_name))

    # 处理receiver 特殊包名
    receiver_node_list = application_node.findall('receiver')
    if receiver_node_list is not None:
        for r_node in receiver_node_list:
            filter_node = r_node.find('intent-filter')
            if filter_node is not None:
                _fixed_category(filter_node.find('category'), package_name)

    # 处理service 特殊包名
    service_node_list = application_node.findall('service')
    if service_node_list is not None:
        for s_node in service_node_list:
            filter_node = s_node.find('intent-filter')
            if filter_node is not None:
                _fixed_category(filter_node.find('action'), package_name)

    tree.write(android_manifest_file, 'UTF-8')


def rename_package_name(channel_config, decompile_dir, is_release=True):
    channel_id = channel_config.get('id', '1')
    new_package_name = channel_config.get('suffix', '')
    android_manifest_file = decompile_dir + "/AndroidManifest.xml"
    android_manifest_file = file_utils.get_full_path(android_manifest_file)
    ET.register_namespace('android', ANDROID_NS)
    tree = ET.parse(android_manifest_file)
    root = tree.getroot()
    old_package_name = root.get('package')
    if new_package_name:
        if new_package_name.startswith("."):
            if is_release:
                new_package_name = old_package_name + new_package_name
            else:
                new_package_name = old_package_name + ".debug" + new_package_name
    else:
        # 没有设置新的package name,暂还使用老的做package name
        if is_release:
            new_package_name = old_package_name
        else:
            new_package_name = old_package_name + ".debug"
    secho("[INFO] rename package name, old package name:%s, new package name:%s" % (old_package_name, new_package_name))
    # check activity or service
    application_node = root.find('application')
    if application_node is not None and len(application_node) > 0:
        # 修正activity 的名称
        activity_node_list = application_node.findall('activity')
        if activity_node_list is not None:
            for a_node in activity_node_list:
                _fixed_name(a_node, old_package_name, new_package_name, False)

                # if channel_id == '5':
                #     l_mode = '{' + ANDROID_NS + '}launchMode'
                #     l_label = '{' + ANDROID_NS + '}label'
                #     mode_name = a_node.get(l_mode)
                #     l_name = a_node.get(l_label)
                #     if mode_name is not None and l_name is not None:
                #         a_node.set(l_mode, 'singleTop')

                # 修正intent-filter 中data的值 
                filter_node = a_node.findall('intent-filter')
                if filter_node is not None:
                    scheme_key = '{' + ANDROID_NS + '}scheme'
                    for f_node in filter_node:
                        data_node = f_node.find('data')
                        if data_node is not None and data_node.get(scheme_key) is not None:
                            data_node.set(scheme_key,
                                          data_node.get(scheme_key).replace(old_package_name, new_package_name))

        # 修正service的名称
        service_node_list = application_node.findall('service')
        if service_node_list is not None:
            for s_node in service_node_list:
                _fixed_name(s_node, old_package_name, new_package_name)
                _fixed_authorities(s_node, old_package_name, new_package_name)
                _fixed_intent(s_node, old_package_name, new_package_name)
        # 修正receiver
        receiver_node_list = application_node.findall('receiver')
        if receiver_node_list is not None:
            for r_node in receiver_node_list:
                _fixed_name(r_node, old_package_name, new_package_name)
                _fixed_authorities(r_node, old_package_name, new_package_name)
                _fixed_intent(r_node, old_package_name, new_package_name)
        # 修正provider
        provider_node_list = application_node.findall('provider')
        if provider_node_list is not None:
            for p_node in provider_node_list:
                _fixed_name(p_node, old_package_name, new_package_name)
                _fixed_authorities(p_node, old_package_name, new_package_name)
                _fixed_intent(p_node, old_package_name, new_package_name)

    # 修复权限文件
    p_node_name = '{' + ANDROID_NS + '}name'
    permission_node = root.findall("permission")
    if permission_node is not None and len(permission_node) > 0:
        for p_node in permission_node:
            p_node.set(p_node_name, p_node.get(p_node_name).replace(old_package_name, new_package_name))

    user_permission_node = root.findall("uses-permission")
    if user_permission_node is not None and len(user_permission_node) > 0:
        for up_node in user_permission_node:
            up_node.set(p_node_name, up_node.get(p_node_name).replace(old_package_name, new_package_name))

    root.set('package', new_package_name)
    tree.write(android_manifest_file, 'UTF-8')
    return new_package_name


def _fixed_name(el_node, package_name, new_package_name, need_replace=True):
    key = '{' + ANDROID_NS + '}name'
    name = el_node.get(key)
    # support old xiaomi push
    if name is not None and 'MiPushMessageReceiver' not in name and 'PushAutoRunReceiver' not in name:
        if name.startswith("."):
            name = package_name + name
        elif name.find(".") == -1:
            name = package_name + "." + name

        if need_replace:
            name = name.replace(package_name, new_package_name)

        el_node.set(key, name)


def _fixed_authorities(el_node, package_name, new_package_name):
    key = '{' + ANDROID_NS + '}authorities'
    name = el_node.get(key)
    if name is not None:
        if name.startswith("."):
            name = package_name + name
        elif name.find(".") == -1:
            name = package_name + "." + name

        name = name.replace(package_name, new_package_name)
        el_node.set(key, name)


def _fixed_intent(el_node, package_name, new_package_name):
    filter_node = el_node.findall('intent-filter')
    if filter_node is not None:
        scheme_key = '{' + ANDROID_NS + '}scheme'
        for f_node in filter_node:
            data_node = f_node.find('data')
            if data_node is not None and data_node.get(scheme_key) is not None:
                data_node.set(scheme_key,
                              data_node.get(scheme_key).replace(package_name, new_package_name))

            action_node = f_node.findall('action')
            name_key = '{' + ANDROID_NS + '}name'
            if action_node is not None:
                for a_node in action_node:
                    if a_node.get(name_key) is not None:
                        a_node.set(name_key,
                                   a_node.get(name_key).replace(package_name, new_package_name))


def _fixed_wallet(el_node, package_name):
    key = '{' + ANDROID_NS + '}scheme'
    key_host = '{' + ANDROID_NS + '}host'
    if el_node is not None:
        scheme_val = el_node.get(key)
        if scheme_val is not None:
            el_node.set(key, scheme_val.replace('{packagename}', package_name))

        host_val = el_node.get(key_host)
        if host_val is not None:
            el_node.set(key_host, host_val.replace('{packagename}', package_name))


def _fixed_category(el_node, package_name):
    key = '{' + ANDROID_NS + '}name'
    if el_node is not None:
        cate_val = el_node.get(key)
        if cate_val is not None:
            el_node.set(key, cate_val.replace('{packagename}', package_name))


def add_splash_screen(work_dir, channel, decompile_dir):
    """
        if the splash attrib is not zero ,then set the splash activity
        if the splash_copy_to_unity attrib is set, then copy the splash img to unity res fold ,replace the default splash.png.

    """

    # lenovo speicl process
    if channel['id'] == '11':
        change_start_activity(decompile_dir)
        return 0

    if channel['splash'] == '0':
        return 0

    if channel['splash_copy_to_unity'] == '1':
        return copy_splash_to_unity_res_folder(work_dir, channel, decompile_dir)

    # splash_path = file_utils.get_splash_path()

    # splash_layout_path = splash_path + "/avalon_splash.xml"
    # splash_target_path = decompile_dir + "/res/layout/avalon_splash.xml"
    # file_utils.copy_files(splash_layout_path, splash_target_path)

    res_path = work_dir + "/sdk/" + channel['name'] + "/splash/" + channel['splash']
    res_target_path = decompile_dir + "/res"
    copy_res_to_apk(res_path, res_target_path)

    # remove original launcher activity of the game
    activity_name = remove_start_activity(decompile_dir)

    # append the launcher activity with the splash activity
    append_splash_activity(decompile_dir, channel['splash'])

    splash_activity_path = os.path.join(decompile_dir, "smali") + "/com/avalon/sdk/SplashActivity.smali"
    f = open(splash_activity_path, 'r+')
    content = str(f.read())
    f.close()

    replace_txt = '{AVALONSDK_Game_Activity}'

    idx = content.find(replace_txt)
    if idx == -1:
        log_utils.error("modify splash file failed.the {AVALONSDK_Game_Activity} not found in SplashActivity.smali")
        return 1

    content = content[:idx] + activity_name + content[(idx + len(replace_txt)):]
    f2 = open(splash_activity_path, 'w')
    f2.write(content)
    f2.close()

    log_utils.info("modify splash file success.")
    return 0


def append_splash_activity(decompile_dir, splash_type):
    manifest_file = decompile_dir + "/AndroidManifest.xml"
    manifest_file = file_utils.get_full_path(manifest_file)
    ET.register_namespace('android', ANDROID_NS)
    key = '{' + ANDROID_NS + '}name'
    screenkey = '{' + ANDROID_NS + '}screenOrientation'
    theme = '{' + ANDROID_NS + '}theme'
    tree = ET.parse(manifest_file)
    root = tree.getroot()

    application_node = root.find('application')
    if application_node is None:
        return

    splash_node = SubElement(application_node, 'activity')
    splash_node.set(key, 'com.avalon.sdk.SplashActivity')
    splash_node.set(theme, '@android:style/Theme.Black.NoTitleBar.Fullscreen')

    if splash_type == '1':
        splash_node.set(screenkey, 'landscape')
    else:
        splash_node.set(screenkey, 'portrait')

    intent_node = SubElement(splash_node, 'intent-filter')
    action_node = SubElement(intent_node, 'action')
    action_node.set(key, 'android.intent.action.MAIN')
    category_node = SubElement(intent_node, 'category')
    category_node.set(key, 'android.intent.category.LAUNCHER')
    tree.write(manifest_file, 'UTF-8')


# only for lenovo
def change_start_activity(decompile_dir):
    manifest_file = decompile_dir + "/AndroidManifest.xml"
    manifest_file = file_utils.get_full_path(manifest_file)
    ET.register_namespace('android', ANDROID_NS)
    key = '{' + ANDROID_NS + '}name'

    tree = ET.parse(manifest_file)
    root = tree.getroot()

    application_node = root.find('application')
    if application_node is None:
        return

    activity_node_list = application_node.findall('activity')
    if activity_node_list is None:
        return

    activity_name = ''

    for activity_node in activity_node_list:
        b_is_main_activity = False
        if activity_node.attrib[key] == 'com.youzhe.penguin.PenguinActivity':
            b_is_main_activity = True

        b_main = False
        intent_node_list = activity_node.findall('intent-filter')
        if intent_node_list is None:
            break

        for intent_node in intent_node_list:
            b_find_action = False
            b_find_category = False

            action_node_lst = intent_node.findall('action')
            if action_node_lst is None:
                break
            for action_node in action_node_lst:
                if action_node.attrib[key] == 'android.intent.action.MAIN':
                    b_find_action = True
                    break

            category_node_lst = intent_node.findall('category')
            if category_node_lst is None:
                break
            for categoryNode in category_node_lst:
                if categoryNode.attrib[key] == 'android.intent.category.LAUNCHER':
                    b_find_category = True
                    break

            if b_find_action and b_find_category and b_is_main_activity:
                b_main = True
                intent_node.remove(action_node)
                intent_node.remove(categoryNode)
                lenovo_main_node = SubElement(intent_node, 'action')
                lenovo_main_node.set(key, 'lenovoid.MAIN')
                cat_node = SubElement(intent_node, 'category')
                cat_node.set(key, 'android.intent.category.DEFAULT')
                break

        if b_main:
            activity_name = activity_node.attrib[key]
            break

    tree.write(manifest_file, 'UTF-8')
    return activity_name


def remove_start_activity(decompile_dir):
    manifest_file = decompile_dir + "/AndroidManifest.xml"
    manifest_file = file_utils.get_full_path(manifest_file)
    ET.register_namespace('android', ANDROID_NS)
    key = '{' + ANDROID_NS + '}name'

    tree = ET.parse(manifest_file)
    root = tree.getroot()

    application_node = root.find('application')
    if application_node is None:
        return

    activity_node_list = application_node.findall('activity')
    if activity_node_list is None:
        return

    activity_name = ''

    for activity_node in activity_node_list:
        b_main = False
        intent_node_list = activity_node.findall('intent-filter')
        if intent_node_list is None:
            break

        for intent_node in intent_node_list:
            b_find_action = False
            b_find_category = False

            action_node_lst = intent_node.findall('action')
            if action_node_lst is None:
                break
            for action_node in action_node_lst:
                if action_node.attrib[key] == 'android.intent.action.MAIN':
                    b_find_action = True
                    break

            category_node_lst = intent_node.findall('category')
            if category_node_lst is None:
                break
            for categoryNode in category_node_lst:
                if categoryNode.attrib[key] == 'android.intent.category.LAUNCHER':
                    b_find_category = True
                    break

            if b_find_action and b_find_category:
                b_main = True
                intent_node.remove(action_node)
                intent_node.remove(categoryNode)
                break

        if b_main:
            activity_name = activity_node.attrib[key]
            break

    tree.write(manifest_file, 'UTF-8')
    return activity_name


def copy_splash_to_unity_res_folder(workDir, channel, decompile_dir):
    splash_path = file_utils.get_splash_path()
    res_path = workDir + "/config/splash/" + channel['name'] + "/%s/avalon_splash.png"
    res_target_path = decompile_dir + "/assets/bin/Data/splash.png"

    paths = ['drawable', 'drawable-hdpi', 'drawable-ldpi', 'drawable-mdpi', 'drawable-xhdpi', 'drawable-xxhdpi',
             'drawable-xxxhdpi']

    b_found = False
    for path in paths:
        img_path = res_path % path
        if os.path.exists(img_path):
            res_path = img_path
            b_found = True
            break

    if not b_found:
        log_utils.error("the avalon_splash is not found.path:%s", res_path)
        return 1

    if not os.path.exists(res_target_path):
        log_utils.error("the avalon_splash is not exists. path:%s", res_target_path)
        return 1

    file_utils.copy_file(res_path, res_target_path)

    return 0


def merge_manifest(channel_config, source_manifest, target_manifest):
    if not file_utils.exists(source_manifest) or not file_utils.exists(target_manifest):
        raise Exception(
            "merge manifest the manifest file is not exists.targetManifest:%s;sdkManifest:%s" % (
                target_manifest, source_manifest))
    ET.register_namespace('android', ANDROID_NS)
    target_tree = ET.parse(target_manifest)
    target_root = target_tree.getroot()
    ET.register_namespace('android', ANDROID_NS)
    source_tree = ET.parse(source_manifest)
    source_root = source_tree.getroot()

    with open(target_manifest, 'r') as stream:
        target_manifest_content = stream.read()
    permission_config_node = source_root.find('permissionConfig')
    if permission_config_node is not None and len(permission_config_node) > 0:
        for child in list(permission_config_node):
            key = '{' + ANDROID_NS + '}name'
            val = child.get(key)
            if val is not None and len(val) > 0:
                find_index = target_manifest_content.find(val)
                if find_index == -1:
                    target_root.append(child)
    source_app_config_node = source_root.find('applicationConfig')
    app_node = target_root.find('application')
    if source_app_config_node is not None:
        proxy_application_name = source_app_config_node.get('proxyApplication')
        if proxy_application_name is not None and len(proxy_application_name) > 0:
            if 'AVALON_APPLICATION_PROXY_NAME' in channel_config:
                channel_config['AVALON_APPLICATION_PROXY_NAME'] = \
                    channel_config['AVALON_APPLICATION_PROXY_NAME'] + "," + proxy_application_name
            else:
                channel_config['AVALON_APPLICATION_PROXY_NAME'] = proxy_application_name
        # keyword do nothing
        # app_keyword = source_app_config_node.get('keyword')
        # 取applicationConfig 下的子节点
        for child in list(source_app_config_node):
            app_node.append(child)
    target_tree.write(target_manifest, 'UTF-8')
    # formater Androidmenifest.xml


def copy_shared_libs(src_dir, dst_dir):
    if not file_utils.exists(src_dir):
        secho("[NOTICE] copy shared lib the src dir is not exit,src dir:%s" % src_dir)
        return
    if not file_utils.exists(dst_dir):
        os.makedirs(dst_dir)
    for f in os.listdir(src_dir):
        source_file = os.path.join(src_dir, f)
        target_file = os.path.join(dst_dir, f)
        if os.path.isdir(source_file):
            copy_shared_libs(source_file, target_file)
        else:
            if source_file.endswith(".jar"):
                continue
            else:
                if not file_utils.exists(target_file) or os.path.getsize(target_file) != os.path.getsize(source_file):
                    with open(source_file, 'rb') as from_stream:
                        with open(target_file, 'wb') as to_stream:
                            to_stream.write(from_stream.read())


def copy_res_to_apk(copy_from, copy_to):
    if not file_utils.exists(copy_from):
        secho("[NOTICE] copy res to apk the src dir is not exit,src dir:%s'" % copy_from, fg='yellow')
        return
    if not file_utils.exists(copy_to):
        os.makedirs(copy_to)
    if os.path.isfile(copy_from) and not merge_res_xml(copy_from, copy_to):
        file_utils.copy_files(copy_from, copy_to)
        return
    for f in os.listdir(copy_from):
        source_file = os.path.join(copy_from, f)
        target_file = os.path.join(copy_to, f)
        if os.path.isdir(source_file):
            copy_res_to_apk(source_file, target_file)
        elif os.path.isfile(source_file):
            # 先执行合并
            merge_ret = merge_res_xml(source_file, target_file)
            if merge_ret:
                continue
            base_dir = os.path.dirname(target_file)
            if not file_utils.exists(base_dir):
                os.makedirs(base_dir)
            if not file_utils.exists(target_file) or os.path.getsize(target_file) != os.path.getsize(source_file):
                with open(target_file, 'wb') as target_stream:
                    with open(source_file, 'rb') as source_stream:
                        target_stream.write(source_stream.read())


def merge_res_xml(source_xml_file, dst_xml_file):
    if not file_utils.exists(dst_xml_file):
        # 目标文件不存在, 不要合并
        return False
    res_xml_list = ['strings.xml', 'styles.xml', 'colors.xml', 'dimens.xml', 'ids.xml', 'attrs.xml', 'integers.xml',
                    'arrays.xml', 'bools.xml', 'drawables.xml', 'temp']
    file_base_name = os.path.basename(source_xml_file)
    if file_base_name in res_xml_list:
        with open(dst_xml_file, 'r') as stream:
            target_content = stream.read()
            source_tree = ET.parse(source_xml_file)
            source_root = source_tree.getroot()
            dst_tree = ET.parse(dst_xml_file)
            dst_root = dst_tree.getroot()
            for node in list(source_root):
                val = node.get('name')
                if val is not None and len(val) > 0:
                    val_matched = '"' + val + '"'
                    index = target_content.find(val_matched)
                    if index == -1:
                        dst_root.append(node)
                    else:
                        secho("[INFO] the node %s is already exists in %s" % (val, file_base_name))
        dst_tree.write(dst_xml_file, 'UTF-8')
        return True
    return False


def append_params_to_manifest(channel_config, decompile_dir):
    android_manifest_path = os.path.join(decompile_dir, "AndroidManifest.xml")
    android_manifest_path = file_utils.get_full_path(android_manifest_path)
    ET.register_namespace('android', ANDROID_NS)
    tree = ET.parse(android_manifest_path)
    root = tree.getroot()
    key = '{' + ANDROID_NS + '}name'
    val = '{' + ANDROID_NS + '}value'
    application_node = root.find('application')
    if application_node is None:
        return
    channel_param_dict = {}
    for param in channel_config['params']:
        channel_param_dict[param['name']] = param
    third_plugin_dict = {}
    if 'third-plugins' in channel_config and channel_config['third-plugins'] is not None:
        for third_plugin in channel_config['third-plugins']:
            if 'params' in third_plugin and third_plugin['params'] is not None:
                for param in third_plugin['params']:
                    third_plugin_dict[param['name']] = param
    meta_data_list = application_node.findall('meta-data')
    if meta_data_list is not None:
        for meta_data_node in meta_data_list:
            name = meta_data_node.get(key)
            if name in channel_param_dict and channel_param_dict[name]['bWriteInManifest'] == "1":
                secho("[NOTICE] the meta-data node %s repeated. remove it ." % name, fg='yellow')
                application_node.remove(meta_data_node)
            if name in third_plugin_dict and third_plugin_dict[name]['bWriteInManifest'] == "1":
                secho("[NOTICE] the meta-data node %s repeated. remove it ." % name, fg='yellow')
                application_node.remove(meta_data_node)
    for param in channel_config['params']:
        if param['bWriteInManifest'] is not None and param['bWriteInManifest'] == "1":
            metadata_node = SubElement(application_node, 'meta-data')
            metadata_node.set(key, param['name'])
            metadata_node.set(val, param['value'])
    if 'third-plugins' in channel_config and channel_config['third-plugins'] is not None:
        for plugin in channel_config['third-plugins']:
            if 'params' in plugin and plugin['params'] is not None:
                for param in plugin['params']:
                    if 'bWriteInManifest' in param and param['bWriteInManifest'] == "1":
                        metadata_node = SubElement(application_node, 'meta-data')
                        metadata_node.set(key, param['name'])
                        metadata_node.set(val, param['value'])
    if 'AVALON_APPLICATION_PROXY_NAME' in channel_config:
        metadata_node = SubElement(application_node, 'meta-data')
        metadata_node.set(key, "AVALON_APPLICATION_PROXY_NAME")
        metadata_node.set(val, channel_config['AVALON_APPLICATION_PROXY_NAME'])
    tree.write(android_manifest_path, 'UTF-8')
    format_xml_pretty(android_manifest_path)


def rename_application_in_manifest(channel_config, decompile_dir):
    if "application_name" not in channel_config:
        return
    manifest_file = decompile_dir + "/AndroidManifest.xml"
    manifest_file = file_utils.get_full_path(manifest_file)
    ET.register_namespace('android', ANDROID_NS)
    tree = ET.parse(manifest_file)
    root = tree.getroot()
    app_node = root.find('application')
    if app_node is None:
        return
    key = '{' + ANDROID_NS + '}name'
    app_name = root.get(key)
    if app_name is None or app_name != channel_config['application_name']:
        app_node.set(key, channel_config['application_name'])
    tree.write(manifest_file, 'UTF-8')


def get_iconname_in_manifest(decompile_dir):
    manifestFile = decompile_dir + "/AndroidManifest.xml"
    manifestFile = file_utils.get_full_path(manifestFile)
    ET.register_namespace('android', ANDROID_NS)
    tree = ET.parse(manifestFile)
    root = tree.getroot()
    iconname = None;
    # now to check activity or service
    appNode = root.find('application')
    if appNode != None:
        key = '{' + ANDROID_NS + '}icon'
        iconname = appNode.attrib[key]
        iconname = iconname[iconname.index('/') + 1:]

    return iconname


def write_developer_info(game_config, channel_config, decompile_dir):
    develop_config_path = os.path.join(decompile_dir, "assets/developer_config.properties")
    base_dir = os.path.dirname(develop_config_path)
    if not file_utils.exists(base_dir):
        os.makedirs(base_dir)
    develop_config_path = file_utils.get_full_path(develop_config_path)
    props = ""
    if "params" in channel_config and channel_config["params"] is not None:
        for param in channel_config["params"]:
            if param["bWriteInClient"] == "1":
                props = props + param['name'] + "=" + param['value'] + "\n"
    if "sdkLogicVersionName" in channel_config:
        props = props + "AVALON_SDK_VERSION_CODE=" + channel_config['sdkLogicVersionName'] + "\n"
    props = props + "Avalon_Channel=" + channel_config['id'] + "\n"
    props = props + "AVALON_APPID=" + game_config['appID'] + "\n"
    props = props + "AVALON_APPKEY=" + game_config['appKey'] + "\n"
    props = props + "Avalon_Channel_Name=" + channel_config['platform_name'] + "\n"
    avalon_config = conf_utils.load_avalon_config()
    props = props + "Avalon_Client_Version=" + avalon_config['avalon_bundle_version'] + "\n"
    if avalon_config['use_avalon_auth'] == "1":
        props = props + "AVALON_AUTH_URL=" + avalon_config["avalon_auth_url"] + "\n"
        props = props + "AVALON_SERVER_URL=" + avalon_config["avalon_server_url"] + "\n"
    if "third-plugins" in channel_config:
        third_plugins = channel_config['third-plugins']
        for plugin in third_plugins:
            if 'params' in plugin and plugin['params'] is not None:
                for param in plugin['params']:
                    if param['bWriteInClient'] == "1":
                        props = props + param['name'] + "=" + param['value'] + "\n"
    with open(develop_config_path, 'wb') as stream:
        props = props.encode('UTF-8')
        stream.write(props)


def write_plugin_info(game_config, channel_config, decompile_dir):
    plugin_config_path = os.path.join(decompile_dir, "assets/plugin_config.xml")
    base_dir = os.path.dirname(plugin_config_path)
    if not file_utils.exists(base_dir):
        os.makedirs(base_dir)
    plugin_xml_root = Element('plugins')
    plugin_xml_tree = ElementTree(plugin_xml_root)
    if "plugins" in channel_config and channel_config['plugins'] is not None:
        for plugin in channel_config['plugins']:
            el = SubElement(plugin_xml_root, 'plugin')
            el.set('name', plugin['name'])
            el.set('type', plugin['type'])
    if "third-plugins" in channel_config and channel_config['third-plugins'] is not None:
        for plugin in channel_config['third-plugins']:
            el = SubElement(plugin_xml_root, 'plugin')
            el.set('name', plugin['name'])
            el.set('type', plugin['type'])
    plugin_xml_tree.write(plugin_config_path, 'UTF-8')


def check_cpu_support(game_config, decompile_dir):
    secho("[INFO] now checking the cpu support")
    cpus = ["armeabi", "armeabi-v7a", "x86", "mips", "arm64-v8a"]
    if 'cpuSupport' in game_config and game_config['cpuSupport']:
        filters = game_config['cpuSupport'].split('|')
        cpus_not_support = [c for c in cpus if c not in filters]
        if cpus_not_support:
            for c in cpus_not_support:
                # 删除不支持的so 共享库
                path = os.path.join(decompile_dir, "lib/%s" % c)
                file_utils.del_file_folder(path)
    armeabi_path = os.path.join(decompile_dir, 'lib/armeabi')
    armeabiv7a_path = os.path.join(decompile_dir, 'lib/armeabi-v7a')
    if file_utils.exists(armeabi_path) and file_utils.exists(armeabiv7a_path):
        for f in os.listdir(armeabi_path):
            fv7 = os.path.join(armeabiv7a_path, f)
            if not file_utils.exists(fv7):
                file_utils.copy_files(os.path.join(armeabi_path, f), fv7)
        for fv7 in os.listdir(armeabiv7a_path):
            f = os.path.join(armeabi_path, fv7)
            if not file_utils.exists(f):
                file_utils.copy_files(os.path.join(armeabiv7a_path, fv7), f)

        # 保留v7a 和 armeabi 保留v7a
        file_utils.del_file_folder(armeabi_path)


def modify_game_name(channel_config, decompile_dir):
    secho("[INFO] now modify game name")
    if 'gameName' not in channel_config:
        return
    mani_fest_file = decompile_dir + "/AndroidManifest.xml"
    mani_fest_file = file_utils.get_full_path(mani_fest_file)
    ET.register_namespace('android', ANDROID_NS)
    tree = ET.parse(mani_fest_file)
    root = tree.getroot()
    label_key = '{' + ANDROID_NS + '}label'
    app_node = root.find('application')
    app_node.set(label_key, channel_config['gameName'])
    secho("[OK] the new game name is %s" % channel_config['gameName'])
    tree.write(mani_fest_file, 'UTF-8')


# 处理 strings.xml和colors.xml,如果在其它资源文件里有重复记录,则删除其它资源中重复的记录
def handle_duplicated_value_res(decompile_dir):
    val_xmls = ['strings.xml', 'styles.xml', 'colors.xml', 'dimens.xml', 'ids.xml', 'attrs.xml', 'integers.xml',
                'arrays.xml', 'bools.xml', 'drawables.xml', 'public.xml']
    res_dir = decompile_dir + '/res/values'
    exists_strs = {}
    strings_xml = res_dir + '/strings.xml'
    if os.path.exists(strings_xml):
        string_tree = ET.parse(strings_xml)
        root = string_tree.getroot()
        for node in list(root):
            string_item = {}
            name = node.get('name')
            val = node.text
            string_item['file'] = strings_xml
            string_item['name'] = name
            string_item['value'] = val
            exists_strs[name] = string_item
    exists_colors = {}
    colors_xml = res_dir + 'colors.xml'
    if os.path.exists(colors_xml):
        color_tree = ET.parse(colors_xml)
        root = color_tree.getroot()
        for node in list(root):
            color_item = {}
            name = node.get('name')
            val = node.text.lower()
            color_item['file'] = colors_xml
            color_item['name'] = name
            color_item['value'] = val
            exists_colors[name] = color_item
    value_files = {}
    for filename in os.listdir(res_dir):
        if filename in val_xmls:
            continue
        src_file = os.path.join(res_dir, filename)
        if os.path.splitext(src_file)[1] != '.xml':
            continue
        tree = ET.parse(src_file)
        root = tree.getroot()
        if root.tag != 'resources':
            continue
        for node in list(root):
            dict_res = None
            if node.tag == 'string':
                dict_res = exists_strs
            elif node.tag == 'color':
                dict_res = exists_colors
            else:
                continue
            name = node.get('name')
            val = node.text
            if name is None:
                continue
            res_item = dict_res.get(name)
            if res_item is not None:
                res_val = res_item.get('value')
                secho(
                    '[NOTICE] file path is %s ,node %s duplicated!!! the val is %s;the before value is %s' % (
                        src_file, name, val, res_val), fg='yellow')
                if val.lower() == res_val.lower():
                    root.remove(node)
                else:
                    secho('[NOTICE] the value is not equal. the val is %s;the before value is %s' % (val, res_val))
                    root.remove(node)
            else:
                val_item = {}
                val_item['file'] = src_file
                val_item['name'] = name
                val_item['value'] = val
                dict_res[name] = val_item
        value_files[src_file] = tree
    for val_file in value_files.keys():
        value_files[val_file].write(val_file, 'UTF-8')


#  remove override icon
def remove_override_conres(res_path, decompile_dir):
    icon_name = get_iconname_in_manifest(decompile_dir)
    drawablepaths = ['drawable', 'drawable-hdpi', 'drawable-ldpi', 'drawable-mdpi', 'drawable-xhdpi', 'drawable-xxhdpi',
                     'drawable-xxxhdpi', 'drawable-hdpi-v4', 'drawable-ldpi-v4', 'drawable-mdpi-v4',
                     'drawable-xhdpi-v4', 'drawable-xxhdpi-v4', 'drawable-xxxhdpi-v4']

    tmp_dic = {'drawable-hdpi': False, "drawable-ldpi": False, "drawable-mdpi": False, "drawable-xhdpi": False,
               "drawable-xxhdpi": False, "drawable-xxxhdpi": False}
    for draw in drawablepaths:
        fin_out_path = os.path.join(os.path.join(res_path, draw), icon_name + ".png")

        if file_utils.exists(fin_out_path):
            if 'drawable-hdpi' in draw:
                if not tmp_dic['drawable-hdpi']:
                    tmp_dic['drawable-hdpi'] = True
                else:
                    file_utils.del_file_folder(fin_out_path)

            elif 'drawable-ldpi' in draw:
                if not tmp_dic["drawable-ldpi"]:
                    tmp_dic["drawable-ldpi"] = True
                else:
                    file_utils.del_file_folder(fin_out_path)
            elif 'drawable-mdpi' in draw:
                if not tmp_dic["drawable-mdpi"]:
                    tmp_dic["drawable-mdpi"] = True
                else:
                    file_utils.del_file_folder(fin_out_path)
            elif 'drawable-xhdpi' in draw:
                if not tmp_dic["drawable-xhdpi"]:
                    tmp_dic["drawable-xhdpi"] = True
                else:
                    file_utils.del_file_folder(fin_out_path)
            elif 'drawable-xxhdpi' in draw:
                if not tmp_dic["drawable-xxhdpi"]:
                    tmp_dic["drawable-xxhdpi"] = True
                else:
                    file_utils.del_file_folder(fin_out_path)
            elif 'drawable-xxxhdpi' in draw:
                if not tmp_dic["drawable-xxxhdpi"]:
                    tmp_dic["drawable-xxxhdpi"] = True
                else:
                    file_utils.del_file_folder(fin_out_path)
            else:
                # tmp_img.thumbnail((192, 192))
                print("do nothing")


def generate_new_r_file(new_package_name, decompile_dir, smali_folder):
    # 2021.1.14 aapt -> aapt2 update
    handle_duplicated_value_res(decompile_dir)
    decompile_dir = file_utils.get_full_path(decompile_dir)
    decompile_dir_parent = os.path.dirname(decompile_dir)
    temp_path = os.path.join(decompile_dir_parent, "temp")
    temp_path = file_utils.get_full_path(temp_path)
    secho('[INFO] generate R:the temp path is %s' % temp_path)
    file_utils.del_file_folder(temp_path)
    if not file_utils.exists(temp_path):
        os.makedirs(temp_path)
    res_path = file_utils.get_full_path(os.path.join(decompile_dir, 'res'))
    target_res_path = file_utils.get_full_path(os.path.join(temp_path, 'res'))
    file_utils.copy_files(res_path, target_res_path)
    gen_path = file_utils.get_full_path(os.path.join(temp_path, 'gen'))
    aapt_flat_path = file_utils.get_full_path(os.path.join(temp_path, 'resources.zip'))
    aapt_tmp_apk = file_utils.get_full_path(os.path.join(temp_path, 'temp.apk'))

    remove_override_conres(target_res_path, decompile_dir)

    if not file_utils.exists(gen_path):
        os.makedirs(gen_path)
    aapt_tool_path = file_utils.get_full_tool_path('aapt2')
    android_jar_path = file_utils.get_full_tool_path('android.jar')
    manifest_path = file_utils.get_full_path(os.path.join(decompile_dir, 'AndroidManifest.xml'))
    # step 1 aapt2 compile
    cmd = '"%s" compile --legacy --dir "%s" -o "%s"' % (
        aapt_tool_path, target_res_path, aapt_flat_path)
    ret = cli_utils.exec_cmd(cmd, True)
    # ignore the error
    # if ret:
    #     msg = "[FAIL] generate_new_r_file run command fail,cmd:%s" % cmd
    #     secho(msg, fg='red')
    #     raise Exception(msg)

    # step 2 aapt2 link
    cmd = '"%s" link -o "%s" --java "%s" -I "%s" "%s" --manifest "%s"' % (
        aapt_tool_path, aapt_tmp_apk, gen_path, android_jar_path, aapt_flat_path, manifest_path)
    ret = cli_utils.exec_cmd(cmd)
    if ret:
        msg = "[FAIL] generate_new_r_file run command fail,cmd:%s" % cmd
        secho(msg, fg='red')
        raise Exception(msg)
    r_file_path = new_package_name.replace('.', '/')
    r_file_path = os.path.join(gen_path, r_file_path)
    r_file_path = os.path.join(r_file_path, 'R.java')
    r_file_path = file_utils.get_full_path(r_file_path)
    # 编译R文件
    cmd = '"%sjavac" -source 1.7 -target 1.7 -encoding UTF-8 "%s"' % (file_utils.get_java_bin_dir(), r_file_path)
    ret = cli_utils.exec_cmd(cmd)
    if ret:
        msg = "[FAIL] generate_new_r_file run command fail,cmd:%s" % cmd
        secho(msg, fg='red')
        raise Exception(msg)
    target_dex_file = file_utils.get_full_path(os.path.join(temp_path, 'classes.dex'))
    dx_tool_path = file_utils.get_full_tool_path('dx.jar')
    cmd = file_utils.get_java_cmd() + ' -jar -Xmx1024m -Xms512m "%s" --dex --output="%s" "%s"' % (
        dx_tool_path, target_dex_file, gen_path)
    ret = cli_utils.exec_cmd(cmd)
    if ret:
        msg = "[FAIL] generate_new_r_file run command fail,cmd:%s" % cmd
        secho(msg, fg='red')
        raise Exception(msg)
    smali_path = file_utils.get_full_path(os.path.join(decompile_dir, smali_folder))
    ret = dex2smali(target_dex_file, smali_path, 'baksmali-2.5.2.jar')
    if ret:
        raise Exception('generate_new_r_file dex2smali fail')


def add_res_to_apk(decompile_dir, apk_file):
    apk_file = file_utils.get_full_path(apk_file)
    aapt_tool_path = file_utils.get_full_tool_path('aapt')
    decompile_dir = file_utils.get_full_path(decompile_dir)
    ignore_files = ['AndroidManifest.xml', 'apktool.yml', 'smali', 'smali_classes2', 'smali_classes3', 'smali_classes4',
                    'smali_classes5', 'smali_classes6', 'smali_classes7', 'smali_classes8', 'res', 'original', 'lib',
                    'build', 'assets', 'unknown', 'smali_assets']
    ignore_files_full_path = []
    for file_tmp in ignore_files:
        full_path = file_utils.get_full_path(os.path.join(decompile_dir, file_tmp))
        ignore_files_full_path.append(full_path)
    add_files = []
    add_files = file_utils.list_files(decompile_dir, add_files, ignore_files_full_path)
    if add_files:
        cmd = '"%s" add "%s"'
        for file_tmp in add_files:
            # 截取文件的相对路径
            relative_file_path = file_tmp[(len(decompile_dir) + 1):]
            cmd = cmd + ' ' + relative_file_path
        cmd = cmd % (aapt_tool_path, apk_file)
        current_path = os.getcwd()
        os.chdir(decompile_dir)
        ret = cli_utils.exec_cmd(cmd)
        os.chdir(current_path)
        if ret:
            msg = "[Fail] add_res_to_apk run cmd fail,the cmd:" % cmd
            secho(msg, fg='red')
            raise Exception(msg)


def zipalign_apk(src_apk_file, dst_apk_file, zipalign_name="zipalign"):
    # zipalign_tool_path = ""
    # file_utils.get_full_tool_path('zipalign')

    zipalign_tool_path = file_utils.get_full_tool_path(zipalign_name)
    cmd = '"%s" -f 4 "%s" "%s"' % (zipalign_tool_path, src_apk_file, dst_apk_file)
    ret = cli_utils.exec_cmd(cmd)
    if ret:
        msg = "[Fail] zipalign apk, cmd:%s" % cmd
        secho(msg, fg='red')
        raise Exception(msg)


def sign_apk(apk_file, game_config, channel_config):
    keystore_cfg = conf_utils.load_keystore_config(game_config['appName'], channel_config['id'])
    apk_file = file_utils.get_full_path(apk_file)
    keystore_file = file_utils.get_full_path(keystore_cfg['keystore'])
    aapt_tool = file_utils.get_full_tool_path('aapt')
    if not file_utils.exists(keystore_file):
        msg = "the keystore file is not exists. %s", keystore_file
        secho(msg, fg='red')
        raise Exception(msg)
    cmd = '%s list %s' % (aapt_tool, apk_file)
    output = os.popen(cmd).read()
    for filename in output.split('\n'):
        if filename.find('META_INF') == 0:
            rmcmd = '"%s" remove "%s" "%s"' % (aapt_tool, apk_file, filename)
            cli_utils.exec_cmd(rmcmd)
    signcmd = '"%sjarsigner" -digestalg SHA1 -sigalg SHA1withRSA -keystore "%s" -storepass "%s" -keypass "%s" "%s" "%s" ' % (
        file_utils.get_java_bin_dir(), keystore_file, keystore_cfg['password'], keystore_cfg['aliaspwd'], apk_file,
        keystore_cfg['aliaskey'])
    ret = cli_utils.exec_cmd(signcmd)
    if ret:
        msg = "[Fail] sign apk file:%s,keystore file:%s,keystore password:%s keystore alias:%s" % (
            apk_file, keystore_file, keystore_cfg['password'], keystore_cfg['aliaskey'])
        secho(msg, fg='red')
        raise Exception(msg)


def format_xml_pretty(xml_file_path):
    mini_dom = xml.dom.minidom.parse(xml_file_path)
    with open(xml_file_path, 'wb') as stream:
        pretty_xml_as_string = mini_dom.toprettyxml()
        stream.write(pretty_xml_as_string.encode('utf8'))


def so_encode(path, section):
    so_protected_tool = file_utils.get_full_tool_path("soEncode.jar")
    print("jar path: %s", so_protected_tool)
    print(path)
    cmd = '"%s" -jar -Xms512m -Xmx1024m "%s" "%s" %s' % \
          (file_utils.get_java_cmd(), so_protected_tool, path, section)
    ret = cli_utils.exec_cmd(cmd)
    return ret
