from pyteomics import mzxml, mzml


# 获取质谱文件仪器型号名称
def read_ms_info(mzxml_path):
    return read_mzml(mzxml_path)


# 读取mzzml文件，获取仪器名称
def read_mzxml(mzxml_path):
    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/msInstrument/msModel')
    ms_model = 'DEFAULT'
    for msModel in rawdata_reader:
        ms_model = msModel['value']
        break

    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/parentFile')
    file_type = None
    for msModel in rawdata_reader:
        file_type = msModel['fileType']
        break

    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/msInstrument')
    ins_id = None
    for msModel in rawdata_reader:
        ins_id = str(msModel['msInstrumentID'])
        break
    return ins_id, ms_model


def read_mzml(mzxml_path):
    rawdata_reader = mzml.iterfind(mzxml_path, 'referenceableParamGroupList/referenceableParamGroup')
    ms_model = 'DEFAULT'
    for msModel in rawdata_reader:
        ms_model = msModel['value']
        break

    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/parentFile')
    file_type = None
    for msModel in rawdata_reader:
        file_type = msModel['fileType']
        break

    rawdata_reader = mzxml.iterfind(mzxml_path, 'msRun/msInstrument')
    ins_id = None
    for msModel in rawdata_reader:
        ins_id = str(msModel['msInstrumentID'])
        break
    return ins_id, ms_model


mzml_process = mzml.MzML('E:\data\guomics\gaohuanhuan\\10\mzXML\\A20201013xiangn_ml_30min_DIA.mzML')
mmm = mzml_process.get_by_id('IC1')
print(str(mmm.get('instrument serial number')))
# read_ms_info('E:\data\guomics\gaohuanhuan\\10\mzXML\A20201013xiangn_ml_30min_DIA.mzML')

