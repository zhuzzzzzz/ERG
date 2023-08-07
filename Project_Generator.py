import os
import shutil
from subprocess import Popen, TimeoutExpired, PIPE

from ER_Settings import logger, LOG_DIR_NAME
from ER_Settings import DEFAULT_WORKING_DIR, PROJECT_DIR_NAME, IOC_DIR_NAME, MODULE_PATH
from ER_Funcs import App_Db_updater, try_makedirs, _get_top, add_lines


def ioc_generator(working_dir, IOC_name, App_name_list):
    if working_dir:
        try_makedirs(working_dir)
    else:
        working_dir = DEFAULT_WORKING_DIR
    logger.info(f'\tSet working directory: "{working_dir}".')

    TOP_IOC_dir = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name)
    try_makedirs(TOP_IOC_dir)
    os.chdir(TOP_IOC_dir)
    logger.info(f'\tMove to "{TOP_IOC_dir}".')

    for item in App_name_list:
        logger.info(f'\tExecute makeBaseApp.pl -t ioc {item}.')
        os.system(f'makeBaseApp.pl -t ioc {item}')
        logger.info(f'\tExecute makeBaseApp.pl -i -t ioc {item}.')
        # 这里必须使用信号 PIPE 而不是自己创建的文本流，这样才能使用 communicate 函数
        proc = Popen(args=f'makeBaseApp.pl -i -t ioc {item}', shell=True, encoding='utf-8', stdin=PIPE, stdout=PIPE,
                     stderr=PIPE)
        try:
            outs, errs = proc.communicate(input=f'{item}\n', timeout=15)
            print(outs)
            if errs:
                logger.error(f'\t{errs}.')
        except TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            print(outs)
            if errs:
                logger.error(f'\t{errs}.')


def ioc_file_manager(working_dir, IOC_name, App_name_list):
    # change mode of st.cmd
    dir_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, 'iocBoot')
    for item in App_name_list:
        file_path = os.path.join(dir_path, f'ioc{item}')
        os.chdir(file_path)
        logger.info(f'\tMove to {file_path}.')
        os.system(f'chmod u+x st.cmd')
        logger.info(f'\tAdd execute permission to st.cmd.')

    #


def project_file_manager(working_dir):
    # create RELEASE.local
    lines_to_add = []
    for key, value in MODULE_PATH.items():
        lines_to_add.append(f'{key} = {value}\n')
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, 'RELEASE.local')
    with open(file_path, 'w') as f:
        f.writelines(lines_to_add)
        logger.info(f'\tCreate RELEASE.local at "{file_path}".')


def ioc_make(working_dir, IOC_name):
    App_Db_updater(working_dir, IOC_name)
    dir_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name)
    os.chdir(dir_path)
    logger.info(f'\tMove to "{dir_path}", make.')
    os.system('make')


def ioc_remake(working_dir, IOC_name):
    App_Db_updater(working_dir, IOC_name)
    dir_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name)
    os.chdir(dir_path)
    logger.info(f'\tMove to "{dir_path}", remake.')
    os.system('make distclean; make')


def project_scripts_generator(working_dir):
    try_makedirs(os.path.join(working_dir, PROJECT_DIR_NAME, 'scripts'))

    # run_iocLogServer.sh
    template_path = os.path.join(_get_top(), 'template', 'scripts', 'run_iocLogServer.sh')
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, 'scripts', 'run_iocLogServer.sh')
    shutil.copy(template_path, file_path)
    lines_to_add = [
        f'export EPICS_IOC_LOG_FILE_NAME=${{script_dir}}/../{LOG_DIR_NAME}/iocLog/iocLog.log\n',
    ]
    add_lines(file_path, '# export log file name\n', lines_to_add)
    try_makedirs(os.path.join(working_dir, PROJECT_DIR_NAME, LOG_DIR_NAME, 'iocLog'))

    # run_ioc_all_Apps.sh
    template_path = os.path.join(_get_top(), 'template', 'scripts', 'run_allIoc.sh')
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, 'scripts', 'run_allIoc.sh')
    shutil.copy(template_path, file_path)
    lines_to_add = [
        f'top_path=$script_dir/../{IOC_DIR_NAME}\n',
    ]
    add_lines(file_path, '# top path\n', lines_to_add)
    #


if __name__ == '__main__':
    working_dir = '/home/zhu/Project/EPICS'  # 项目TOP路径
    IOC_name = 'test'  # IOC名称
    App_name = ['test1', 'test2', 'test3', 'test4', ]  # IOC内App名称

    ioc_generator(working_dir, IOC_name, App_name)
    ioc_file_manager(working_dir, IOC_name, App_name)
