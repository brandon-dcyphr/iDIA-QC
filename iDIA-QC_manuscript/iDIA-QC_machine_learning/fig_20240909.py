import os.path
import matplotlib.pyplot as plt

import pandas as pd

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.size'] = 10

point_size = 5

base_dddd = '20240909_fig_6'
if not os.path.exists(base_dddd):
    os.mkdir(base_dddd)

PEP_NUM_FLAG = 'Peptide number'
PROT_NUM_FLAG = 'Protein number'
MS1_FLAG = 'MS1'
MS2_FLAG = 'MS2'
DIA_FLAG = 'DIA'
MAIN_FLAG = 'Maintenance'

area_fill_colors = {
    PEP_NUM_FLAG: '#C20008',
    PROT_NUM_FLAG: '#13AFEF',
    DIA_FLAG: '#FF3030',
    MS2_FLAG: '#BF3EFF',
    MS1_FLAG: 'black'
}

line_colors = {
    PEP_NUM_FLAG: '#a9009d',  # 蒂芙尼蓝
    PROT_NUM_FLAG: '#0000EE',  # 蓝色
    MS1_FLAG: 'black',
    DIA_FLAG: '#FF3030',  ##红色
    MS2_FLAG: '#BF3EFF',  ###紫色
    MAIN_FLAG: '#249322'
}

line_color_list = ['#a9009d', '#0000EE', 'black', '#FF3030', '#BF3EFF', '#249322']

maintenance_time_line_color = line_colors[MAIN_FLAG]


# 先加载对应关系
dia_dda_pair_file = 'RadarMfuzz_collection/DIAQC_1516DIA_DDA_Pair_20240102.csv'

dia_peak_data_base_dir = r'E:\data\guomics\gaohuanhuan\DIAQC\DIA_peak_data'
dda_peak_data_base_dir = r'E:\data\guomics\gaohuanhuan\DIAQC\04DDA_FragPipe_analysis_peak_data'


def load_dia_dda_pair_data():
    pair_df = pd.read_csv(dia_dda_pair_file)
    ins_pair_data_dict = {}
    for index, row in pair_df.iterrows():
        dda_raw_name = str(row['DDA'])
        dia_raw_name = str(row['DIA'])
        ins_pair_data_dict[dia_raw_name] = dda_raw_name
    return ins_pair_data_dict


def read_dia_f2(file_path):
    df = pd.read_csv(file_path)
    return df['RT'].median()

def read_dia_f4(file_path):
    df = pd.read_csv(file_path)
    df = df.iloc[0]
    charge1 = df['Charge1 profile']
    charge2 = df['Charge2 profile']
    charge3 = df['Charge3 profile']
    charge4 = df['Charge4 profile']
    charge5 = df['Charge5 profile']
    charge6 = df['Charge6 profile']

    return (charge1, charge2, charge3, charge4, charge5, charge6)


def read_dda_f4(file_path):
    df = pd.read_csv(file_path)
    df = df.iloc[0]
    charge1 = df['Charge1 profile']
    charge2 = df['Charge2 profile']
    charge3 = df['Charge3 profile']
    charge4 = df['Charge4 profile']
    charge5 = df['Charge5 profile']
    charge6 = df['Charge6 profile']

    return (charge1, charge2, charge3, charge4, charge5, charge6)

def read_dda_f2(file_path):
    df = pd.read_csv(file_path)
    return df['retention_time'].median()


def read_dia_f6(file_path):
    df = pd.read_csv(file_path)
    return df.iloc[0]['Median.Mass.Acc.MS1']

def read_dda_f6(file_path):
    df = pd.read_csv(file_path)
    return df.iloc[0]['F6_val']

def read_dia_f11(file_path):
    df = pd.read_csv(file_path)
    return df.iloc[0]['Precursors.Identified']

def read_dia_f12(file_path):
    df = pd.read_csv(file_path)
    return df.iloc[0]['Proteins.Identified']

def read_dia_f13(file_path):
    df = pd.read_csv(file_path)
    return df['Intensity'].median()

def read_dda_f13(file_path):
    df = pd.read_csv(file_path)
    return df['Intensity'].median()

def read_dia_f14(file_path):
    df = pd.read_csv(file_path)
    return df['Intensity'].median()

def read_dda_f11_f12(file_path):
    df = pd.read_csv(file_path)
    f11_val = df.iloc[0]['pept_num']
    f12_val = df.iloc[0]['prot_num']
    return f11_val, f12_val


