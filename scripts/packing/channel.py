# -*- coding: utf-8 -*-
import os
import os.path
import re
import shutil
import time

from click import secho

from utils import apk_utils
from utils import file_utils
from utils import img_utils
from utils import protect_utils
from utils import unity_utils

__author__ = 'Kevin Sun <sun-w@klab.com>'


class Channel:
    def __init__(self, game_config, channel_config, encrypt, protected):
        self.mono_encrypt_ver = encrypt
        self.protected = protected
        self.game_config = game_config
        self.channel_config = channel_config
        self.game_apk_path = file_utils.get_full_path("games/%s/base_game.apk" % game_config['appName']).replace('\\',
                                                                                                                 '/')
        self.is_release = True
        app_name = self.game_config['appName']
        channel_name = self.channel_config["name"]
        sdk_name = self.channel_config["sdk"]
        self.app_name = app_name
        self.channel_name = channel_name
        self.sdk_name = sdk_name
        self.work_dir = file_utils.get_full_path('workspace/' + app_name + "/" + channel_name)
        self.sdk_work_dir = self.work_dir + "/sdk/%s" % self.sdk_name
        self.decompile_dir = self.work_dir + "/decompile"
        self.decompile_smali_dir = self.decompile_dir + "/smali"
        self.out_apk_path = self.work_dir + "/output.apk"

    def pack(self):
        if not file_utils.exists(self.game_apk_path):
            secho("[Fail] the base apk file is not exists, apk path:" + self.game_apk_path, fg='red')
            return 1
        secho("now packing app name:%s channel name:%s" % (self.app_name, self.channel_name))
        file_utils.del_file_folder(self.work_dir)
        # 1. decompile apk 拷贝sdk到workspace目录,将sdk的jar反编译成smali文件
        sdk_smali_folder = self._prepared_base_smali()

        # 1.1 确定加密mono 和 dll
        if self.mono_encrypt_ver != '':
            unity_utils.encrypt_unity(self.mono_encrypt_ver, self.decompile_dir)

        # 2. 重命名AndroidManifest.xml文件的package name
        new_package_name = apk_utils.rename_package_name(self.channel_config, self.decompile_dir, self.is_release)
        # 3. 处理第三方插件
        self._handle_third_plugins(new_package_name, sdk_smali_folder)
        # 4. 执行sdk 的operations
        if 'operations' in self.channel_config:
            self._do_config_operations(self.channel_config['operations'], new_package_name, self.sdk_work_dir,
                                       self.decompile_dir, self.sdk_name, sdk_smali_folder, False)

        # 4.1 替换第三方xml中的包名
        apk_utils.rename_third_package_name(self.decompile_dir, new_package_name)

        # 4.2 使用最新的avalon sdk代码
        self._handle_newest_avalon_sdk()
        # 5. 处理channel特殊的资源
        self._copy_channel_resources()

        # 6. copy game root resources and res resources
        self._copy_game_resources()
        # 7. copy game root resources and res resources
        self._copy_game_root_resources()
        # 8. 自动给游戏添加角标
        self._append_channel_icon_mark()
        # 9. 生成developer_config.properties信息
        self._write_dev_info()
        # 10. 生成插件的配置文件
        self._write_plugin_info()
        # 11. 将一些配置信息写到
        self._write_manifest_info()
        # 12. TODO sdk has special logic. execute the special logic script.
        # game has some special logic. execute the special logic script.called post_script.py
        # here to config the splash screen. 有的渠道要求加入闪屏
        self._add_splash_screen()

        # 13. check cpu supports
        self._check_cpu_support()
        # 14. modify game name if channel specified.
        self._modify_game_name()
        # 15. generate new R.java
        self._generate_r_file(new_package_name, sdk_smali_folder)
            # 16. recompile api
        self._recompile_apk()

        # 17. 添加新的签名
        self._sign_apk()

        # 加固check
        if self.protected != 'none':
            self._protected_apk()
            self._sign_apk()

        # 18. 使用zipalign优化apk包
        self._zipalign_apk()

    def _protected_apk(self):
        self.out_apk_path = protect_utils.protect_apk(self.out_apk_path, os.path.dirname(self.out_apk_path),
                                                      self.protected)

    def _get_last_smali_folder(self, dec_folder):
        smali_num = 1;
        for f in os.listdir(dec_folder):
            if "smali_classes" in f:
                smali_num = max(int(f[-1]), smali_num)

        smali_num = smali_num + 1
        return "smali_classes" + str(smali_num)

    def _prepared_base_smali(self):
        file_utils.copy_files(self.game_apk_path, self.work_dir + "/temp.apk")
        decompile_dir = self.work_dir + "/decompile"
        ret = apk_utils.decompile_apk(self.work_dir + "/temp.apk", decompile_dir)
        if ret:
            msg = "[FAIL] decompile fail base_apk:%s decompile dir:%s" % (self.work_dir + "/temp.apk", decompile_dir)
            secho(msg, fg='red')
            raise UserWarning(msg)
        # 拷贝渠道sdk的资源和jar包到workspace的sdk目录
        sdk_source_dir = file_utils.get_full_path("config/sdk/%s" % self.sdk_name)
        file_utils.copy_files(sdk_source_dir, self.sdk_work_dir)
        # 先将sdk中所有的jar打包成一个classes.dex
        if not file_utils.exists(sdk_source_dir + "/classes.dex"):
            apk_utils.jar2dex(sdk_source_dir, self.sdk_work_dir)

        # 增加白名单过滤
        sdk_smali_name = self._get_last_smali_folder(decompile_dir)
        des_smali_path = os.path.join(decompile_dir, sdk_smali_name)
        # 重新定为最新 smali 目录(dex拆分)
        self.decompile_smali_dir = des_smali_path

        white_list = self.channel_config['libHold'].split('|') if self.channel_config.has_key('libHold') else None
        secho('white list is %s' % white_list, fg='green')

        temp_sdk_smali_dir = self.sdk_work_dir + "/tmp_smali"
        ret = apk_utils.dex2smali(self.sdk_work_dir + "/classes.dex", temp_sdk_smali_dir, "baksmali-2.5.2.jar")
        if ret:
            msg = "[FAIL]dex2smali fail classes.dex source:%s smali dir:%s" % (
                self.sdk_work_dir + "/classes.dex", self.decompile_smali_dir)
            secho(msg, fg='red')
            raise UserWarning(msg)

        # copy
        if white_list:
            for f in os.listdir(temp_sdk_smali_dir):
                can_copy = True
                for path in white_list:
                    can_copy = can_copy if not can_copy else path not in f

                if can_copy:
                    secho("copy file %s" % os.path.join(temp_sdk_smali_dir, f), fg='green')
                    file_utils.copy_files(os.path.join(temp_sdk_smali_dir, f), os.path.join(des_smali_path, f))
                else:
                    secho("ig file %s" % os.path.join(temp_sdk_smali_dir, f), fg='green')
        else:
            file_utils.copy_files(temp_sdk_smali_dir, des_smali_path)

        if "sdkAPK" in self.channel_config and self.channel_config['sdkAPK'] is not None:
            sdk_decompile_dir = self.work_dir + "/sdk_decompile"
            sdk_apk_file = os.path.join(self.sdk_work_dir, self.channel_config['sdkAPK'])
            ret = apk_utils.decompile_apk(sdk_apk_file, sdk_decompile_dir)
            if ret:
                msg = "[FAIL] decompile fail sdk apk:%s decompile dir:%s" % (sdk_apk_file, sdk_decompile_dir)
                secho(msg, fg='red')
                raise UserWarning(msg)

            sdk_smali_path = os.path.join(sdk_decompile_dir, "smali")

            if white_list:
                for f in os.listdir(sdk_smali_path):
                    can_copy = True
                    for path in white_list:
                        can_copy = can_copy if not can_copy else path not in f

                    if can_copy:
                        secho("copy file %s" % os.path.join(sdk_smali_path, f), fg='green')
                        file_utils.copy_files(os.path.join(sdk_smali_path, f), os.path.join(des_smali_path, f))
                    else:
                        secho("ig file %s" % os.path.join(sdk_smali_path, f), fg='green')
            else:
                file_utils.copy_files(sdk_smali_path, des_smali_path)

            if file_utils.exists(os.path.join(sdk_decompile_dir, "unknown")):
                file_utils.copy_files(os.path.join(sdk_decompile_dir, "unknown"),
                                      decompile_dir)

            if file_utils.exists(os.path.join(sdk_decompile_dir, "assets")):
                file_utils.copy_files(os.path.join(sdk_decompile_dir, "assets"), os.path.join(decompile_dir, "assets"))

        return sdk_smali_name

    def _handle_third_plugins(self, package_name, smali_folder):
        plugin_base_folder = file_utils.get_full_path('config/plugin')
        game_plugin_config_folder = file_utils.get_full_path('games/%s/plugin' % self.app_name)
        plugin_configs = self.channel_config.get('third-plugins')
        if not plugin_configs:
            secho("[OK] the channel %s has no supported plugins, the game %s" % (self.channel_name, self.app_name),
                  fg='green')
            return 0
        success_plugin_count = 0
        for plugin_conf in plugin_configs:
            plugin_name = plugin_conf['name']
            cur_plugin_folder = os.path.join(plugin_base_folder, plugin_name)
            if not file_utils.exists(cur_plugin_folder):
                secho('[NOTICE] the plugin %s config folder is not exists' % cur_plugin_folder, fg='yellow')
                continue
            plugin_target_folder = self.work_dir + "/plugins/" + plugin_name
            file_utils.copy_files(cur_plugin_folder, plugin_target_folder)
            plugin_dex_file = os.path.join(plugin_target_folder, "classes.dex")
            if not file_utils.exists(plugin_dex_file):
                # 将该插件下的所有jar包转成classes.dex
                apk_utils.jar2dex(cur_plugin_folder, plugin_target_folder)
            # 再将classes.dex转成smali文件
            ret = apk_utils.dex2smali(plugin_dex_file, self.decompile_smali_dir)
            if ret:
                raise UserWarning("decompile classes.dex fail,dex file path:%s" % plugin_dex_file)
            if 'operations' in plugin_conf:
                self._do_config_operations(plugin_conf['operations'], package_name, plugin_target_folder,
                                           self.decompile_dir, plugin_name, smali_folder, True)
            success_plugin_count += 1
        secho(
            "[INFO] Total plugin num:%s, success handle num:%s" % (str(len(plugin_configs)), str(success_plugin_count)))
        return 0

    def _copy_channel_resources(self):
        res_path = "games/%s/channels/%s" % (self.app_name, self.channel_config['id'])
        res_path = file_utils.get_full_path(res_path)
        if not file_utils.exists(res_path):
            return
        target_res_path = file_utils.get_full_path(self.decompile_dir)
        apk_utils.copy_res_to_apk(res_path, target_res_path)

    def _copy_game_resources(self):
        res_path = "games/%s/res" % self.app_name
        res_path = file_utils.get_full_path(res_path)
        if not file_utils.exists(res_path):
            return
        res_sub_dir = ['assets', 'libs', 'res']
        target_sub_dir = ['assets', 'lib', 'res']
        for i in range(len(res_sub_dir)):
            copy_from = os.path.join(res_path, res_sub_dir[i])
            copy_to = os.path.join(self.decompile_dir, target_sub_dir[i])
            apk_utils.copy_res_to_apk(copy_from, copy_to)

    def _copy_game_root_resources(self):
        res_path = "games/%s/root" % self.app_name
        res_path = file_utils.get_full_path(res_path)
        if not file_utils.exists(res_path):
            return
        copy_to = file_utils.get_full_path(self.decompile_dir)
        apk_utils.copy_res_to_apk(res_path, copy_to)

    def _append_channel_icon_mark(self):
        """
        自动给游戏的图标添加角标
        """
        iconpos = self.channel_config["icon"]
        sdk_source_dir = file_utils.get_full_path("config/sdk/%s" % self.sdk_name)
        conericon = sdk_source_dir + "/coner.png"
        gameicon = file_utils.get_full_path(
            'games/%s/icon/%s' % (self.app_name, self.channel_config["id"])) + "/icon.png"
        has_speical_icon = True
        if not file_utils.exists(gameicon):
            secho("[Start] not found speical in channel folder", fg='green')
            gameicon = file_utils.get_full_path('games/%s/icon' % self.app_name) + "/icon.png"
            has_speical_icon = False

        if iconpos and gameicon and file_utils.exists(conericon):
            base_res_dir = self.decompile_dir
            img_utils.addimgconer(conericon, gameicon, iconpos, base_res_dir)
        elif has_speical_icon:
            img_utils.copy_speical_icon(gameicon, self.decompile_dir)

    def _write_dev_info(self):
        apk_utils.write_developer_info(self.game_config, self.channel_config, self.decompile_dir)

    def _write_plugin_info(self):
        apk_utils.write_plugin_info(self.game_config, self.channel_config, self.decompile_dir)

    def _write_manifest_info(self):
        apk_utils.append_params_to_manifest(self.channel_config, self.decompile_dir)
        # 修改application结点的android:name值
        apk_utils.rename_application_in_manifest(self.channel_config, self.decompile_dir)

    # TODO will imply later
    def _add_splash_screen(self):
        apk_utils.add_splash_screen(self.work_dir, self.channel_config, self.decompile_dir)

    def _check_cpu_support(self):
        apk_utils.check_cpu_support(self.game_config, self.decompile_dir)

    def _modify_game_name(self):
        apk_utils.modify_game_name(self.channel_config, self.decompile_dir)

    def _generate_r_file(self, new_package_name, smail_folder):
        apk_utils.generate_new_r_file(new_package_name, self.decompile_dir, smail_folder)

    def _recompile_apk(self):
        secho("[Start] Start Recompile APK",
              fg='green')
        ret = apk_utils.recompile_apk(self.decompile_dir, self.out_apk_path)
        if ret:
            msg = "[FAIL]Fail to Recomplie APK"
            secho(msg, fg='red')
            raise Exception(msg)

        apk_utils.add_res_to_apk(self.decompile_dir, self.out_apk_path)

    def _sign_apk(self):
        secho("[Start] Sign Apk",
              fg='green')
        apk_utils.sign_apk(self.out_apk_path, self.game_config, self.channel_config)

    def _do_config_operations(self, operations, new_package_name, src_dir, dest_dir, name, sdk_smali_folder, is_plugin):
        if operations is not None:
            for op in operations:
                operation_type = op['type']
                if operation_type == "mergeManifest":
                    # 合并manifest配置文件
                    manifest_from = file_utils.get_full_path(os.path.join(src_dir, op['from']))
                    manifest_from_backup = manifest_from
                    manifest_to = file_utils.get_full_path(os.path.join(dest_dir, op['to']))
                    # 处理一下是不是有针对不同布局的配置
                    if 'orientation' in self.game_config:
                        if self.game_config['orientation'] == 'portrait':
                            manifest_from = manifest_from[:-4] + "_portrait.xml"
                        else:
                            manifest_from = manifest_from[:-4] + "_landscape.xml"
                        if not file_utils.exists(manifest_from):
                            manifest_from = manifest_from_backup
                    secho("[INFO] the from manifest file is %s" % manifest_from)

                    apk_utils.merge_manifest(self.channel_config, manifest_from, manifest_to)
                elif operation_type == "copyRes":
                    # 拷贝资源
                    if op.get('from') is None or op.get('to') is None:
                        msg = "[FAIL] app name:%s channel name:%s the config file is error, " \
                              "'copyRes' need 'from' and 'to' sdk or plugin name:%s" % (
                                  self.app_name, self.channel_name, name)
                        secho(msg, fg='red')
                        raise UserWarning(msg)
                    copy_from = file_utils.get_full_path(os.path.join(src_dir, op['from']))
                    copy_to = file_utils.get_full_path(os.path.join(dest_dir, op['to']))
                    if op['to'] == 'lib':
                        apk_utils.copy_shared_libs(copy_from, copy_to)
                    else:
                        apk_utils.copy_res_to_apk(copy_from, copy_to)
                elif operation_type == "modifySmaliPkg2Current":
                    # 修改smali package路径
                    sdk_package = op['sdkPackage']
                    md_path = sdk_package.split('.')
                    smali_txt_path = os.path.join('/'.join(md_path), '/'.join(op['filePart'].split('.')))
                    file_obj = open(os.path.join(dest_dir, sdk_smali_folder + "/" + smali_txt_path + ".smali"), "r")
                    all_the_text = file_obj.read()
                    file_obj.close()
                    curr_txt_path = os.path.join('/'.join(new_package_name.split('.')),
                                                 '/'.join(op['filePart'].split('.')))

                    all_the_text = all_the_text.replace(smali_txt_path, curr_txt_path)
                    file_obj = open(os.path.join(dest_dir, sdk_smali_folder + "/" + smali_txt_path + ".smali"), "w")
                    file_obj.write(all_the_text)
                    file_obj.close()
                    file_utils.move_file(os.path.join(dest_dir, sdk_smali_folder + "/" + smali_txt_path + ".smali"),
                                os.path.join(dest_dir, sdk_smali_folder + "/" + curr_txt_path + ".smali"))

                elif operation_type == "script":
                    # 执行自定义脚本 TODO
                    pass

    def _zipalign_apk(self):

        secho("[Start] Zip Align",
              fg='green')
        channel_name = re.sub('\s', '', self.channel_name)
        if self.is_release:
            new_apk_file = "%s-%s.apk" % (channel_name, time.strftime('%Y%m%d%H'))
        else:
            new_apk_file = "%s-%s-debug.apk" % (channel_name, time.strftime('%Y%m%d%H'))
        output_dir = file_utils.get_full_path('output/' + self.app_name + '/' + self.channel_name)
        if not file_utils.exists(output_dir):
            os.makedirs(output_dir)
        new_apk_file = os.path.join(output_dir, new_apk_file)
        apk_utils.zipalign_apk(self.out_apk_path, new_apk_file)

        path_file = os.path.join(output_dir, "download_name.txt")
        file_obj = open(path_file, 'w')
        file_obj.write(new_apk_file)
        file_obj.close()

    def _handle_newest_avalon_sdk(self):
        avalon_sdk_work_dir = self.work_dir + "/avalon_sdk"
        avalon_sdk_source = file_utils.get_full_path("config/avalon")
        file_utils.copy_files(avalon_sdk_source, avalon_sdk_work_dir)
        # 先将sdk中所有的jar打包成一个classes.dex
        if not file_utils.exists(avalon_sdk_source + "/classes.dex"):
            apk_utils.jar2dex(avalon_sdk_source, avalon_sdk_work_dir)
        ret = apk_utils.dex2smali(avalon_sdk_work_dir + "/classes.dex", self.decompile_smali_dir, "baksmali-2.5.2.jar")
        if ret:
            msg = "[FAIL]dex2smali fail classes.dex source:%s smali dir:%s" % (
                avalon_sdk_work_dir + "/classes.dex", self.decompile_smali_dir)
            secho(msg, fg='red')
            raise UserWarning(msg)
