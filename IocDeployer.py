#!/usr/bin/python3

import argparse
import os
import shutil
import pathlib
import logging

from ER_Settings import logger, DEFAULT_WORKING_DIR, PROJECT_DIR_NAME, IOC_DIR_NAME
from ER_Funcs import try_makedirs, config_set
from Project_Generator import ioc_generator
from Project_Manager import ioc_file_manager, ioc_make, ioc_remake
from IocModule_manager import add_pva, add_autosave, add_caPutLog, add_devIocStats


# create: 创建IOC及相关文件
def create(args):
    working_dir = args.path  # 项目TOP路径
    IOC_name = args.IOC  # IOC名称
    App_name_list = args.Apps  # IOC内App名称

    run_flag = False
    if not ioc_generator(working_dir, IOC_name, App_name_list):
        ans = input(f'项目内已存在相同名称IOC目录, 是否将其移除并重新生成?|[y/n]?\n')
        while True:
            if ans.lower() == 'yes' or ans.lower() == 'y':
                logger.info(f'\t移除IOC目录: {IOC_name}/.')
                shutil.rmtree(os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name))
                ioc_generator(working_dir, IOC_name, App_name_list)
                run_flag = True
                break
            elif ans.lower() == 'no' or ans.lower() == 'n':
                break
            else:
                ans = input(f'输入无效, 请重新输入.|[y/n]?\n')
    else:
        run_flag = True

    if run_flag:
        ioc_file_manager(working_dir, IOC_name, App_name_list)
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


# make: IOC编译
def make(args):
    working_dir = args.path  # 项目TOP路径
    IOC_name = args.IOC  # IOC名称

    project_dir_path = os.path.join(working_dir, PROJECT_DIR_NAME)
    if IOC_name:
        for item in IOC_name:
            logger.info(f'\t编译IOC: {item}.')
            ioc_make(working_dir, item)
            config_set(project_dir_path, item, 'status', 'Built')
    else:
        os.chdir(os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME))
        for item in [ioc for ioc in os.listdir() if os.path.isdir(ioc)]:
            logger.info(f'\t编译IOC: {item}.')
            ioc_make(working_dir, item)
            config_set(project_dir_path, item, 'status', 'Built')


# remake: IOC重新编译
def remake(args):
    working_dir = args.path  # 项目TOP路径
    IOC_name = args.IOC  # IOC名称

    if IOC_name:
        for item in IOC_name:
            logger.info(f'\t卸载并重新编译IOC: {item}.')
            ioc_remake(working_dir, item)
    else:
        os.chdir(os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME))
        for item in [ioc for ioc in os.listdir() if os.path.isdir(ioc)]:
            logger.info(f'\t卸载并重新编译IOC: {item}.')
            ioc_remake(working_dir, item)


def main():
    # argparse
    parser = argparse.ArgumentParser(description='IOC快速部署脚本.')
    parser.add_argument('-p', '--path', type=pathlib.Path, help='设置工作路径的绝对路径, 默认为当前工作路径.')
    parser.add_argument('-v', '--verbose', action="store_true", help='显示调试信息.')

    subparsers = parser.add_subparsers(
        help='子解析器命令. 运行以下命令获取详细帮助: "python IocDeployer.py create/make/remake -h".')

    parser_create = subparsers.add_parser('create', help='创建IOC及相关文件.')
    parser_create.add_argument('IOC', type=str, help='IOC项目名称.')
    parser_create.add_argument('Apps', type=str, nargs='+', help='IOC内App名称列表.')
    parser_create.add_argument('--pva', action="store_true", help='添加PVA模块.')
    parser_create.add_argument('--putlog', action="store_true", help='添加caPutLog模块.')
    parser_create.add_argument('--status-ioc', action="store_true",
                               help='添加devIocStats模块的IOC状态监视功能.')
    parser_create.add_argument('--status-os', action="store_true",
                               help='添加devIocStats模块的OS状态监视功能.')
    parser_create.add_argument('--autosave', action="store_true", help='添加autosave模块.')
    parser_create.set_defaults(func=create)

    parser_make = subparsers.add_parser('make', help='IOC编译.')
    parser_make.add_argument('IOC', type=str, nargs='*',
                             help='IOC名称列表, 不输入任何参数时默认对项目中的全部IOC进行操作.')
    parser_make.set_defaults(func=make)

    parser_remake = subparsers.add_parser('remake', help='IOC重新编译.')
    parser_remake.add_argument('IOC', type=str, nargs='*',
                               help='IOC名称列表, 不输入任何参数时默认对项目中的全部IOC进行操作.')
    parser_remake.set_defaults(func=remake)

    args = parser.parse_args()

    # print(args)

    run_flag = True
    #
    if args.verbose:
        logger.setLevel(logging.DEBUG)
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
        ans = input(f'Args: {args}\n'
                    f'Confirm to execute?|[y/n]?\n')
        if ans.lower() == 'yes' or ans.lower() == 'y':
            args.func(args)
            break
        elif ans.lower() == 'no' or ans.lower() == 'n':
            print('Canceled.')
            break


if __name__ == '__main__':
    main()
