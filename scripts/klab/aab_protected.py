#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/9 12:24 PM
# @Author  : Mason
# @Site    :
# @File    : aab_protected.py
# @Software: PyCharm

import os
import subprocess
from os import path
import io

from utils import apk_utils
from utils import file_utils
from utils import aab_utils
from utils import cli_utils
import shutil
from klab import jiagu
import zipfile

"""
一、Android App Bundle 加固说明
    1.解压目标aab
    2.使用pb解析程序 修改aab 目录中manifest 文件 替换application为壳的启动appilcation
    2.bundletool build-apks --mode=universal 生成全包 apks
    3.解压apks 提取全包apk apktool反编译
    4.合并smali目录 copy加固aplication smali (如果需要) 使用smali 重构dex
    5.编译壳项目 并提取壳项目的 lib 和 dex
    6.通过dex加壳程序 把前面编译壳项目的dex 和 合并后的 dex 合并 成新的dex-final
    7.拷贝壳项目jni 解壳so到aab里 lib目录中 
        删除aab中原有的dex
        最终生成的dex放到aab dex目录中 
    8.使用zip重新打包aab
"""


def klab_aab_protected(filepath, config):
    root_path = os.path.dirname(filepath)
    work_dir = os.path.join( os.path.dirname(filepath), "protected");
    apk_work_dir = path.join(work_dir, "universal_apk_files")
    source_aab = path.join(work_dir, "Target.aab")
    apks_path = path.join(work_dir, "Target.apks")

    # step 1 + 2
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)

    os.mkdir(work_dir)

    file_utils.copy_files(filepath, source_aab)
    jiagu.un_zip(source_aab)

    ret = aab_utils.aab_modify_application(path.join(source_aab + "_files", "base/manifest/AndroidManifest.xml"), "org.hackcode.ProxyApplication")
    if ret:
        print('[Error] aab modify error !')
        return


    # 孤岛进程加入
    ret = aab_utils.aab_add_service(path.join(source_aab + "_files", "base/manifest/AndroidManifest.xml"), "org.hackcode.service.IsolatedService")
    if ret:
        print('[Error] aab service modify error !')
        return


    # 是否  没定义application
    applicationName = None
    is_defined_app = os.path.exists(path.join(source_aab + "_files", "base/manifest/origin_app"))
    if is_defined_app:
        with io.open(path.join(source_aab + "_files", "base/manifest/origin_app"), 'r', encoding='utf-8') as f:
            applicationName = f.read()

        os.remove(path.join(source_aab + "_files", "base/manifest/origin_app"))


    aab_utils.generator_apk(source_aab, apks_path)

    jiagu.un_zip(apks_path)

    # 3. 反编译apk
    full_apk_path = os.path.join(apks_path + "_files" , "universal.apk")
    apk_utils.decompile_apk(full_apk_path, apk_work_dir)


    if not applicationName:
        applicationName = 'com.targetapk.MyApplication'
        smali_path = file_utils.get_full_path("config/apk_protected_klab/smali")
        subprocess.Popen('cp -rf ' + smali_path + ' ' + apk_work_dir, shell=True,
                               stdout=subprocess.PIPE).stdout.read()

    # 4. 合并smali 并提取 dex
    # jiagu.smali_merge(apk_work_dir)

    dex_num = jiagu.find_dex_num(apk_work_dir)
    for root, dirs, files in os.walk(apk_work_dir):
        for dir in dirs:
            if dir == "smali":
                apk_utils.smali2dex(os.path.join(apk_work_dir, "smali"), os.path.join(apk_work_dir, "classes.dex"))
            elif "smali" in dir:
                apk_utils.smali2dex(os.path.join(apk_work_dir, dir), os.path.join(apk_work_dir, dir[6:] + ".dex"))

    # 5. 编译壳项目 做dex 加固
    jiagu.recompile_tuokeapk_project(applicationName)

    # 6. 通过dex加壳程序 把前面编译壳项目的dex 和 合并后的 dex 合并 成新的dex-final
    jiagu.dex_protected(apk_work_dir, dex_num, path.join(apk_work_dir, "unknown"))

    # dex回写 aab
    shutil.rmtree(path.join(source_aab + "_files", "base/dex"))
    os.mkdir(path.join(source_aab + "_files", "base/dex"))
    shutil.copyfile('classes.dex', path.join(source_aab + "_files", "base/dex/classes.dex"))

    # 7 lib 处理 并回写 aab
    aab_lib_path = path.join(source_aab + "_files", "base")
    jiagu.lib_protected(aab_lib_path)

    # 8 重新zip aab 流程结束
    jiagu.zip_dir(source_aab + "_files", path.join(root_path, "aab_protected.aab"))

    #9 签名
    # sign_aab(path.join(root_path, "aab_protected.aab"), config)

    return path.join(root_path, "aab_protected.aab")

def sign_aab(apkpath, keystore_config):
    signcmd = '"%sjarsigner" -digestalg SHA-256 -sigalg SHA256withRSA -keystore "%s" -storepass "%s" -keypass "%s" "%s" "%s" ' % (
        file_utils.get_java_bin_dir(), file_utils.get_full_path(keystore_config["default"]["keystore"]),
        keystore_config["default"]['password'], keystore_config["default"]['aliaspwd'], apkpath,
        keystore_config["default"]['aliaskey'])

    ret = cli_utils.exec_cmd(signcmd)
    if ret:
        msg = "[Fail] sign apk file:%s" % (
            apkpath)
        secho(msg, fg='red')
        raise UserWarning(msg)

