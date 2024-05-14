import datetime
import os
import shutil
import time
from pathlib import Path


# 获取文件的最后修改时间,时间戳
def get_file_mtime(file_path):
    if not os.path.exists(file_path):
        return None
    if os.path.isdir(file_path):
        # 如果是文件夹，就文件夹内所有文件的修改时间，取最后那个为整个文件夹的修改时间
        return int(get_dir_file_mtime(file_path))
    else:
        file_stat = os.stat(file_path)
        return int(file_stat.st_mtime)


def get_dir_file_mtime(dir_path):
    mtime = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            f_mtime = os.stat(os.path.join(root, file)).st_mtime
            if f_mtime > mtime:
                mtime = f_mtime
    return mtime


def get_first_day_of_previous_month():
    # 获取当前日期
    today = datetime.datetime.today()
    # 获取当前月份的第一天
    first_day_of_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # 获取上个月的第一天
    first_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
    # 获取上个月的最后一天
    last_day_of_previous_month = first_day_of_previous_month.replace(day=1)
    return last_day_of_previous_month


# 判断文件的最后修改时间是否是指定时间外（分钟）
def is_file_modified_days_out_minute(file_path, minutes=10):
    file_path = str(file_path)
    if file_path.endswith('.wiff') or file_path.endswith('.WIFF'):
        # 如果是.wiff文件，那么就再检测一下wiff.scan文件是否存在，并且时间是否满足
        wiff_scan_path = file_path + '.scan'
        wiff_last_modified_time = get_file_mtime(file_path)
        wiff_scan_last_modified_time = get_file_mtime(wiff_scan_path)
        if wiff_last_modified_time is None or wiff_scan_last_modified_time is None:
            return False
        return wiff_last_modified_time + (minutes * 60) < time.time() and wiff_scan_last_modified_time + (minutes * 60) < time.time()
    else:
        last_modified_time = get_file_mtime(file_path)
        if last_modified_time is None:
            return False
        return last_modified_time + (minutes * 60) < time.time()


# 获取文件的大小
def get_file_size(abs_file_path):
    # 判断文件是否存在
    if not os.path.exists(abs_file_path):
        return None
    if os.path.isdir(abs_file_path):
        return get_dir_file_size(abs_file_path)
    else:
        file_info = Path(abs_file_path)
        return file_info.stat().st_size


def get_dir_file_size(dir_path):
    size_count = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            f = Path(os.path.join(root, file))
            size = f.stat().st_size
            size_count += size
    return size_count


def get_file_md5(abs_file_path):
    return _md5.get_file_md5(abs_file_path)


# 压缩文件，包含顶层文件夹
# save_path，压缩后文件的存储目录，压缩后的名称为设定的save_path+.zip
# root_dir 要压缩文件夹的父级目录
# base_dir 要压缩文件夹的名称
def zip_file(abs_base_save_path, root_dir_path, base_dir):
    zip_name = shutil.make_archive(abs_base_save_path, 'zip', root_dir=root_dir_path, base_dir=base_dir)
    if os.path.exists(zip_name):
        return True
    else:
        return False


# def delete_file(file_path):
#     if os.path.isdir(file_path):
#         shutil.rmtree(file_path)
#     else:
#         os.remove(file_path)


# 构建目标目录
# 构建规则，根据原始文件父级文件夹的创建时间，获取年和月创建两级文件夹
def build_and_create_target_path(org_base_dir, org_parent_dir, org_file_name, target_base_dir, mass_machine_name):
    # 先获取原始文件父级目录的创建时间
    org_parent_dir_path = os.path.join(org_base_dir, org_parent_dir)
    org_create_timestamp = os.stat(org_parent_dir_path).st_ctime
    org_create_time = datetime.datetime.fromtimestamp(org_create_timestamp)
    target_root_path = os.path.join(target_base_dir, mass_machine_name,
                                    str(org_create_time.year), 'M' + str(org_create_time.month).zfill(2))
    if not os.path.exists(target_root_path):
        os.makedirs(target_root_path)
    target_parent_path = os.path.join(target_root_path, org_parent_dir)
    if not os.path.exists(target_parent_path):
        os.mkdir(target_parent_path)
    abs_target_path = os.path.join(target_parent_path, org_file_name)
    relative_target_path = abs_target_path.removeprefix(target_base_dir).replace('\\', '/').removeprefix('/')
    return abs_target_path, relative_target_path


def build_and_create_target_path_v2(file_relative_dir, org_file_name, target_base_dir, mass_machine_name, time_file_path):
    #
    org_create_timestamp = os.stat(time_file_path).st_ctime
    org_create_time = datetime.datetime.fromtimestamp(org_create_timestamp)
    target_root_path = os.path.join(target_base_dir, mass_machine_name,
                                    str(org_create_time.year), 'M' + str(org_create_time.month).zfill(2))
    if not os.path.exists(target_root_path):
        os.makedirs(target_root_path)

    target_parent_path = os.path.join(target_root_path, file_relative_dir)
    if not os.path.exists(target_parent_path):
        os.makedirs(target_parent_path)
    abs_target_path = os.path.join(target_parent_path, org_file_name)
    relative_target_path = abs_target_path.removeprefix(target_base_dir).replace('\\', '/').removeprefix('/')
    return abs_target_path, relative_target_path


if __name__ == '__main__':
    pass
    # org_parent_dir_path = os.path.join('D:\\ProgramData\\mass_offline_backup\\src')
    # org_create_time = os.stat(org_parent_dir_path).st_ctime
    # import datetime
    # ddd = datetime.datetime.fromtimestamp(org_create_time)
    # print(org_create_time)
    # print(ddd)
    # print(ddd.year)
    # print(ddd.month)
