import os
import shutil

from ER_Settings import logger
from ER_Settings import DB_FILE_SUFFIX, PROJECT_DIR_NAME, IOC_DIR_NAME


def _get_top():
    return os.path.dirname(__file__)


def _escape_str(string: str):
    return string.replace('\n', '\\n')


def try_makedirs(d):
    try:
        os.makedirs(d)
    except FileExistsError:
        logger.info(f'\ttry_makedirs("{d}") -> FileExistsError Exception.')
    else:
        logger.info(f'\ttry_makedirs("{d}") -> Success.')


# 读取文件，根据给定的字符串匹配位置，添加列表里的字符串至文件中匹配的位置处，返回添加后的文件字符串列表
def add_lines(file_path, idx_str, str_list: list):
    with open(file_path, 'r') as f:
        file = f.readlines()
    try:
        idx = file.index(idx_str)
    except ValueError:
        logger.error(f'add_lines: 文件"{file_path}"中不存在与"{_escape_str(idx_str)}"匹配的文本行 -> None')
        return None
    first_half = file[0:idx + 1]
    second_half = file[idx + 1:]
    new_file = []
    new_file.extend(first_half)
    new_file.extend(str_list)
    new_file.extend(second_half)
    with open(file_path, 'w') as f:
        f.writelines(new_file)
    return new_file


# 根据Db文件夹中的文件更新Makefile，从template中复制Makefile确保此函数可以多次执行
def App_Db_updater(working_dir, IOC_name):
    template_path = os.path.join(_get_top(), 'template', 'IOC', 'App', 'Db', 'Makefile')
    ioc_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name)
    for app_dir in os.listdir(ioc_path):
        if app_dir.endswith('App'):
            file_path = os.path.join(ioc_path, app_dir, 'Db')
            shutil.copy(template_path, file_path)
            logger.info(f'\tUpdating "{os.path.join(file_path, "Makefile")}".')
            db_list = []
            for f in os.listdir(file_path):
                if f.endswith(DB_FILE_SUFFIX):
                    db_list.append(f'DB += ' + f + '\n')
            if db_list:
                file_path = os.path.join(file_path, 'Makefile')
                add_lines(file_path, f'#DB += xxx.db\n', db_list)


if __name__ == '__main__':
    App_Db_updater('/home/zhu/Project/EPICS', 'test')