def draw_f2_pic(draw_data_list, draw_blank_data_list, sign):
    x_list = [dd[0] for dd in draw_data_list]
    y1_list = [dd[1] * 60 for dd in draw_data_list]
    y2_list = [dd[2] for dd in draw_data_list]
    plt.plot(x_list, y1_list, label='DIA RT')
    plt.plot(x_list, y2_list, label='DDA RT')

    for dd in draw_blank_data_list:
        plt.axvline(dd, ymin=0, ymax=1, zorder=5, color=maintenance_time_line_color,linewidth=1)
    plt.legend()
    plt.savefig('{}/F2_{}.pdf'.format(base_dddd, sign))
    plt.close()


# def calc_xxx(data_list):
#     if len(data_list) == 0:
#         return []
#     new_data_list = []
#     for index in range(len(data_list) - 1):
#         if data_list[index] == 0:
#             new_data_list.append(0)
#         else:
#             new_data_list.append(data_list[index + 1] / data_list[index])
#     new_data_list.append(1)
#     return new_data_list


def calc_xxx(data_list):
    if len(data_list) == 0:
        return []
    new_data_list = [0]
    for index in range(1, len(data_list)):
        if data_list[index] == 0:
            new_data_list.append(0)
        else:
            new_data_list.append((data_list[index] - data_list[index - 1]) / data_list[index])
    return new_data_list


def draw_f4_pic(draw_data_list, draw_blank_data_list, sign):
    x_list = [dd[0] for dd in draw_data_list]
    y1_list = [dd[1][0] for dd in draw_data_list]
    y2_list = [dd[1][1] for dd in draw_data_list]
    y3_list = [dd[1][2] for dd in draw_data_list]
    y4_list = [dd[1][3] for dd in draw_data_list]
    y5_list = [dd[1][4] for dd in draw_data_list]
    y6_list = [dd[1][5] for dd in draw_data_list]

    y21_list = [dd[2][0] for dd in draw_data_list]
    y22_list = [dd[2][1] for dd in draw_data_list]
    y23_list = [dd[2][2] for dd in draw_data_list]
    y24_list = [dd[2][3] for dd in draw_data_list]
    y25_list = [dd[2][4] for dd in draw_data_list]
    y26_list = [dd[2][5] for dd in draw_data_list]

    y1_list = calc_xxx(y1_list)
    y2_list = calc_xxx(y2_list)
    y3_list = calc_xxx(y3_list)
    y4_list = calc_xxx(y4_list)
    y5_list = calc_xxx(y5_list)
    y6_list = calc_xxx(y6_list)

    plt.plot(x_list, y1_list, label='DIA Charge1 profile', color=line_color_list[0])
    plt.plot(x_list, y2_list, label='DIA Charge2 profile', color=line_color_list[1])
    plt.plot(x_list, y3_list, label='DIA Charge3 profile', color=line_color_list[2])
    plt.plot(x_list, y4_list, label='DIA Charge4 profile', color=line_color_list[3])
    plt.plot(x_list, y5_list, label='DIA Charge5 profile', color=line_color_list[4])
    plt.plot(x_list, y6_list, label='DIA Charge6 profile', color=line_color_list[5])

    y21_list = calc_xxx(y21_list)
    y22_list = calc_xxx(y22_list)
    y23_list = calc_xxx(y23_list)
    y24_list = calc_xxx(y24_list)
    y25_list = calc_xxx(y25_list)
    y26_list = calc_xxx(y26_list)

    plt.plot(x_list, y21_list, '--', label='DDA Charge1 profile', color=line_color_list[0])
    plt.plot(x_list, y22_list, '--', label='DDA Charge2 profile', color=line_color_list[1])
    plt.plot(x_list, y23_list, '--', label='DDA Charge3 profile', color=line_color_list[2])
    plt.plot(x_list, y24_list, '--', label='DDA Charge4 profile', color=line_color_list[3])
    plt.plot(x_list, y25_list, '--', label='DDA Charge5 profile', color=line_color_list[4])
    plt.plot(x_list, y26_list, '--', label='DDA Charge6 profile', color=line_color_list[5])

    for dd in draw_blank_data_list:
        plt.axvline(dd, ymin=0, ymax=1, zorder=5, color=maintenance_time_line_color,linewidth=1)
    plt.legend()
    plt.savefig('{}/F4_{}.pdf'.format(base_dddd, sign))
    plt.close()


def draw_f6_pic(draw_data_list, draw_blank_data_list, sign):
    x_list = [dd[0] for dd in draw_data_list]
    y1_list = [dd[1] for dd in draw_data_list]
    y2_list = [dd[2] for dd in draw_data_list]
    plt.plot(x_list, y1_list, label='DIA Median.Mass.Acc.MS1')
    plt.plot(x_list, y2_list, label='DDA Median.Mass.Acc.MS1')

    for dd in draw_blank_data_list:
        plt.axvline(dd, ymin=0, ymax=1, zorder=5, color=maintenance_time_line_color,linewidth=1)
    plt.legend()
    plt.savefig('{}/F6_{}.pdf'.format(base_dddd, sign))
    plt.close()


