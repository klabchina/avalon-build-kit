# -*- coding: utf-8 -*-
__author__ = 'mason'

import click
from protecting import protect


@click.group()
def cli():
    pass


@cli.command()
@click.option('-p', '--path', type=str, default='', help=u'给APK 加固')
@click.option('-m', '--method', type=click.Choice(['klab', '360']), default='klab', help=u'加固方式')
@click.option('-s', '--signname', type=str, default='Penguin', help=u'签名选择')
@click.option('-e', '--env', type=bool, default=False, help=u'是否为DEV环境 默认正式')
def protectedapk(path, method, signname, env):
    """加壳"""
    protect.protect_apk(path, method, signname, env)

@cli.command()
@click.option('-p', '--path', type=str, default='', help=u'给APK 加固')
@click.option('-m', '--method', type=click.Choice(['klab', '360']), default='klab', help=u'加固方式')
@click.option('-s', '--signname', type=str, default='Penguin', help=u'签名选择')
@click.option('-e', '--env', type=bool, default=False, help=u'是否为DEV环境 默认正式')
def protectedso(path, method, signname, env):
    """加壳"""
    protect.protect_so_only(path, method, signname, env)



@cli.command()
@click.option('-p', '--path', type=str, default='', help=u'给aab 加固')
@click.option('-s', '--signname', type=str, default='Penguin', help=u'签名选择')
@click.option('-ks', '--keystorename', type=str, default='', help=u'keystore name')
@click.option('-ksp', '--keystorepass', type=str, default='Penguin', help=u'keystore pass')
@click.option('-ka', '--keyalias', type=str, default='Penguin', help=u'alias name')
@click.option('-kap', '--keyaliaspassword', type=str, default='Penguin', help=u'alias password')
@click.option('-e', '--env', type=bool, default=False, help=u'是否为DEV环境 默认正式')
def protectedaab(path, signname, keystorename, keystorepass, keyalias, keyaliaspassword, env):
    """aab 加壳"""
    protect.protect_aab(path, signname, keystorename, keystorepass, keyalias, keyaliaspassword, env)


@cli.command()
@click.option('-p', '--path', type=str, default='', help=u'给APK 添加mono编译')
@click.option('-v', '--mono_version', type=click.Choice(['5.1', '5.6']), default='5.6', help=u'给APK 添加mono编译')
@click.option('-g', '--game_name', type=str, default='Penguin', help=u'游戏名字')
@click.option('-e', '--env', type=bool, default=False, help=u'是否为DEV环境 默认正式')
def mono_protected(path, mono_version, game_name, env):
    """加壳"""
    protect.protect_apk_mono(path, mono_version, game_name, env)
