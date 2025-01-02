# -*- coding: utf-8 -*-

from utils import log_utils
from utils import file_utils
from utils import apk_utils
from utils import conf_utils
from utils import cli_utils
from click import secho
from channel import Channel
from packing import executor_manager
import sys

__author__ = 'Kevin Sun <sun-w@klab.com>'


def entry(is_release=False, gameid='4', channelid='qihoosdk', encrypt='', thread_num=1, verbose=0, protected='none'):
    secho('[INFO]get current python interceptor version:%s' % conf_utils.get_py_version())
    secho(u"=============游戏列表============")
    secho(u"\t appID \t\t 游戏文件夹 \t\t 游戏名称")
    games = conf_utils.get_games_conf()
    if not games:
        secho("[Fail]get games config ,games config is empty", fg='red')
        return
    if games:
        for game in games:
            secho(u"\t %s \t\t %s \t\t\t%s" % (game['appID'], game['appName'], game['appDesc']))

    print("game id is %s" % gameid)
    selected_app_id = gameid  # cli_utils.exec_prompt(u"请选择一个游戏(输入appID)")
    selected_game = None
    for game in games:
        if str(game['appID']) == selected_app_id:
            selected_game = game
    if not selected_game:
        secho("[NOTICE]selected app id %s is not exist" % selected_app_id, fg='yellow')
        return

    # if is_selectable:
    #     # 要选择渠道
    #     selected_channels = select_channels(game, is_release)
    # else:
    #     # 打包所有渠道
    #     selected_channels = conf_utils.get_channels_conf(game['appName'])
    selected_channels = select_channels(game, channelid)

    if not selected_channels:
        secho("[NOTICE]没有选择合适的channel进行打包,游戏名称:%s" % game['appName'])
        return
    # 创建channel对象
    channel_objects = []
    if selected_channels:
        for selected_channel in selected_channels:
            channel_objects.append(Channel(selected_game, selected_channel, encrypt, protected))
    executor_manager.run_all_channels(channel_objects, thread_num)


def entry_auto(is_release=False, game='*', channel='*', thread_num=1, verbose=0):
    pass


def select_channels(game, channelid, is_full_res=False):
    secho(u"=============渠道列表============")
    secho(u"\t渠道名 \t\t 渠道号 \t\t 渠道 \n")
    channels = conf_utils.get_channels_conf(game['appName'])
    if not channels:
        secho("[Fail] 没有任何可以打包的渠道")
        return
    for ch in channels:
        name = ch['name']
        if len(name) <= 6:
            ch_str = u"\t%s \t\t\t %s \t\t %s " % (ch['name'], ch['id'], ch['desc'])
        elif 6 < len(name) <= 13:
            ch_str = u"\t%s \t\t %s \t\t %s " % (ch['name'], ch['id'], ch['desc'])
        else:
            ch_str = u"\t%s \t %s \t\t %s " % (ch['name'], ch['id'], ch['desc'])
        secho(ch_str)
    selected = []
    while True:
        target = channelid  # cli_utils.exec_prompt(u"请选择需要打包的渠道(渠道名),全部输入*,多个用逗号分割")
        if target == '*':
            selected = channels
        else:
            for t in target.split(','):
                t = t.strip()
                match_channels = [c for c in channels if c['name'].lower() == t.lower()]
                if match_channels:
                    selected.append(match_channels[0])
        if selected:
            break
        else:
            secho("\n无效的渠道名，请重新输入！！\n")
    return selected
