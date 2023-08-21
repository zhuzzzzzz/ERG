import logging
import os
import getpass

# logging设置
logger = logging.getLogger('')
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s - %(funcName)s')

#
CONFIG_FILE_NAME = 'config.ini'

# 默认工作路径
DEFAULT_WORKING_DIR = os.getcwd()

# 默认目录名称
PROJECT_DIR_NAME = 'ER'  # TOP目录名称
IOC_DIR_NAME = 'IOC'  # IOC目录名称
SETTINGS_DIR_NAME = 'settings'  # 配置文件存放目录名称
LOG_DIR_NAME = 'log'  # 日志文件存放目录名称
OPI_DIR_NAME = 'opi'  # opi文件存放目录名称
SCRIPTS_DIR_NAME = 'scripts'  # scripts文件存放目录名称

# db文件后缀
DB_FILE_SUFFIX = ('.db', '.substitutions')

# Phoebus
PHOEBUS_PATH = '/home/zhu/Phoebus/product-sns-4.6.10-SNAPSHOT'
PHOEBUS_SERVER_PORT = 4918

# EPICS模块安装路径, for RELEASE.local
MODULE_PATH = {
    'caPutLog': '/home/zhu/EPICS/Module/caPutLog',
    'autosave': '/home/zhu/EPICS/Module/autosave-R5-10-2',
    'devIocStats': '/home/zhu/EPICS/Module/iocStats',
}


# 文本替换设置
##############################
def APP_SRC_MAKEFILE_HOOK(App_name):
    return f'#{App_name}_LIBS += xxx\n'


def ST_CMD_BEFORE_DBLOAD_HOOK(App_name):
    return f'{App_name}_registerRecordDeviceDriver pdbbase\n'


def ST_CMD_AT_DBLOAD_HOOK(App_name):
    return f'#dbLoadRecords("db/{App_name}.db","user={getpass.getuser()}")\n'


def ST_CMD_AFTER_IOCINIT_HOOK():
    return f'#seq sncxxx,"user={getpass.getuser()}"\n'
