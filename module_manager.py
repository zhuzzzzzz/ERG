import os
import shutil
import socket

from ER_Settings import logger, PROJECT_DIR_NAME, IOC_DIR_NAME, DOC_DIR_NAME, PHOEBUS_PATH, PHOEBUS_SERVER_PORT, \
    APP_SRC_MAKEFILE_HOOK, ST_CMD_BEFORE_DBLOAD_HOOK, ST_CMD_AFTER_IOCINIT_HOOK, ST_CMD_AT_DBLOAD_HOOK
from ER_Funcs import add_lines, _get_top, try_makedirs


def add_pva(working_dir, IOC_name, App_name):
    logger.info(f'\tAdding PVA module for {IOC_name}/{App_name}.')
    # App/src/Makefile
    lines_to_add = [
        f'# pva-QSRV\n',
        f'ifdef EPICS_QSRV_MAJOR_VERSION\n',
        f'{App_name}_LIBS += qsrv\n',
        f'{App_name}_LIBS += $(EPICS_BASE_PVA_CORE_LIBS)\n',
        f'{App_name}_DBD += PVAServerRegister.dbd\n',
        f'{App_name}_DBD += qsrv.dbd\n',
        f'endif\n',
        f'\n',
    ]
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, f'{App_name}App', 'src', 'Makefile')
    add_lines(file_path, APP_SRC_MAKEFILE_HOOK(App_name), lines_to_add)


def add_caPutLog(working_dir, IOC_name, App_name):
    logger.info(f'\tAdding caPutLog module for {IOC_name}/{App_name}.')
    # App/src/Makefile
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, f'{App_name}App', 'src', 'Makefile')
    lines_to_add = [
        f'# caPutLog\n'
        f'{App_name}_LIBS += caPutLog\n',
        f'{App_name}_DBD += caPutLog.dbd\n',
        f'{App_name}_DBD += caPutJsonLog.dbd\n',
        f'\n',
    ]
    add_lines(file_path, APP_SRC_MAKEFILE_HOOK(App_name), lines_to_add)

    # iocBoot/ioc/st.cmd
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, 'iocBoot', f'ioc{App_name}',
                             'st.cmd')

    lines_to_add_before_dbLoad = [
        '#caPutLog\n',
        'asSetFilename("${TOP}/${IOC}.acf")\n',
        'epicsEnvSet("EPICS_IOC_LOG_INET","127.0.0.1")\n',
        'iocLogPrefix("${IOC} ")\n',
        'iocLogInit()\n',
        '\n',
    ]
    add_lines(file_path, ST_CMD_BEFORE_DBLOAD_HOOK(App_name), lines_to_add_before_dbLoad)

    lines_to_add_after_iocInit = [
        '\n',
        '#caPutLog after iocInit\n',
        'caPutLogInit "127.0.0.1:7004" 0\n',
        '\n',
    ]
    add_lines(file_path, ST_CMD_AFTER_IOCINIT_HOOK(), lines_to_add_after_iocInit)

    # caPutLog .acf
    template_path = os.path.join(_get_top(), 'template', 'IOC', 'template.acf')
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, f'ioc{App_name}.acf')
    shutil.copy(template_path, file_path)


def add_autosave(working_dir, IOC_name, App_name):
    logger.info(f'\tAdding autosave module for {IOC_name}/{App_name}.')
    # App/src/Makefile
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, f'{App_name}App', 'src', 'Makefile')
    lines_to_add = [
        '# autosave\n'
        f'{App_name}_LIBS += autosave\n',
        f'{App_name}_DBD += asSupport.dbd\n',
        '\n',
    ]
    add_lines(file_path, APP_SRC_MAKEFILE_HOOK(App_name), lines_to_add)

    # iocBoot/ioc/st.cmd
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, 'iocBoot', f'ioc{App_name}',
                             'st.cmd')

    lines_to_add_before_dbLoad = [
        '\n',
        '#autosave\n'
        f'epicsEnvSet SAVE_DIR ${{TOP}}/../../{DOC_DIR_NAME}/autosave/{IOC_name}/${{IOC}}\n',
        'set_requestfile_path("$(SAVE_DIR)")\n',
        'set_savefile_path("$(SAVE_DIR)")\n',
        'set_pass0_restoreFile("${IOC}-automake-pass0.sav")\n',
        'set_pass1_restoreFile("${IOC}-automake.sav")\n',
        'save_restoreSet_DatedBackupFiles(1)\n',
        'save_restoreSet_NumSeqFiles(3)\n',
        'save_restoreSet_SeqPeriodInSeconds(600)\n',
        'save_restoreSet_RetrySeconds(60)\n',
        'save_restoreSet_CallbackTimeout(-1)\n',
        '\n',
    ]
    add_lines(file_path, ST_CMD_BEFORE_DBLOAD_HOOK(App_name), lines_to_add_before_dbLoad)

    lines_to_add_after_iocInit = [
        '#autosave after iocInit\n',
        'makeAutosaveFileFromDbInfo("$(SAVE_DIR)/${IOC}-automake-pass0.req", "autosaveFields_pass0")\n',
        'makeAutosaveFileFromDbInfo("$(SAVE_DIR)/${IOC}-automake.req", "autosaveFields")\n',
        'create_monitor_set("${IOC}-automake-pass0.req",10)\n',
        'create_monitor_set("${IOC}-automake.req",10)\n',
        '\n',
    ]
    add_lines(file_path, ST_CMD_AFTER_IOCINIT_HOOK(), lines_to_add_after_iocInit)

    # doc dir
    dir_path = os.path.join(working_dir, PROJECT_DIR_NAME, DOC_DIR_NAME, 'autosave', IOC_name, f'ioc{App_name}')
    try_makedirs(dir_path)


