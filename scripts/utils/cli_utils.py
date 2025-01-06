# -*- coding: utf-8 -*-
import sys
import importlib
import re
import click
import platform
import subprocess
from utils import log_utils
import os

__author__ = 'Kevin Sun <sun-w@klab.com>'


def exec_cmd(cmd, ignore = False):
    cmd = cmd.replace('\\', '/')
    cmd = re.sub('/+', '/', cmd)
    ret = 0
    try:
        importlib.reload(sys)
        if platform.system() == 'Windows':
            st = subprocess.STARTUPINFO
            st.dwFlags = subprocess.STARTF_USESHOWWINDOW
            st.wShowWindow = subprocess.SW_HIDE
        cmd_subprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        std_output, err_output = cmd_subprocess.communicate()
        # 获取执行结果
        ret = cmd_subprocess.returncode
        if ret:
            # 返回值不为0,执行失败
            if not ignore:
                click.secho('[Fail] exec cmd:%s fail!!!' % cmd, fg='red')

            log_utils.error(std_output)
            log_utils.error(err_output)
        else:
            click.secho('[OK] exec cmd:%s successfully' % cmd, fg='green')
            log_utils.info(std_output)
            log_utils.info(err_output)
    except Exception as e:
        click.secho(str(e), fg='red')
        raise e
    return ret


def exec_win_cmd(cmd):
    os.system(cmd)


def exec_prompt(tip):
    txt = click.prompt(tip, type=str)
    return txt
