#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/8 下午2:45
# @Author  : Mason
# @Site    :
# @File    : jiagu.py
# @Software: PyCharm

import codecs
import os
import random
import re
import shutil
import string
import subprocess
import zipfile
from os import path
from xml.dom import minidom

from utils import apk_utils
from utils import cli_utils
from utils import conf_utils
from utils import file_utils

"""
一、针对目标app不存在自定义application的情况
    1.反编译目标app
    2.检测manifest文件是否有自定义的Application，并假设没有自定义Application
    3.如果没有自定义Application，则复制smali文件夹，跟反编译后的app下的smali合并: cp -rf smali Target/
    4.修改manifest文件，将自定义Application设定为“org.hackcode.ProxyApplication”
    5.重打包目标app
    6.提取重打包后的apk中的classes.dex文件，并压缩为TargetApk.zip文件，并将重打包的app命名为Target.modified.apk
    7.合并TuokeApk项目下的classes.dex和TargetApk.zip(加固),生成classes.dex
    8.将合并生成的新classes.dex文件与Target.modified.apk中的classes.dex替换
    9.复制TuokeApk项目下的lib目录下的所有文件和文件夹到目标app中
    10.将修改后的app重压缩成zip文件
    11.签名
"""


def un_zip(file_name):
    """unzip zip file"""
    zip_file = zipfile.ZipFile(file_name, "r", zipfile.zlib.DEFLATED, True)
    if os.path.isdir(file_name + "_files"):
        pass
    else:
        os.mkdir(file_name + "_files")
    for names in zip_file.namelist():
        zip_file.extract(names, file_name + "_files/")
    zip_file.close()
    return file_name + "_files"


def zip_dir(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))

    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED, True)
    for tar in filelist:
        arcname = tar[len(dirname):]
        zf.write(tar, arcname)
    zf.close()


def recompile_tuokeapk_project(application_name):
    """
    1.修改 String appClassName = "com.targetapk.MyApplication";
    2.重新编译
    """
    file_path = file_utils.get_full_path(
        'config/apk_protected_klab/TuokeApk/app/src/main/java/org/hackcode/ProxyApplication.java')
    new_file_path = file_utils.get_full_path(
        'config/apk_protected_klab/TuokeApk/app/src/main/java/org/hackcode/ProxyApplication2.java')
    file_in = open(file_path)
    file_out = open(new_file_path, 'w')
    while 1:
        line = file_in.readline()
        if not line:
            break
        pattern = re.compile(r'.*String.*appClassName.*=.*\".*\";.*')
        if re.search(pattern, line):
            print('[+] Find \"String appClassName = ...\", replace it with \"' + application_name + '\"')
            file_out.write('\t\t\tString appClassName = \"' + application_name + '\";\n')
        else:
            file_out.write(line)

    file_in.close()
    file_out.close()

    os.remove(file_path)
    os.rename(new_file_path, file_path)

    # 重新编译TuokeApk工程
    os.chdir(file_utils.get_full_path('config/apk_protected_klab/TuokeApk/'))

    subprocess.Popen("gradle clean", shell=True, stdout=subprocess.PIPE).stdout.read()
    out = subprocess.Popen("gradle build", shell=True, stdout=subprocess.PIPE).stdout.read()
    print(out)
    if out.find(('BUILD SUCCESSFUL').encode('utf-8')) < 0:
        print('Build error!')
        raise Exception("Gradle Build Failed")
        return False
    print('[+] Rebuild TuokeApk project successfully!')
    os.chdir('../../../scripts')

    return True


def remove_without_exception(item, type):
    if type == 'd':
        try:
            shutil.rmtree(item)
        except Exception as e:
            pass
    else:
        try:
            os.remove(item)
        except Exception as e:
            pass


def clean(base_dir):
    try:
        print('start clean')
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)

        os.mkdir(base_dir)
    except Exception as e:
        print(e.message)
        pass

    os.chdir(tuapk_project_path)
    subprocess.Popen("gradle clean", shell=True, stdout=subprocess.PIPE).stdout.read()
    os.chdir('../../../scripts')


