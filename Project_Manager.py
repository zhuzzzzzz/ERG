import os
import shutil

from ER_Funcs import try_makedirs, _get_top, add_lines
from ER_Settings import logger, PROJECT_DIR_NAME, IOC_DIR_NAME, LOG_DIR_NAME, MODULE_PATH, DB_FILE_SUFFIX, \
    ST_CMD_AT_DBLOAD_HOOK


def ioc_make(working_dir, IOC_name):
    App_Db_updater(working_dir, IOC_name)
    dir_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name)
    os.chdir(dir_path)
    logger.debug(f'\tMove to "{dir_path}", make.')
    os.system('make')


def ioc_remake(working_dir, IOC_name):
    App_Db_updater(working_dir, IOC_name)
    dir_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name)
    os.chdir(dir_path)
    logger.debug(f'\tMove to "{dir_path}", remake.')
    os.system('make distclean; make')


def ioc_file_manager(working_dir, IOC_name, App_name_list):
    # change mode of st.cmd
    dir_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, 'iocBoot')
    for item in App_name_list:
        file_path = os.path.join(dir_path, f'ioc{item}')
        os.chdir(file_path)
        logger.debug(f'\tMove to {file_path}.')
        os.system(f'chmod u+x st.cmd')
        logger.debug(f'\tAdd execute permission to st.cmd.')

    #


def project_file_generator(working_dir):
    # create RELEASE.local
    lines_to_add = []
    for key, value in MODULE_PATH.items():
        lines_to_add.append(f'{key} = {value}\n')
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, 'RELEASE.local')
    with open(file_path, 'w') as f:
        f.writelines(lines_to_add)
        logger.debug(f'\tCreate RELEASE.local at "{file_path}".')


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


# 根据Db文件夹中的文件更新Makefile
def App_Db_updater(working_dir, IOC_name):
    template_path = os.path.join(_get_top(), 'template', 'IOC', 'App', 'Db', 'Makefile')
    ioc_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name)
    for app_dir in os.listdir(ioc_path):
        if app_dir.endswith('App'):
            file_path = os.path.join(ioc_path, app_dir, 'Db')
            shutil.copy(template_path, file_path)  # 从template中复制Makefile确保此函数可以多次执行
            logger.debug(f'\tUpdating "{os.path.join(file_path, "Makefile")}".')
            db_list = []
            for f in os.listdir(file_path):
                if f.endswith(DB_FILE_SUFFIX):
                    db_list.append(f'DB += ' + f + '\n')
            if db_list:
                file_path = os.path.join(file_path, 'Makefile')
                add_lines(file_path, f'#DB += xxx.db\n', db_list)
