#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import os
from utils import log_utils
from utils import file_utils
from os.path import dirname

plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')

__author__ = 'Kevin Sun <sun-w@klab.com>'


class MyCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py'):
                if filename[:-3] == "__init__":
                    continue
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['cli']


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version 4.0')
    ctx.exit()


@click.command(cls=MyCLI)
@click.option('-V', '--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.option('-v', '--verbose', count=True, help='increase output verbosity.\n-v=info\n-vv=debug')
@click.pass_context
def cli(ctx, verbose):
    base_dir = dirname(dirname(os.path.realpath(__file__))) + "/"
    ctx.obj['base_dir'] = base_dir
    # init log utils
    log_utils.init(base_dir)
    # init file utils
    file_utils.init(base_dir)
    pass


if __name__ == '__main__':
    cli(obj={})
