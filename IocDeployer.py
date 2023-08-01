#!/usr/bin/python3

import argparse
import os
import pathlib
import logging

from ER_Settings import logger, DEFAULT_WORKING_DIR
from ER_Funcs import try_makedirs
from project_manager import ioc_generator, ioc_file_manager, ioc_make, ioc_remake, project_file_manager
from module_manager import add_pva, add_autosave, add_caPutLog, add_devIocStats


def create(args):
    working_dir = args.path  # 项目TOP路径
    IOC_name = args.IOC  # IOC名称
    App_name_list = args.Apps  # IOC内App名称

    ioc_generator(working_dir, IOC_name, App_name_list)
    ioc_file_manager(working_dir, IOC_name, App_name_list)
    project_file_manager(working_dir)
    if args.pva:
        for app in App_name_list:
            add_pva(working_dir, IOC_name, app)
    if args.putlog:
        for app in App_name_list:
            add_caPutLog(working_dir, IOC_name, app)
    if args.autosave:
        for app in App_name_list:
            add_autosave(working_dir, IOC_name, app)
    if args.status_ioc and not args.status_os:
        for app in App_name_list:
            add_devIocStats(working_dir, IOC_name, app, mode='ioc')
    elif not args.status_ioc and args.status_os:
        for app in App_name_list:
            add_devIocStats(working_dir, IOC_name, app, mode='os')
    elif args.status_ioc and args.status_os:
        for app in App_name_list:
            add_devIocStats(working_dir, IOC_name, app, mode='all')


def make(args):
    working_dir = args.path  # 项目TOP路径
    IOC_name = args.IOC  # IOC名称
    ioc_make(working_dir, IOC_name)


def remake(args):
    working_dir = args.path  # 项目TOP路径
    IOC_name = args.IOC  # IOC名称
    ioc_remake(working_dir, IOC_name)


# cargparse
parser = argparse.ArgumentParser(description='IOC快速部署脚本.')
parser.add_argument('-p', '--path', type=pathlib.Path,
                    help='Absolute path to working directory, default to current working directory.')
parser.add_argument('-v', '--verbose', action="store_true", help='Show details.')

subparsers = parser.add_subparsers(
    help='Subparsers. Run "python IocDeployer.py create/make/remake -h" for more details.')

parser_create = subparsers.add_parser('create', help='Create the project.')
parser_create.add_argument('IOC', type=str, help='IOC name.')
parser_create.add_argument('Apps', type=str, nargs='+', help='App name list in IOC.')
parser_create.add_argument('--pva', action="store_true", help='Add PVA module.')
parser_create.add_argument('--putlog', action="store_true", help='Add caPutLog module.')
parser_create.add_argument('--status-ioc', action="store_true",
                           help='Add devIocStats module and set IOC status monitor.')
parser_create.add_argument('--status-os', action="store_true", help='Add devIocStats module and set OS status monitor.')
parser_create.add_argument('--autosave', action="store_true", help='Add autosave module.')
parser_create.set_defaults(func=create)

parser_make = subparsers.add_parser('make', help='Build the specific IOC.')
parser_make.add_argument('IOC', type=str, help='IOC name.')
parser_make.set_defaults(func=make)

parser_remake = subparsers.add_parser('remake', help='Rebuild the specific IOC.')
parser_remake.add_argument('IOC', type=str, help='IOC name.')
parser_remake.set_defaults(func=remake)

args = parser.parse_args()

# main
run_flag = True
#
if args.verbose:
    logger.setLevel(logging.INFO)
if args.path:
    if os.path.isabs(args.path):
        try_makedirs(args.path)
    else:
        print('Invalid input: Input path is not an absolute path!')
        run_flag = False
else:
    args.path = DEFAULT_WORKING_DIR
#
while run_flag:
    ans = input(f'=================== Ioc Deployer Run Confirmation ===================\n'
                f'Subcommand: {args.func.__name__}\n'
                f'Args: {args}\n'
                f'Confirm to execute?|[y/n]?\n')
    if ans.lower() == 'yes' or ans.lower() == 'y':
        print('=================== Ioc Deployer Running ===================')
        args.func(args)
        break
    elif ans.lower() == 'no' or ans.lower() == 'n':
        print('=================== Ioc Deployer Canceled ===================')
        break