def draw_f11_pic(draw_data_list, draw_blank_data_list, sign):
    x_list = [dd[0] for dd in draw_data_list]
    y1_list = [dd[1] for dd in draw_data_list]
    y2_list = [dd[2] for dd in draw_data_list]

    y1_list = calc_xxx(y1_list)
    y2_list = calc_xxx(y2_list)

    # plt.plot(x_list, y1_list, label='DIA Precursors')
    # plt.plot(x_list, y2_list, label='DDA Precursors')
    plt.plot(x_list, y1_list, label='DIA F11', color=line_color_list[0])
    plt.plot(x_list, y2_list, label='DDA F11', color=line_color_list[1])

    plt.scatter(x_list, y1_list, color=line_color_list[0], s=point_size)
    plt.scatter(x_list, y2_list, color=line_color_list[1], s=point_size)
    for jj, x_i in enumerate(x_list):
        plt.annotate(jj, xy=(x_i, y1_list[jj]), xytext=(5, -5), textcoords='offset points')


    for dd in draw_blank_data_list:
        plt.axvline(dd, ymin=0, ymax=1, zorder=5, color=maintenance_time_line_color,linewidth=1)
    plt.legend()
    plt.savefig('{}/F11_VS_F11_{}.pdf'.format(base_dddd, sign))
    plt.close()


def draw_f12_pic(draw_data_list, draw_blank_data_list, sign):
    x_list = [dd[0] for dd in draw_data_list]
    y1_list = [dd[1] for dd in draw_data_list]
    y2_list = [dd[2] for dd in draw_data_list]

    y1_list = calc_xxx(y1_list)
    y2_list = calc_xxx(y2_list)

    # plt.plot(x_list, y1_list, label='DIA Proteins')
    # plt.plot(x_list, y2_list, label='DDA Proteins')
    plt.plot(x_list, y1_list, label='DIA F12', color=line_color_list[0])
    plt.plot(x_list, y2_list, label='DDA F12', color=line_color_list[1])

    plt.scatter(x_list, y1_list, color=line_color_list[0], s=point_size)
    plt.scatter(x_list, y2_list, color=line_color_list[1], s=point_size)
    for jj, x_i in enumerate(x_list):
        plt.annotate(jj, xy=(x_i, y1_list[jj]), xytext=(5, -5), textcoords='offset points')

    for dd in draw_blank_data_list:
        plt.axvline(dd, ymin=0, ymax=1, zorder=5, color=maintenance_time_line_color,linewidth=1)

    plt.legend()
    plt.savefig('{}/F12_VS_F12_{}.pdf'.format(base_dddd, sign))
    plt.close()


def draw_f13_pic(draw_data_list, draw_blank_data_list, sign):
    x_list = [dd[0] for dd in draw_data_list]
    y1_list = [dd[1] for dd in draw_data_list]
    y2_list = [dd[2] for dd in draw_data_list]

    y1_list = calc_xxx(y1_list)
    y2_list = calc_xxx(y2_list)

    # plt.plot(x_list, y1_list, label='DIA Intensity')
    # plt.plot(x_list, y2_list, label='DDA Intensity')
    plt.plot(x_list, y1_list, label='DIA F13', color=line_color_list[0])
    plt.plot(x_list, y2_list, label='DDA F13', color=line_color_list[1])

    plt.scatter(x_list, y1_list, color=line_color_list[0], s=point_size)
    plt.scatter(x_list, y2_list, color=line_color_list[1], s=point_size)
    for jj, x_i in enumerate(x_list):
        plt.annotate(jj, xy=(x_i, y1_list[jj]), xytext=(5, -5), textcoords='offset points')

    for dd in draw_blank_data_list:
        plt.axvline(dd, ymin=0, ymax=1, zorder=5, color=maintenance_time_line_color,linewidth=1)

    plt.legend()
    plt.savefig('{}/F13_VS_F13_{}.pdf'.format(base_dddd, sign))
    plt.close()


