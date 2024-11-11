import datetime
import os
import shutil
import time
from pathlib import Path


def get_file_mtime(file_path):
    if not os.path.exists(file_path):
        return None
    if os.path.isdir(file_path):
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
    today = datetime.datetime.today()
    first_day_of_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
    last_day_of_previous_month = first_day_of_previous_month.replace(day=1)
    return last_day_of_previous_month


def is_file_modified_days_out_minute(file_path, minutes=10):
    file_path = str(file_path)
    if file_path.endswith('.wiff') or file_path.endswith('.WIFF'):
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

def get_file_size(abs_file_path):
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


def zip_file(abs_base_save_path, root_dir_path, base_dir):
    zip_name = shutil.make_archive(abs_base_save_path, 'zip', root_dir=root_dir_path, base_dir=base_dir)
    if os.path.exists(zip_name):
        return True
    else:
        return False


def build_and_create_target_path(org_base_dir, org_parent_dir, org_file_name, target_base_dir, mass_machine_name):
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