def gen_random_str(length):
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for i in range(length)])  # 得出的结果中字符会有重复的


def modify_and_protect_so(apk_dir):
    """
    使用UPX加固so
    要求so必须有.init 段

    """
    for root, dirs, files in os.walk(os.path.join(apk_dir, "lib")):
        for name in files:
            filepath = root + os.path.sep + name
            filename, ext = os.path.splitext(filepath)
            if check_need_protected(filename, ext):
                ret = apk_utils.protect_so(filename)
                if not ret:
                    os.remove(filepath)
                    shutil.move(filename + "-npx.so", filepath)


def check_need_protected(filename, ext):
    if (ext == '.so'):
        for so_name in so_list["solit"]:
            if so_name in filename:
                return True

        return False
    else:
        return False

def dex_protected(dir_name, dex_count, unknow_path):
    os.chdir(dir_name)
    # 写入classes.dex
    f = zipfile.ZipFile('TargetApk.zip', 'w', zipfile.ZIP_DEFLATED)
    if path.exists(unknow_path):
        os.chdir(unknow_path)
        for root, dir_list, file_list in os.walk(unknow_path):
            for file_name in file_list:
                f_path = os.path.join(root, file_name)
                f.write(f_path.replace(unknow_path, "")[1:])

    os.chdir(dir_name)
    f.write('classes.dex')
    for i in range(2, dex_count + 1):
        f.write('classes' + str(i) + '.dex')
        os.remove('classes' + str(i) + '.dex')
    f.close()
    os.remove('classes.dex')

    shutil.copyfile(file_utils.get_full_path(
        'config/apk_protected_klab/TuokeApk/app/build/intermediates/dex/release/mergeDexRelease/classes.dex'), 'tuoke.dex')

    jiagu_resut = cli_utils.exec_cmd(
        'java -jar ' + file_utils.get_full_tool_path('klab_protected.jar') + ' tuoke.dex TargetApk.zip')

    if jiagu_resut:
        msg = 'protected failed by klab_protected.jar'
        print(msg)
        raise Exception(msg)


def smali_merge(project_dir):
    for i in range(2, 10):
        apk_smali_path = os.path.join(project_dir, "smali_classes" + str(i))
        if path.exists(apk_smali_path):
            file_utils.copy_files(apk_smali_path, os.path.join(project_dir, "smali"))
            shutil.rmtree(apk_smali_path)


def find_dex_num(project_dir):
    ret = 0
    for root, dirs, files in os.walk(project_dir):
        for dir in dirs:
            if "smali" in dir and "assets" not in dir:
                ret = ret + 1

    return ret


def lib_protected(extracted_dir):
    ret = apk_utils.decompile_apk(file_utils.get_full_path(
        "config/apk_protected_klab/TuokeApk/app/build/outputs/apk/release/app-release-unsigned.apk"),
                                  file_utils.get_full_path(
                                      "config/apk_protected_klab/TuokeApk/app/build/outputs/apk/release/nice-way"))

    if ret:
        print('[Error] apktool decompiled error!')
        return
    print('[+] Apktool decompiled Target-apk-release.apk successfully!')

    print('[+] Copying config/apk_protected_klab/TuokeApk/app/build/outputs/apk/release/nice-way/lib/...')
    rela_apk_output = "config/apk_protected_klab/TuokeApk/app/build/outputs/apk/release/nice-way/lib/"
    if not os.path.exists(extracted_dir + '/lib/'):
        os.mkdir(extracted_dir + '/lib/')
        for item in os.listdir(file_utils.get_full_path(
                rela_apk_output)):

            # so libklabniceway 加密
            apk_utils.so_encode(file_utils.get_full_path(
                rela_apk_output + item + '/libklabniceway.so'), ".kcniceway")

            if not os.path.exists(extracted_dir + '/lib/' + item):
                shutil.copytree(file_utils.get_full_path(
                    rela_apk_output + item),
                    extracted_dir + '/lib/' + item)
            else:
                shutil.copyfile(
                    file_utils.get_full_path(
                        rela_apk_output + item + '/libklabniceway.so'),
                    extracted_dir + '/lib/' + item + '/libklabniceway.so')
    else:
        for item in os.listdir(extracted_dir + '/lib/'):
            # so libklabniceway 加密
            apk_utils.so_encode(file_utils.get_full_path(
                rela_apk_output + item + '/libklabniceway.so'), ".kcniceway")

            shutil.copyfile(file_utils.get_full_path(
                rela_apk_output + item + '/libklabniceway.so'),
                extracted_dir + '/lib/' + item + '/libklabniceway.so')
            shutil.copyfile(file_utils.get_full_path(
                rela_apk_output + item + '/libassistant1.so'),
                extracted_dir + '/lib/' + item + '/libassistant1.so')
            shutil.copyfile(file_utils.get_full_path(
                rela_apk_output + item + '/libassistant2.so'),
                extracted_dir + '/lib/' + item + '/libassistant2.so')

    # 破坏SO文件的ELF头部（删除 ELF header）
    # modify_and_protect_so(extracted_dir)

