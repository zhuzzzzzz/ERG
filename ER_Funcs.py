import os
import configparser

from ER_Settings import logger, CONFIG_FILE_NAME


def _get_top():
    return os.path.dirname(__file__)


def _escape_str(string: str):
    return string.replace('\n', '\\n')


def try_makedirs(d):
    try:
        os.makedirs(d)
    except FileExistsError:
        logger.debug(f'\ttry_makedirs("{d}") -> FileExistsError Exception.')
        return False
    else:
        logger.debug(f'\ttry_makedirs("{d}") -> Success.')
        return True


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


def config_check(project_dir_path, section, key=None, value_to_compare=None):
    config_file_path = os.path.join(project_dir_path, CONFIG_FILE_NAME)
    if os.path.exists(config_file_path):
        conf = configparser.ConfigParser()
        conf.read(config_file_path)
        if section in conf and key is None:
            logger.debug(f'\tConfig中存在section {section}.')
            return True
        elif section not in conf:
            logger.debug(f'\tConfig中不存在section {section}.')
            return False
        if conf.get(section, key, fallback=None) == value_to_compare:
            logger.debug(f'\tConfig["{section}"]["{key}"] == {value_to_compare}.')
            return True
    else:
        logger.debug(f'\t配置文件不存在 或 Config["{section}"]["{key}"]!={value_to_compare}.')
        return False


def config_set(project_dir_path, section, key, value_to_set):
    config_file_path = os.path.join(project_dir_path, CONFIG_FILE_NAME)
    if os.path.exists(config_file_path):
        conf = configparser.ConfigParser()
        conf.read(config_file_path)
        try:
            conf.add_section(section)
        except configparser.DuplicateSectionError:
            pass
        conf.set(section, key, value_to_set)
        with open(config_file_path, 'w') as f:
            conf.write(f)
        logger.debug(f'\t配置文件更新成功: Config["{section}"]["{key}"]={CONFIG_FILE_NAME}.')
    else:
        logger.debug(f'\t配置文件不存在, 已创建新配置文件.')
        config = configparser.ConfigParser()
        config[section] = {
            key: value_to_set,
        }
        with open(config_file_path, 'w') as f:
            config.write(f)


if __name__ == '__main__':
    # App_Db_updater('/home/zhu/Project/EPICS', 'test')
    pass