def add_devIocStats(working_dir, IOC_name, App_name, mode: str):
    logger.info(f'\tAdding devIocStats module(mode:{mode}) for {IOC_name}/{App_name}.')
    # App/src/Makefile
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, f'{App_name}App', 'src', 'Makefile')
    lines_to_add = [
        '# devIocStats\n'
        f'{App_name}_LIBS += devIocStats\n',
        f'{App_name}_DBD += devIocStats.dbd\n',
        '\n',
    ]
    add_lines(file_path, APP_SRC_MAKEFILE_HOOK(App_name), lines_to_add)

    # iocBoot/ioc/st.cmd
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, 'iocBoot', f'ioc{App_name}',
                             'st.cmd')
    if mode.lower() == 'ioc':
        lines_to_add_at_dbLoad = [
            'dbLoadRecords("db/status_ioc.db","IOC=$(IOC)")\n',
        ]
    elif mode.lower() == 'os':
        lines_to_add_at_dbLoad = [
            f'dbLoadRecords("db/status_OS.db","HOST={socket.gethostname()}")\n',
        ]
    else:
        lines_to_add_at_dbLoad = [
            'dbLoadRecords("db/status_ioc.db","IOC=$(IOC)")\n',
            f'dbLoadRecords("db/status_OS.db","HOST={socket.gethostname()}")\n',
        ]
    add_lines(file_path, ST_CMD_AT_DBLOAD_HOOK(App_name), lines_to_add_at_dbLoad)

    # devIocStats .db
    template_path = os.path.join(_get_top(), 'template', 'IOC', 'App', 'Db')
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, IOC_DIR_NAME, IOC_name, f'{App_name}App', 'Db')
    if mode.lower() == 'ioc':
        shutil.copy(os.path.join(template_path, 'status_ioc.db'), os.path.join(file_path, 'status_ioc.db'))
    elif mode.lower() == 'os':
        shutil.copy(os.path.join(template_path, 'status_OS.db'), os.path.join(file_path, 'status_OS.db'))
    else:
        shutil.copy(os.path.join(template_path, 'status_ioc.db'), os.path.join(file_path, 'status_ioc.db'))
        shutil.copy(os.path.join(template_path, 'status_OS.db'), os.path.join(file_path, 'status_OS.db'))

    # opi files
    template_path = os.path.join(_get_top(), 'template', 'opi', 'StatusMonitor')
    file_path = os.path.join(working_dir, PROJECT_DIR_NAME, 'opi', IOC_name, 'StatusMonitor')
    shutil.copytree(template_path, file_path)  # shutil.copytree复制时似乎创建不存在的目录

    # opi command
    template_path = os.path.join(_get_top(), 'template', 'scripts', 'IOC', 'run_status_opi.sh')
    dir_path = os.path.join(working_dir, PROJECT_DIR_NAME, 'scripts', IOC_name)
    file_path = os.path.join(dir_path, 'run_status_opi.sh')
    try_makedirs(dir_path)
    shutil.copy(template_path, file_path)
    lines_to_add = [
        f'export PHOEBUS_PATH={PHOEBUS_PATH}\n',
        f"${{PHOEBUS_PATH}}/phoebus.sh -server {PHOEBUS_SERVER_PORT} -resource 'file:"
        f"{os.path.join(working_dir, PROJECT_DIR_NAME, 'opi', IOC_name, 'StatusMonitor', 'ioc_status.bob')}?"
        f"app=display_runtime&IOC=ioc{App_name}&HOST={socket.gethostname()}&target=window@420x700+200+150'\n",
        '\n',
    ]
    add_lines(file_path, '# execute command\n', lines_to_add)


if __name__ == '__main__':
    # working_dir = '/home/zhu/Project/EPICS'  # 项目TOP路径
    # IOC_name = 'test'  # IOC名称
    # App_name = 'test1'  # IOC内App名称
    # add_pva(working_dir, 'test', 'test1')
    # add_caPutLog(working_dir, 'test', 'test1')
    # add_devIocStats(working_dir, 'test', 'test1', 'ioc')
    # add_autosave(working_dir, 'test', 'test1')
    # App_Db_updater(working_dir, IOC_name, App_name)
    pass
