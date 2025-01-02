# -*- coding: utf-8 -*-
import click
from packing import apps
from protecting import protect

__author__ = 'Kevin Sun <sun-w@klab.com>'


@click.group()
def cli():
    pass


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version 1.0')
    ctx.exit()


@cli.command()
@click.option('-r', '--release', is_flag=True, help=u'标识是否打release版本')
@click.option('-g', '--gameid', type=str, help=u'让用户自己选择需要打包的游戏id')
@click.option('-c', '--channelid', type=str, help=u'让用户自己选择需要打包的渠道id')
@click.option('-e', '--encryptmono', type=click.Choice(['5.1', '5.6', '']), default='', help=u'是否使用加密的mono,支持5.1 5.6')
@click.option('-t', '--thread', type=int, default=1, help=u'打渠道包时运行的线程数,打多个渠道时,可以用多个线程,加快打包')
@click.option('-V', '--version', is_flag=True, expose_value=False,
              is_eager=True, callback=print_version, help=u'打印当前打包命令的版本号')
@click.option('-v', '--verbose', count=True, help='increase output verbosity.\n-v=info\n-vv=debug')
@click.option('-p', '--protected', type=click.Choice(['360', 'klab', 'none']), default='none', help=u'是否使用加固')
@click.pass_context
def pack_game(ctx, release, gameid, channelid, encryptmono, thread, verbose, protected):
    """package multi platform"""

    apps.entry(release, gameid, channelid, encryptmono, thread, verbose, protected)


@cli.command()
@click.option('-r', '--release', is_flag=True, help=u'标识是否打release版本')
@click.option('-g', '--game', type=str, default='*', help=u'打包的游戏,这个是设制游戏ID,"*"号代表全部,多个的话用","号分隔')
@click.option('-c', '--channel', type=str, default='*', help=u'打包的渠道,这个是设制渠道ID,"*"号代表合,多个的话用","号分隔')
@click.option('-t', '--thread', type=int, default=1, help=u'打渠道包时运行的线程数,打多个渠道时,可以用多个线程,加快打包')
@click.option('-V', '--version', is_flag=True, expose_value=False,
              is_eager=True, callback=print_version, help=u'打印当前打包命令的版本号')
@click.option('-v', '--verbose', count=True, help='increase output verbosity.\n-v=info\n-vv=debug')
def pack_game_auto(ctx, release, game, channel, thread, verbose):
    """自动打包多渠道"""
    apps.entry_auto(release, game, channel, thread, verbose)


@cli.command()
@click.option('-p', '--path', type=str, default='', help=u'重打包目录')
@click.option('-s', '--signname', type=str, default='Lapis', help=u'签名选择')
def re_pack_apk(path, signname):
    """自动打包多渠道"""
    protect.re_build_apk(path, signname)

