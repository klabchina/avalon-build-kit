# -*- coding: utf-8 -*-
import os
import shutil
import click
import re
import platform
from utils import log_utils

__author__ = 'Kevin Sun <sun-w@klab.com>'

cur_dir = os.getcwd()
base_dir = None


def init(tools_dir):
    global base_dir
    base_dir = tools_dir


def list_files(src, res_files, ignore_files):
    if os.path.exists(src):
        if os.path.isfile(src):
            if src not in ignore_files:
                res_files.append(src)
        elif os.path.isdir(src):
            if src not in ignore_files:
                for f in os.listdir(src):
                    list_files(os.path.join(src, f), res_files, ignore_files)
    return res_files


def del_file_folder(src):
    if os.path.exists(src):
        if os.path.isfile(src):
            try:
                src = src.replace('\\', '/')
                os.remove(src)
            except Exception as e:
                click.secho("[Fail] file_utils.del_file_folder when remove a file error info:" + str(e), fg='red')
        elif os.path.isdir(src):
            try:
                shutil.rmtree(src)
            except Exception as e:
                click.secho("[Fail] file_utils.del_file_folder when remove dir error info:" + str(e), fg='red')

def move_file(src, dst):
    parent_path = os.path.dirname(dst)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)

    shutil.move(src, dst)

def copy_files(src, dst):
    if not os.path.exists(src):
        click.secho('[Fail] file_utils.copy_files src is not exists path:%s' % src, fg='red')
        return
    if os.path.isfile(src):
        _copy_file(src, dst)
        return
    elif os.path.isdir(src):
        for f in os.listdir(src):
            source_file = os.path.join(src, f)
            target_file = os.path.join(dst, f)
            if os.path.isfile(source_file):
                _copy_file(source_file, target_file)
            else:
                copy_files(source_file, target_file)


def get_splash_path():
    return get_full_path("config/splash")


def _copy_file(src, dst):
    src = get_full_path(src)
    dst = get_full_path(dst)
    if not exists(src):
        return
    if not exists(dst) or os.path.getsize(dst) != os.path.getsize(src) \
            or os.path.getmtime(dst) != os.path.getmtime(src):
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        with open(src, 'rb') as src_stream:
            with open(dst, 'wb') as dst_stream:
                dst_stream.write(src_stream.read())


def modify_file_content(sourcefile, oldContent, newContent):
    if os.path.isdir(sourcefile):
        log_utils.warning("the source %s must be a file not a dir", sourcefile)
        return

    if not os.path.exists(sourcefile):
        log_utils.warning("the source is not exists.path:%s", sourcefile)
        return

    f = open(sourcefile, 'r+')
    data = str(f.read())
    f.close()
    bRet = False
    idx = data.find(oldContent)
    while idx != -1:
        data = data[:idx] + newContent + data[idx + len(oldContent):]
        idx = data.find(oldContent, idx + len(oldContent))
        bRet = True

    if bRet:
        fw = open(sourcefile, 'w')
        fw.write(data)
        fw.close()
        log_utils.info("modify file success.path:%s", sourcefile)
    else:
        log_utils.warning("there is no content matched in file:%s with content:%s", sourcefile, oldContent)


def get_full_path(filename):
    if os.path.isabs(filename):
        return filename
    filename = os.path.join(base_dir, filename)
    filename = filename.replace('\\', '/')
    filename = re.sub('/+', '/', filename)
    return filename


def get_splash_path():
    return get_full_path("config/splash")


def get_java_bin_dir():
    if platform.system() == 'Windows':
        return get_full_path("tools/win/jre/bin/")
    else:
        return ""


def get_java_cmd():
    return get_java_bin_dir() + "java"


def get_tool_path(tool_name):
    if platform.system() == 'Windows':
        return "tools/win/" + tool_name
    else:
        return "tools/linux/" + tool_name


def get_full_tool_path(tool_name):
    return get_full_path(get_tool_path(tool_name))


def get_full_output_path(app_name, channel):
    path = get_full_path('output/' + app_name + '/' + channel)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def exists(path):
    return os.path.exists(path)
