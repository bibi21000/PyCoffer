# -*- encoding: utf-8 -*-
"""Password plugin Click interface

"""
__author__ = 'bibi21000 aka Sébastien GALLET'
__email__ = 'bibi21000@gmail.com'

import click

from pycoffer import main_lib

# ~ @click.group(help='Manage passwords in coffer.')
# ~ @click.command(help='Manage passwords in coffer.')
# ~ def password():
    # ~ pass

@click.group()
def cli():
    pass

@cli.group(help='Manage passwords in coffer.')
def password():
    pass

@password.command(help='List passwords in coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
def ls(conf, coffer):
    with main_lib.open_coffer(conf, coffer, 'r') as ff:
        with ff.plugin('password') as plg:
            print('Name', "Username", "Url", "Owner")
            for member in plg.getmembers():
                print(member.name, member.username, member.url, member.owner)

@password.command(help='Delete password in coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option("--name", help='Name of the password to delete.')
@click.option("--owner", help='Owner of the password to delete.')
def delete(conf, coffer, name, owner):
    with main_lib.open_coffer(conf, coffer, 'a') as ff:
        with ff.plugin('password') as plg:
            pwd = plg.get((owner,name)).to_public()
            plg.delete(pwd)

@password.command(help='Import passwords from chrome.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option( "-i","--file", help='Csv file exported by chrome.')
def import_chrome(conf, coffer, file):
    with main_lib.open_coffer(conf, coffer, 'a') as ff:
        with ff.plugin('password') as plg:
            plg.import_chrome(file)

@password.command(help='Add password in coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option("--name", help='Name of the password.')
@click.option("--username", help='Username to login.')
@click.option("--url", help='Url linked to password.')
@click.option("--password", help='The password.')
@click.option("--note", help='A note.')
@click.option("--owner", help="Owner of the password.")
def add(conf, coffer, name, username, url, password, note, owner):
    with main_lib.open_coffer(conf, coffer, 'a') as ff:
        with ff.plugin('password') as plg:
            dpass = plg.Info(name=name, username=username, url=url,
                password=password, note=note, owner=owner)
            plg.add(dpass)

@password.command(help='Show password in coffer.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option("--name", help='Name of the password to delete.')
@click.option("--owner", help='Owner of the password to delete.')
def show(conf, coffer, name, owner):
    with main_lib.open_coffer(conf, coffer, 'a') as ff:
        with ff.plugin('password') as plg:
            print('Owner', "Name", "Username", "Url", "Password")
            pwd = plg.get((owner,name))
            print(pwd.owner, pwd.name, pwd.username, pwd.url, pwd.password)

@password.command(help='Copy password in coffer to clipboard.')
@main_lib.opt_configuration
@main_lib.opt_coffer
@click.option("--name", help='Name of the password to delete.')
@click.option("--owner", help='Owner of the password to delete.')
def clip(conf, coffer, name, owner):
    with main_lib.open_coffer(conf, coffer, 'a') as ff:
        with ff.plugin('password') as plg:
            import pyperclip
            pwd = plg.get((owner,name))
            pyperclip.copy(pwd.password)
