#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/9 2:33 PM
# @Author  : Mason
# @Site    : 
# @File    : aab_utils.py
# @Software: PyCharm

from utils import file_utils
from utils import cli_utils

def aab_modify_application(file_path, app_name):
    aab_helper = file_utils.get_full_tool_path("kcaabhelper.jar")
    print("jar path: %s", aab_helper)
    cmd = '"%s" -jar -Xms512m -Xmx1024m "%s" modifyapp "%s" %s' % \
          (file_utils.get_java_cmd(), aab_helper, file_path, app_name)
    ret = cli_utils.exec_cmd(cmd)
    return ret

def aab_add_service(file_path, serviceName):
    aab_helper = file_utils.get_full_tool_path("kcaabhelper.jar")
    print("jar path: %s", aab_helper)
    cmd = '"%s" -jar -Xms512m -Xmx1024m "%s" addIsolatedService "%s" %s' % \
          (file_utils.get_java_cmd(), aab_helper, file_path, serviceName)
    ret = cli_utils.exec_cmd(cmd)
    return ret

def generator_apk(aab_path, output_path):
    cmd = 'bundletool build-apks --bundle=%s --output=%s --mode=universal' % \
          (aab_path, output_path)
    ret = cli_utils.exec_cmd(cmd)
    return ret