def klab_protected(filepath, sign_name):
    global tuapk_project_path, so_list

    so_list = conf_utils.get_protected_so(sign_name)
    tuapk_project_path = file_utils.get_full_path("config/apk_protected_klab/TuokeApk")
    print(tuapk_project_path)
    dir_name = os.path.join(os.path.dirname(filepath), 'protected')

    clean(dir_name)
    input_filename = filepath

    file_utils.copy_files(input_filename, path.join(dir_name, 'Target.apk'))

    # Step1: 反编译目标app

    ret = apk_utils.decompile_apk(os.path.join(dir_name, 'Target.apk'), path.join(dir_name, 'Target'))

    if ret:
        print('[Error] apktool decompiled error!')
        return
    print('[+] Apktool decompiled Target.apk successfully!')

    dex_num = find_dex_num(path.join(dir_name, 'Target'))

    # Step2: 检测manifest文件是否有自定义的Application
    doc = minidom.parse(path.join(dir_name, 'Target/AndroidManifest.xml'))
    root = doc.documentElement
    application_node = root.getElementsByTagName('application')[0]
    applicationName = application_node.getAttribute('android:name')

    packageName = root.getAttribute('package')
    if applicationName:
        if not applicationName.startswith(packageName) and applicationName.startswith('.'):
            applicationName = packageName + applicationName
        print('[+] Target app\'s Application: ', applicationName)
        # Step3: 修改JiguApk工程中ProxyApplication中的applicationName变量为目标app的Application名称
        recompile_tuokeapk_project(applicationName)
    else:
        print('[+] Target.apk has no self-defined Application!')
        applicationName = 'com.targetapk.MyApplication'
        recompile_tuokeapk_project(applicationName)
        # Step3: 复制smali文件夹，跟反编译后的app下的smali合并
        print('[+] Copy smali folder into Target folder...')
        smali_path = file_utils.get_full_path("config/apk_protected_klab/smali")
        out = subprocess.Popen('cp -rf ' + smali_path + ' ' + path.join(dir_name, 'Target/'), shell=True,
                               stdout=subprocess.PIPE).stdout.read()

    # Step4: 修改manifest文件，将自定义Application设定为“org.hackcode.ProxyApplication”
    print('[+] Modified AndroidManifest.xml...')
    application_node.setAttribute('android:name', 'org.hackcode.ProxyApplication')

    # Step4-1: 修改mainfest文件，添加magisk对应的 services
    magisk_service = doc.createElement("service")
    magisk_service.setAttribute("android:name", "org.hackcode.service.IsolatedService")
    magisk_service.setAttribute("android:enabled", "true")
    magisk_service.setAttribute("android:isolatedProcess", "true")
    application_node.appendChild(magisk_service)

    file_handle = codecs.open(path.join(dir_name, 'Target/AndroidManifest.xml'), 'w', 'utf-8')
    root.writexml(file_handle)
    file_handle.close()

    # Step5: 重打包目标app
    out = apk_utils.recompile_apk(path.join(dir_name, 'Target'), path.join(dir_name, 'Target/dist/Target.apk'))

    if out:
        print('[Error] apktool recompiled error!')
        return
    print('[+] Apktool recompiled Target successfully!')

    # Step6: 将重打包的app命名为Target.modified.apk,并提取重打包后的apk中的classes.dex文件，并压缩为TargetApk.zip文件
    print('[+] Rename target app: \"Target.modified.apk\"')
    shutil.copyfile(path.join(dir_name, 'Target/dist/Target.apk'), path.join(dir_name, 'Target.modified.apk'))

    ret = apk_utils.decompile_apk_nodex(os.path.join(dir_name, 'Target.modified.apk'), path.join(dir_name, 'Target.modified.apk_files'))

    if ret:
        print('[Error] apktool decompiled error!')
        return
    print('[+] Apktool decompiled Target.modified.apk successfully!')
    extracted_dir = path.join(dir_name, 'Target.modified.apk_files')

    print('[+] Extracted classes.dex from Target.modifed.apk into TargetApk.zip')
    shutil.copyfile(extracted_dir + '/classes.dex', path.join(dir_name, 'classes.dex'))
    for i in range(2, dex_num + 1):
        shutil.copyfile(extracted_dir + '/classes' + str(i) + '.dex', path.join(dir_name, 'classes' + str(i) + '.dex'))
        os.remove(extracted_dir + '/classes' + str(i) + '.dex')


    # Step7: 合并TuokeApk/bin/classes.dex和TargetApk.zip(加固),生成classes.dex
    dex_protected(dir_name, dex_num, path.join(dir_name, "Target/unknown"))

    # Step8: 将合并生成的新classes.dex文件与Target.modified.apk中的classes.dex替换
    print('[+] Replace \"%s\" with \"classes.dex\"' % (extracted_dir + '/classes.dex',))
    shutil.copyfile('classes.dex', extracted_dir + '/classes.dex')

    # Step9: 复制TuokeApk/libs目录下的所有文件和文件夹到目标app中
    lib_protected(extracted_dir)



    # Step10: 将修改后的app重压缩成zip文件
    print('[+] Compress %s folder into Target.modified.2.apk' % extracted_dir)
    # zip_dir(extracted_dir, 'Target.modified.2.apk')
    out = apk_utils.recompile_apk(extracted_dir, path.join(dir_name, 'Target.modified.2.apk'))

    if out:
        print('[Error] apktool recompiled error!')
        return
    print('[+] Apktool recompiled Target successfully!')

    print('[+] Protected End...')

    return path.join(dir_name, 'Target.modified.2.apk')


def so_protected(filepath):

    dir_name = os.path.join(os.path.dirname(filepath), 'protected')

    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

    os.mkdir(dir_name)
    input_filename = filepath

    file_utils.copy_files(input_filename, path.join(dir_name, 'Target.apk'))

    # Step1: 反编译目标app

    extracted_dir = un_zip(path.join(dir_name, 'Target.apk'))

    # Step9: 复制TuokeApk/libs目录下的所有文件和文件夹到目标app中
    apk_utils.so_encode(file_utils.get_full_path(
        extracted_dir + '/lib/arm64-v8a/libsimple.so'), ".kcniceway")
    apk_utils.so_encode(file_utils.get_full_path(
        extracted_dir + '/lib/x86/libsimple.so'), ".kcniceway")

    os.chdir(path.dirname(extracted_dir));
    # Step10: 将修改后的app重压缩成zip文件
    print('[+] Compress %s folder into Target.modified.2.apk' % extracted_dir)
    zip_dir(extracted_dir, 'Target.modified.2.apk')

    print('[+] Protected End...')

    return path.join(dir_name, 'Target.modified.2.apk')