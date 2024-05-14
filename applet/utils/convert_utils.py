
from applet.obj.Entity import FileTypeEnum, FileInfo


# 做一下转换，把win的路径转为linux的
def convert_to_file_name(file_path):
    # 做一下转换，把win的路径转为linux的
    file_path = file_path.replace('\\', '/')
    file_name = file_path[file_path.rfind('/') + 1:]
    return file_name


# 转换mzXML名称
def convert_to_mzXML_name(file_info: FileInfo):
    file_name = file_info.file_name
    file_type = file_info.file_type
    if file_type == FileTypeEnum.D:
        file_info.mzXML_file_name = file_name.replace('.d', '.mzXML')
        file_info.mzML_file_name = file_name.replace('.d', '.mzML')
        file_info.base_file_name = file_name.replace('.d', '')
    elif file_type == FileTypeEnum.RAW:
        file_info.mzXML_file_name = file_name.replace('.raw', '.mzXML')
        file_info.mzML_file_name = file_name.replace('.raw', '.mzML')
        file_info.base_file_name = file_name.replace('.raw', '')
    elif file_type == FileTypeEnum.WIFF:
        file_info.mzXML_file_name = file_name.replace('.wiff', '.mzXML')
        file_info.mzML_file_name = file_name.replace('.wiff', '.mzML')
        file_info.base_file_name = file_name.replace('.wiff', '')
    else:
        return None
