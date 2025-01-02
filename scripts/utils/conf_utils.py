# -*- coding: utf-8 -*-
import sys
from utils import file_utils
import yaml
from click import secho

__author__ = 'Kevin Sun <sun-w@klab.com>'


def get_py_version():
    version = sys.version_info
    major = version.major
    minor = version.minor
    micro = version.micro
    curr_version = str(major) + "." + str(minor) + "." + str(micro)
    return curr_version


def is_py_env_2():
    version = sys.version_info
    major = version.major
    return major == 2


def get_games_conf():
    config_file_path = file_utils.get_full_path("games/games.yml")
    try:
        with open(config_file_path, 'r') as stream:
            games = yaml.load(stream)
            return games
    except Exception as e:
        secho("[Fail]can't parse games.xml error info:%s path:%s" % (str(e), config_file_path), fg='red')
        raise e


def get_protected_keystore(game_name='Penguin', env=True):
    env_str = ""
    if env:
        env_str = "_dev"


    config_file_path = file_utils.get_full_path("games/%s/keystore%s.yml" % (game_name, env_str))

    print("config file path is %s" % config_file_path)
    try:
        with open(config_file_path, 'r') as stream:
            keystore = yaml.load(stream)
            return keystore
    except Exception as e:
        secho("[Fail]can't parse keystore.xml error info:%s path:%s" % (str(e), config_file_path), fg='red')
        raise e

def get_protected_so(game_name='Lapis'):
    config_file_path = file_utils.get_full_path("games/%s/protected.yml" % (game_name))

    print("config file path is %s" % config_file_path)
    try:
        with open(config_file_path, 'r') as stream:
            keystore = yaml.load(stream)
            return keystore
    except Exception as e:
        secho("[Fail]can't parse keystore.xml error info:%s path:%s" % (str(e), config_file_path), fg='red')
        raise e


def get_channels_conf(game_name="Lovelive"):
    config_file_path = file_utils.get_full_path("games/" + game_name + "/game_channels_config.yml")
    try:
        with open(config_file_path, 'r') as stream:
            game_channels_config = yaml.load(stream)
            # 加载插件配置
            global_plugins = []
            if "global-plugins" in game_channels_config:
                for global_plugin in game_channels_config['global-plugins']:
                    plugin = load_plugin_config(game_name, global_plugin['name'])
                    global_plugins.append(plugin)
            new_configs = []
            for one_game_channel in game_channels_config['channels']:
                # 处理特殊参数
                if "sdk-params" in one_game_channel:
                    sdk_params = {}
                    for param in one_game_channel["sdk-params"]:
                        sdk_params[param['name']] = param['value']
                    one_game_channel['sdkParams'] = sdk_params
                    one_game_channel['third-plugins'] = global_plugins
                # 加载每个渠道自有的配置
                channel_config = load_channel_config(one_game_channel["sdk"], one_game_channel)
                # 合并两个channel配置
                one_game_channel = dict(one_game_channel, **channel_config)
                new_configs.append(one_game_channel)
            return new_configs
    except Exception as e:
        secho("[Fail]config_utils.get_channels_conf error info:%s path:%s" % (str(e), config_file_path), fg='red')
        raise e


def load_channel_config(channel_name, game_channel_conf):
    config_path = file_utils.get_full_path('config/sdk/%s/config.yml' % channel_name)
    try:
        with open(config_path, 'r') as stream:
            one_channel = yaml.load(stream)
            if "params" in one_channel:
                for param in one_channel["params"]:
                    if "required" in param and "1" == param["required"]:
                        key = param["name"]
                        if key in game_channel_conf["sdkParams"] and game_channel_conf["sdkParams"][key] is not None:
                            param['value'] = game_channel_conf["sdkParams"][key]
                        else:
                            msg = "the sdk %s 'sdkParam's is not all configed in the config.xml.path:%s" % (
                                channel_name, config_path)
                            secho(msg, fg='red')
                            raise UserWarning(msg)
            return one_channel
    except Exception as e:
        secho("[Fail] load channel config error info:%s path:%s" % (str(e), config_path))
        raise e


def load_plugin_config(game_name, plugin_name):
    plugin_config_path = file_utils.get_full_path("games/%s/plugin/%s/config.yml" % (game_name, plugin_name))
    try:
        with open(plugin_config_path, 'r') as stream:
            plugin_config = yaml.load(stream)
            return plugin_config
    except Exception as e:
        secho("[Fail]config_utils.load_plugin_config error info:%s path:%s" % (str(e), plugin_config_path), fg='red')
        raise e


def load_avalon_config():
    avalon_config_path = file_utils.get_full_path("config/avalon/avalon_conf.yml")
    with open(avalon_config_path, 'r') as stream:
        avalon_config = yaml.load(stream)
        if "use_avalon_auth" not in avalon_config or "avalon_auth_url" not in avalon_config \
                or "avalon_server_url" not in avalon_config:
            msg = "the use_avalon_auth or avalon_auth_url is not exists in config/avalon/avalon_conf.yml,please check!!"
            secho(msg, fg='red')
            raise UserWarning(msg)
        return avalon_config


def load_keystore_config(game_name, channel_id):
    keystore_config_path = file_utils.get_full_path("games/%s/keystore.yml" % game_name)
    with open(keystore_config_path, 'r') as stream:
        keystore_config = yaml.load(stream)
        if "channel_keystores" in keystore_config and keystore_config['channel_keystores'] is not None:
            for keystore in keystore_config['channel_keystores']:
                if keystore['channelId'] == channel_id:
                    return keystore
        return keystore_config['default']
