import os
from subprocess import Popen, TimeoutExpired, PIPE

from ER_Settings import logger, DEFAULT_WORKING_DIR, PROJECT_DIR_NAME, IOC_DIR_NAME
from ER_Funcs import try_makedirs, config_check, config_set
from Project_Manager import project_file_generator, project_scripts_generator


def project_generator(working_dir):
    if not working_dir:
        working_dir = DEFAULT_WORKING_DIR
    logger.info(f'\t设置工作路径为: "{working_dir}".')

    project_dir_path = os.path.join(working_dir, PROJECT_DIR_NAME)
    if config_check(project_dir_path, 'Project', 'status', 'initialized'):
        logger.info(f'\t项目已初始化, 跳过初始化.')
    else:
        try_makedirs(project_dir_path)
        ioc_top_path = os.path.join(project_dir_path, IOC_DIR_NAME)
        try_makedirs(ioc_top_path)

        project_file_generator(working_dir)
        project_scripts_generator(working_dir)

        config_set(project_dir_path, 'Project', 'status', 'initialized')
        logger.info(f'\t设置项目初始化.')


def ioc_generator(working_dir, IOC_name, App_name_list):
    project_generator(working_dir)

    project_dir_path = os.path.join(working_dir, PROJECT_DIR_NAME)
    if config_check(project_dir_path, IOC_name):
        logger.info(f'\t配置文件提示已创建IOC:{IOC_name}.')
        return False
    else:
        TOP_IOC_dir = os.path.join(project_dir_path, IOC_DIR_NAME, IOC_name)
        try_makedirs(TOP_IOC_dir)
        os.chdir(TOP_IOC_dir)
        logger.debug(f'\tMove to "{TOP_IOC_dir}".')

        for item in App_name_list:
            logger.info(f'\t执行 makeBaseApp.pl -t ioc {item}.')
            os.system(f'makeBaseApp.pl -t ioc {item}')
            logger.info(f'\t执行 makeBaseApp.pl -i -t ioc {item}.')
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

        config_set(project_dir_path, IOC_name, 'type', 'IOC')
        config_set(project_dir_path, IOC_name, 'app_list', str(App_name_list))
        config_set(project_dir_path, IOC_name, 'status', 'notBuild')
        logger.info(f'\t配置IOC:{IOC_name}, 并更新配置文件.')
        return True


if __name__ == '__main__':
    working_dir = '/home/zhu/Project/EPICS'  # 项目TOP路径
    IOC_name = 'test'  # IOC名称
    App_name = ['test1', 'test2', 'test3', 'test4', ]  # IOC内App名称

    # project_generator(working_dir)
    ioc_generator(working_dir, IOC_name, App_name)
