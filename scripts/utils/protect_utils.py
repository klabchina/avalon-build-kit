#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/8 下午2:45
# @Author  : Mason
# @Site    : 
# @File    : protect_utils.py
# @Software: PyCharm

from klab import jiagu
from utils import file_utils
from utils import cli_utils
import os
import click
from click import secho


def protect_apk(path, output_path, protect_type, sign_name):
    if protect_type == 'klab':
        output_pak = jiagu.klab_protected(path, sign_name)
        apk_name = path[path.rindex(os.sep) + 1:path.rindex(".")] + "_protected.apk"
        final_apk = os.path.join(output_path, apk_name)
        file_utils.copy_files(output_pak, final_apk)
        return final_apk
    else:
        # use 360 加固
        login_cmd = '"%s" -jar -Xms2048m -Xmx4096m "%s" -login %s %s' % \
            (file_utils.get_java_cmd(), file_utils.get_full_tool_path("jiagu_qihoo/jiagu.jar"), "13918090549", "jayryu1986")
        cli_utils.exec_cmd(login_cmd)

        config_cmd = '"%s" -jar -Xms2048m -Xmx4096m "%s" -config -x86' % \
            (file_utils.get_java_cmd(), file_utils.get_full_tool_path("jiagu_qihoo/jiagu.jar"))
        cli_utils.exec_cmd(config_cmd)

        protect_cmd = '"%s" -jar -Xms2048m -Xmx4096m "%s" -jiagu %s %s' % \
            (file_utils.get_java_cmd(), file_utils.get_full_tool_path("jiagu_qihoo/jiagu.jar"), path, output_path)

        print protect_cmd
        ret = cli_utils.exec_cmd(protect_cmd)
        if ret:
            msg = "[FAIL] Failed Protected apk use 360"
            secho(msg, fg='red')
            raise Exception(msg)

        apk_name = path[path.rindex(os.sep) + 1:path.rindex(".")] + "_030_jiagu.apk"

        return os.path.join(output_path, apk_name)


def protect_so(path, output_path, protect_type):
    output_pak = jiagu.so_protected(path)
    apk_name = path[path.rindex(os.sep) + 1:path.rindex(".")] + "_protected.apk"
    final_apk = os.path.join(output_path, apk_name)
    file_utils.copy_files(output_pak, final_apk)
    return final_apk