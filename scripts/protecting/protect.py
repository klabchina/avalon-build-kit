# -*- coding: utf-8 -*-
from utils import file_utils
from click import secho
from utils import apk_utils
from utils import cli_utils
from utils import conf_utils
from utils import protect_utils
from klab import jiagu
from klab import aab_protected
import shutil
import os

__author__ = 'mason'


def re_build_apk(folder, sign_name):
    global work_dir, apk_name, keystore_config

    keystore_config = conf_utils.get_protected_keystore(sign_name, False)

    output_path = folder + ".apk"

    jiagu.zip_dir(folder, output_path)

    sign_apk(output_path)

# apk 加壳
def protect_apk(path, method, sign_name, env):
    global work_dir, apk_name, keystore_config

    keystore_config = conf_utils.get_protected_keystore(sign_name, env)

    work_dir = os.path.dirname(path)
    apk_name = path[path.rindex(os.sep) + 1:path.rindex(".")]

    output_path = protect_utils.protect_apk(path, work_dir, method, sign_name)

    new_apk_file = work_dir + os.sep + os.path.basename(output_path).split(".")[0] + "-zipped.apk"
    secho("[Final] File name is %s" % new_apk_file)
    apk_utils.zipalign_apk(output_path, new_apk_file)
    os.remove(output_path)
    shutil.move(new_apk_file, output_path)
    sign_apk(output_path)

    return output_path


# apk 加壳
def protect_so_only(path, method, sign_name, env):
    global work_dir, apk_name, keystore_config

    keystore_config = conf_utils.get_protected_keystore(sign_name, env)

    work_dir = os.path.dirname(path)
    apk_name = path[path.rindex(os.sep) + 1:path.rindex(".")]

    output_path = protect_utils.protect_so(path, work_dir, method)

    sign_apk(output_path)

    return output_path

# aab 加固
def protect_aab(path, sign_name, keystorepass, keyalias, keyaliaspassword, env):
    global keystore_config
    keystore_config = conf_utils.get_protected_keystore(sign_name, env)
    
    if keystorepass != "":
        keystore_config["default"]["password"] = keystorepass
    if keyalias != "":
        keystore_config["default"]["aliaskey"] = keyalias
    if keyaliaspassword != "":
        keystore_config["default"]["aliaspwd"] = keyaliaspassword

    output_path = aab_protected.klab_aab_protected(path, keystore_config)

    sign_aab(output_path, " --min-sdk-version 21")


# mono 加密 独立
def protect_apk_mono(path, mono_ver, game, env):
    global work_dir, apk_name, keystore_config

    keystore_config = conf_utils.get_protected_keystore(game, env)

    work_dir = os.path.dirname(path)
    apk_name = path[path.rindex(os.sep) + 1:path.rindex(".")]

    result = protected_apk_mono(path, mono_ver)

    sign_apk(result)

    zipalign_apk(result)


def protected_apk_mono(srcpath, mono_ver):
    work_path = os.path.join(work_dir, apk_name + "-mono_encrypt")
    file_utils.del_file_folder(work_path)
    workapkpath = os.path.join(work_path, apk_name + ".apk")
    file_utils.copy_files(srcpath, workapkpath)
    apk_utils.mono_encrypt(workapkpath, mono_ver)

    apk_utils.recompile_apk(os.path.join(work_path, "decompile"),
                            os.path.join(work_path, apk_name + "_mono_encrypt.apk"))
    file_utils.del_file_folder(workapkpath)
    file_utils.del_file_folder(os.path.join(work_path, "decompile"))

    return os.path.join(work_path, apk_name + "_mono_encrypt.apk")



def zipalign_apk(apkpath):
    secho("[Start] Zip Align",
          fg='green')
    new_apk_file = work_dir + os.sep + os.path.basename(apkpath).split(".")[0] + "-zipped.apk"
    secho("[Final] File name is %s" % new_apk_file)
    apk_utils.zipalign_apk(apkpath, new_apk_file)


# 重新签名
def sign_apk(apkpath):
    signcmd = '"%s" sign --ks "%s" --ks-pass pass:%s "%s" ' % (
        file_utils.get_full_tool_path('apksigner'), file_utils.get_full_path(keystore_config["default"]["keystore"]),
        keystore_config["default"]['password'], apkpath)


    ret = cli_utils.exec_cmd(signcmd)
    if ret:
        msg = "[Fail] sign apk file:%s" % (
            apkpath)
        secho(msg, fg='red')
        raise UserWarning(msg)

def sign_aab(apkpath, other_parms):
    signcmd = '"%s" sign%s --ks "%s" --ks-pass pass:%s --ks-key-alias %s --key-pass pass:%s "%s" ' % (
        file_utils.get_full_tool_path('apksigner'), other_parms,
        file_utils.get_full_path(keystore_config["default"]["keystore"]),
        keystore_config["default"]['password'], keystore_config["default"]['aliaskey'], keystore_config["default"]['aliaspwd'],  apkpath)
    ret = cli_utils.exec_cmd(signcmd)
    if ret:
        msg = "[Fail] sign apk file:%s" % (
            apkpath)
        secho(msg, fg='red')
        raise UserWarning(msg)