def draw_f14_pic(draw_data_list, draw_blank_data_list, sign):
    x_list = [dd[0] for dd in draw_data_list]
    y1_list = [dd[1] for dd in draw_data_list]
    y2_list = [dd[2] for dd in draw_data_list]

    y1_list = calc_xxx(y1_list)
    y2_list = calc_xxx(y2_list)

    # plt.plot(x_list, y1_list, label='DIA Intensity')
    # plt.plot(x_list, y2_list, label='DDA Intensity')
    plt.plot(x_list, y1_list, label='DIA F14', color=line_color_list[0])
    plt.plot(x_list, y2_list, label='DDA F13', color=line_color_list[1])

    plt.scatter(x_list, y1_list, color=line_color_list[0], s=point_size)
    plt.scatter(x_list, y2_list, color=line_color_list[1], s=point_size)
    for jj, x_i in enumerate(x_list):
        plt.annotate(jj, xy=(x_i, y1_list[jj]), xytext=(5, -5), textcoords='offset points')

    for dd in draw_blank_data_list:
        plt.axvline(dd, ymin=0, ymax=1, zorder=5, color=maintenance_time_line_color,linewidth=1)

    plt.legend()
    plt.savefig('{}/F13_VS_F14_{}.pdf'.format(base_dddd, sign))
    plt.close()


def draw_f7_pic(draw_data_list, draw_blank_data_list, sign):
    x_list = [dd[0] for dd in draw_data_list]
    y1_list = [dd[1] for dd in draw_data_list]
    y2_list = [dd[2] for dd in draw_data_list]

    y1_list = calc_xxx(y1_list)
    y2_list = calc_xxx(y2_list)

    # plt.plot(x_list, y1_list, label='DIA MS1.Signal')
    # plt.plot(x_list, y2_list, label='DDA MS1.Signal')
    plt.plot(x_list, y1_list, label='DIA F7', color=line_color_list[0])
    plt.plot(x_list, y2_list, label='DDA F7', color=line_color_list[1])

    plt.scatter(x_list, y1_list, color=line_color_list[0], s=point_size)
    plt.scatter(x_list, y2_list, color=line_color_list[1], s=point_size)
    for jj, x_i in enumerate(x_list):
        plt.annotate(jj, xy=(x_i, y1_list[jj]), xytext=(5, -5), textcoords='offset points')

    for dd in draw_blank_data_list:
        plt.axvline(dd, ymin=0, ymax=1, zorder=5, color=maintenance_time_line_color,linewidth=1)

    plt.legend()
    plt.savefig('{}/F7_VS_F7_{}.pdf'.format(base_dddd, sign))
    plt.close()


def draw_f9_pic(draw_data_list, draw_blank_data_list, sign):
    x_list = [dd[0] for dd in draw_data_list]
    y1_list = [dd[1] for dd in draw_data_list]
    y2_list = [dd[2] for dd in draw_data_list]


    y1_list = calc_xxx(y1_list)
    y2_list = calc_xxx(y2_list)

    # plt.plot(x_list, y1_list, label='DIA MS2.Signal')
    # plt.plot(x_list, y2_list, label='DDA MS2.Signal')
    plt.plot(x_list, y1_list, label='DIA F9', color=line_color_list[0])
    plt.plot(x_list, y2_list, label='DDA F9', color=line_color_list[1])

    plt.scatter(x_list, y1_list, color=line_color_list[0], s=point_size)
    plt.scatter(x_list, y2_list, color=line_color_list[1], s=point_size)
    for jj, x_i in enumerate(x_list):
        plt.annotate(jj, xy=(x_i, y1_list[jj]), xytext=(5, -5), textcoords='offset points')

    for dd in draw_blank_data_list:
        plt.axvline(dd, ymin=0, ymax=1, zorder=5, color=maintenance_time_line_color,linewidth=1)

    plt.legend()
    plt.savefig('{}/F9_VS_F9_{}.pdf'.format(base_dddd, sign))
    plt.close()


def read_area():
    area_file = r"E:\data\guomics\gaohuanhuan\DIAQC\DDA_read_mzXML_peak_data\area_data.csv"
    area_df = pd.read_csv(area_file)
    area_data = {}
    for dd, row in area_df.iterrows():
        area_data[str(row['FileName']).removesuffix('.csv')] = (row['ms1_area'], row['ms2_area'])

    return area_data


def read_dia_f7(file_path):
    df = pd.read_csv(file_path)
    return df.iloc[0]['MS1.Signal']


def read_dia_f9(file_path):
    df = pd.read_csv(file_path)
    return df.iloc[0]['MS2.Signal']


def read_timeline():
    dia_dda_pair = load_dia_dda_pair_data()
    df = pd.read_excel(r"E:\data\guomics\gaohuanhuan\DIAQC\DIAQC1516_Pre_log_timeline_draw_figure20240909-1935.xlsx")
    # df = df.dropna(subset='20220620sign')
    groups = df.groupby('Selection')

    area_data = read_area()

    for sign, group_data in groups:
        draw_f2_data_list = []
        draw_f4_data_list = []
        draw_f6_data_list = []
        draw_11_data_list = []
        draw_12_data_list = []
        draw_13_data_list = []
        draw_14_data_list = []
        draw_f7_data_list = []
        draw_f9_data_list = []
        draw_blank_data_list = []
        group_data.sort_values(by='Time', inplace=True)
        group_data = group_data.reset_index(drop=True)
        lll = len(group_data)
        file_list = []
        for index, row in group_data.iterrows():
            print('{}/{}'.format(index, lll))
            status = row['Status']
            dia_file_name = row['Event']
            # if dia_file_name == 'B20200224xiangn_ml_30min_DIA':
            #     continue
            if status == 'Normal':
                dda_file_name = dia_dda_pair[dia_file_name]
                file_list.append({'DIA file': dia_file_name, 'DDA file': dda_file_name})
                # 加载F2数据
                # draw_f2_data_list.append((index, read_dia_f2(os.path.join(dia_peak_data_base_dir, dia_file_name, 'F2.csv')), read_dda_f2(os.path.join(dda_peak_data_base_dir, dda_file_name, 'F2.csv'))))
                # draw_f4_data_list.append((index, read_dia_f4(os.path.join(dia_peak_data_base_dir, dia_file_name, 'F4.csv')), read_dda_f4(os.path.join(dda_peak_data_base_dir, dda_file_name, 'F4.csv'))))
                # draw_f6_data_list.append((index, read_dia_f6(os.path.join(dia_peak_data_base_dir, dia_file_name, 'F6.csv')), read_dda_f6(os.path.join(dda_peak_data_base_dir, dda_file_name, 'F6.csv'))))

                dia_f11 = read_dia_f11(os.path.join(dia_peak_data_base_dir, dia_file_name, 'F11.csv'))
                dia_f12 = read_dia_f12(os.path.join(dia_peak_data_base_dir, dia_file_name, 'F12.csv'))
                dda_f11, dda_f12 = read_dda_f11_f12(os.path.join(dda_peak_data_base_dir, dda_file_name, 'F11_F12.csv'))
                #
                dia_f13_val = read_dia_f13(os.path.join(dia_peak_data_base_dir, dia_file_name, 'F13.csv'))
                dia_f14_val = read_dia_f13(os.path.join(dia_peak_data_base_dir, dia_file_name, 'F14.csv'))
                #
                dda_f13_val = read_dda_f13(os.path.join(dda_peak_data_base_dir, dda_file_name, 'F13.csv'))
                #
                draw_11_data_list.append((index, dia_f11, dda_f11))
                draw_12_data_list.append((index, dia_f12, dda_f12))
                #
                draw_13_data_list.append((index, dia_f13_val, dda_f13_val))
                draw_14_data_list.append((index, dia_f14_val, dda_f13_val))
                dia_f7_val = read_dia_f7(os.path.join(dia_peak_data_base_dir, dia_file_name, 'F7.csv'))
                dia_f9_val = read_dia_f9(os.path.join(dia_peak_data_base_dir, dia_file_name, 'F9.csv'))

                area_val = area_data.get(dda_file_name)
                if area_val:
                    dda_f7_val, dda_f9_val = area_data.get(dda_file_name)
                    draw_f7_data_list.append((index, dia_f7_val, dda_f7_val))
                    draw_f9_data_list.append((index, dia_f9_val, dda_f9_val))
                else:
                    print('-------------', dia_file_name, '==', dda_file_name)
            else:
                draw_blank_data_list.append(index)

        if sign == 7:
            print('------------')
        # draw_f2_pic(draw_f2_data_list, draw_blank_data_list, sign)
        # draw_f4_pic(draw_f4_data_list, draw_blank_data_list, sign)
        # draw_f6_pic(draw_f6_data_list, draw_blank_data_list, sign)

        draw_f7_pic(draw_f7_data_list, draw_blank_data_list, sign)
        draw_f9_pic(draw_f9_data_list, draw_blank_data_list, sign)
        draw_f11_pic(draw_11_data_list, draw_blank_data_list, sign)
        draw_f12_pic(draw_12_data_list, draw_blank_data_list, sign)
        draw_f13_pic(draw_13_data_list, draw_blank_data_list, sign)
        draw_f14_pic(draw_14_data_list, draw_blank_data_list, sign)

        savedf = pd.DataFrame(file_list)
        savedf.to_csv('{}/file_info_{}.csv'.format(base_dddd, sign))


read_timeline()
