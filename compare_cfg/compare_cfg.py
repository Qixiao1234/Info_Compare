#!/usr/bin/env python

# third party
import os
import xlwt
import datetime
import pandas as pd

# 形成pah路径字典
df = pd.read_excel('path_info.xlsx')
pathmap = dict(zip(df['name'],df['path']))
# print('pathmap', pathmap)


# @click.command()
# @click.option('--file1', type=click.Path(), help='file path to first text file', requi0xFF0000=True)
# @click.option('--file2', type=click.Path(), help='file path to second text file', requi0xFF0000=True)

from argparse import ArgumentParser

def pip3_xlwt():
    cmd = 'pip3 install xlwt'
    os.system(cmd)

def pip3_pandas():
    cmd = 'pip3 install pandas'
    os.system(cmd)

try:
    import xlwt
except:
    pip3_xlwt()


try:
    import pandas
except:
    pip3_pandas()

# def get_lastest_file(type, path):
#
#     l = []
#
#     def get_files(path):
#         # l = []
#         lsdir = os.listdir(path)
#         dirs = [i for i in lsdir if os.path.isdir(os.path.join(path, i))]
#         files = [i for i in lsdir if os.path.isfile(os.path.join(path, i))]
#         if files:
#             for f in files:
#                 l.append(os.path.join(path, f))
#                 # l.append(f)
#         if dirs:
#             for d in dirs:
#                 get_files(os.path.join(path, d)) # 递归查找
#         return l
#
#     def findnewestfile(filenames):
#         # filenames = os.listdir(file_path)
#         # print(filenames)
#         name_ = []
#         time_ = []
#         for filename in filenames:
#             if type == filename[-len(type):]:##因我只想查询png类的文件，不用的可以删除
#                 # print filename
#                 c_time = os.path.getctime(filename)
#                 # print(c_time)
#                 # print type(mtime)
#                 name_.append(filename)
#                 time_.append(c_time)
#                 # print(time_)
#                 # print filename,mtime
#         newest_file = name_[time_.index(max(time_))]
#         # print name_
#         # print time_
#         return newest_file
#
#     return findnewestfile(get_files(path))


l = []

def get_files(path):
    # l = []
    lsdir = os.listdir(path)
    dirs = [i for i in lsdir if os.path.isdir(os.path.join(path, i))]
    files = [i for i in lsdir if os.path.isfile(os.path.join(path, i))]
    if files:
        for f in files:
            # l.append(os.path.join(path, f))
            l.append(f)
    if dirs:
        for d in dirs:
            get_files(os.path.join(path, d)) # 递归查找
    return l


def main():
    global l1, l2, all, workload_name, report_path
    workload_name, report_path = '', ''

    parser = ArgumentParser(description='props file compare or check')
    # parser.add_argument('-p', '--prepare', action='store_true',
    #                     help='To prepare the needed packages, recommand to execute first', default=False)
    parser.add_argument('-w', '--workload_name', help='Input workload_name, choose specjbb2015/speccpu/specpower/unixbench/mlc/tdx')
    parser.add_argument('-i', '--input', help='Input golden props file path')
    parser.add_argument('-c', '--compare', help='Input props file path for comparison or check')
    parser.add_argument('-o', '--output', help='Enter the output excel report path')

    args = vars(parser.parse_args())
    # print(args)


    if args['workload_name'] != None:
        workload_name = args['workload_name']
        file2_path = pathmap[workload_name]
    #     if args['workload_name'] == 'specjbb2015':
    #         golden_file = 'specjbb2015.props'
    #     elif args['workload_name'] == 'speccpu':
    #         golden_file = 'ic18.0-lin-core-avx512-rate-20170821.cfg'
    #     elif args['workload_name'] == 'specpower':
    #         golden_file = ['SPECpower_ssj_EXPERT.props', 'SPECpower_ssj_config_sut1.props', 'SPECpower_ssj_config.props', 'SPECpower_ssj.props', 'SPECpower_ssj_old.props', 'SPECpower_ssj_config_sut.props', 'SPECpower_ssj-back.props']
        # elif args['workload_name'] == 'unixbench':
        #     golden_file =
        # elif args['workload_name'] == 'mlc':
        #     golden_file =
        # elif args['workload_name'] == 'tdx':
        #     golden_file =
        # elif args['workload_name'] == '****':
        #     golden_file =


    if args['input'] != None:
        if os.path.exists(args['input']):
            golden_file = args['input']


    if args['compare'] != None:
        if os.path.exists(args['compare']):
            file2 = args['compare']

            # file2_path = args['compare']
            # print(file2_path)


    if args['output'] != None:
        report_path = args['output']
        if not report_path.endswith('/'):
            report_path = report_path + '/'
        if not os.path.exists(args['output']):
            os.mkdir(args['output'])
    # print(report_path)

    golden_file = pathmap['golden_file'] + workload_name
    # print('golden', golden_file)

    GoldenfilePath = get_files(golden_file)


    if ';' in file2_path:
        file2_path = file2_path.split(';')
        for item in file2_path:
            ComparefilePath = os.listdir(item)
            for i in ComparefilePath:
                if i in GoldenfilePath:
                    if not item.endswith('/'):
                        item = item + '/'
                    if not golden_file.endswith('/'):
                        golden_file = golden_file + '/'
                    l1, l2, all = compare(item + i, golden_file + i)
                    to_excel(i, workload_name, l1, l2, all, 66)

    else:
        ComparefilePath = get_files(file2_path)
        # print(ComparefilePath)
        # print(GoldenfilePath)
        for i in ComparefilePath:
            # print(i)
            if i in GoldenfilePath:
                if not file2_path.endswith('/'):
                    file2_path = file2_path + '/'
                if not golden_file.endswith('/'):
                    golden_file = golden_file + '/'
                # print(file2_path + i)
                # print(golden_file + i)
                l1, l2, all = compare(file2_path + i, golden_file + i)
                to_excel(i, workload_name, l1, l2, all, 66)
            else:
                continue
        # parser.add_argument('-f','--full', help='Run all test')


def compare(file1, file2):
    # file1
    file1_list = newline_file_to_list(file1)
    file1_set = set(file1_list)
    file1_dups = unique_dups(file1_list)

    msg = '\nAll lines in {_file1}'.format(_file1=file1)
    # print_result(msg, file1_list)

    msg = '\nDuplicate lines in {_file1}'.format(_file1=file1)
    # print_result(msg, file1_dups)

    # file2
    file2_list = newline_file_to_list(file2)
    file2_set = set(file2_list)
    # file2_dups = unique_dups(file2_list)

    # msg = '\nAll lines in {_file2}'.format(_file2=file2)
    # print_result(msg, file2_list)
    #
    # msg = '\nDuplicate lines in {_file2}'.format(_file2=file2)
    # print_result(msg, file2_dups)

    # # intersection
    # file_intersection = file1_set & file2_set
    # msg = '\nUnique lines in {_file1} AND {_file2} - intersection'.format(
    #         _file1=file1, _file2=file2)
    # print_result(msg, file_intersection)
    #
    # # union
    # file_union = file1_set | file2_set
    # msg = '\nUnique lines in {_file1} OR {_file2} - union'.format(
    #         _file1=file1, _file2=file2)
    # print_result(msg, file_union)

    # file1 only
    file1_only = file1_set - file2_set
    msg = '\nUnique lines in {_file1} ONLY - set difference'.format(
        _file1=file1)
    # print_result(msg, file1_only)

    # file2 only
    file2_only = file2_set - file1_set
    msg = '\nUnique lines in {_file2} ONLY - set difference'.format(
        _file2=file2)
    # print_result(msg, file2_only)
    file1_only = sorted(file1_only)
    file2_only = sorted(file2_only)

    all = list(file2_set | file1_set)

    # file1_only = [i.replace(' = ', '=').replace('#', '') for i in file1_only]
    # file2_only = [i.replace(' = ', '=').replace('#', '') for i in file2_only]
    # file1_only = [i.replace(' = ', '=') for i in file1_only]
    # file2_only = [i.replace(' = ', '=') for i in file2_only]

    file1 = [i.replace(' = ', '=') for i in list(file1_set) if "=" in i]
    file2 = [i.replace(' = ', '=') for i in list(file2_set) if "=" in i]

    all = [i.replace(' = ', '=') for i in all if "=" in i]


    return file1, file2, all


def newline_file_to_list(file_path):
    with open(file_path, 'r') as f:
        file_list = f.read().splitlines()
    return file_list


def print_result(msg, list_or_set):
    # print(msg)
    print('-' * (len(msg) - 1))
    print(sorted(list_or_set))
    print()


def unique_dups(seq):
    seen = set()
    dups = set()
    for item in seq:
        if item not in seen:
            seen.add(item)
        else:
            dups.add(item)
    return list(dups)


# 样式设置
def set_Style(name, size, color, borders_size, color_fore, blod=False):
    style = xlwt.XFStyle()  # 初始化样式
    # 字体
    font = xlwt.Font()
    font.name = name
    font.height = 20 * size  # 字号
    font.bold = blod  # 加粗
    font.colour_index = color  # 默认：0x7FFF 黑色：0x08
    style.font = font
    # 居中
    alignment = xlwt.Alignment()  # 居中
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    style.alignment = alignment
    # 边框
    borders = xlwt.Borders()
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top = xlwt.Borders.THIN
    borders.bottom = borders_size  # 自定义：1：细线；2：中细线；3：虚线；4：点线
    style.borders = borders
    # 背景颜色
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN  # 设置背景颜色的模式(NO_PATTERN; SOLID_PATTERN)
    pattern.pattern_fore_colour = color_fore  # 默认：无色：0x7FFF；黄色：0x0D；蓝色：0x0C
    style.pattern = pattern

    return style


# width 是单元格宽度
def to_excel(st, f, l1, l2, all, width):
    d1 = {}
    d2 = {}
    d3 = {}
    default = {}

    for i in all:
        if '=' in i and '#' in i:
            i = i.split('=')
            default[i[0].replace('#', '')] = i[1]
    # print(default)

    def parse(l, d):
        for item in l:
            # print(item)
            if '=' in item:
                item = item.split('=')
                d[item[0]] = item[1]

    parse(l1, d1)
    parse(l2, d2)
    parse(all, d3)
    # print(d1)
    # print('========================')
    # print(d2)
    # print('========================')
    # print(d3)

    # keys1 = set(list(d1.keys()) + list(d2.keys()))
    keys = list(d3.keys())

    font = xlwt.Font()
    font.name = 'name Times New Roman'
    count = 0
    workbook = xlwt.Workbook()
    # sheet = workbook.add_sheet(f + '_' + str(datetime.datetime.today()).replace(' ', '_')[:19].replace(':', '_'))
    sheet = workbook.add_sheet(st)
    sheet.write(count, 0, workload_name, set_Style('宋体', 12, 0x08, 2, 0x7FFF, blod=True))
    sheet.write(count, 1, 'dut', set_Style('宋体', 12, 0x08, 2, 0x7FFF, blod=True))
    sheet.write(count, 2, 'golden', set_Style('宋体', 12, 0x08, 2, 0x7FFF, blod=True))
    count += 1
    for i in keys:
        if '#' not in i:
            if i in d1:
                # print(d2[i])
                if i in d2:
                    if d1[i] == d2[i]:
                        sheet.write(count, 0, i, set_Style('宋体', 12, 8, 2, 0x7FFF, blod=True))
                        sheet.write(count, 1, d1[i], set_Style('宋体', 12, 8, 2, 0x7FFF, blod=True))  # row, column, value
                        sheet.write(count, 2, d2[i], set_Style('宋体', 12, 8, 2, 0x7FFF, blod=True))
                    else:
                        sheet.write(count, 0, i, set_Style('宋体', 12, 8, 2, 0x7FFF, blod=True))
                        sheet.write(count, 1, d1[i], set_Style('宋体', 12, 2, 2, 0x7FFF, blod=True))  # row, column, value
                        sheet.write(count, 2, d2[i], set_Style('宋体', 12, 2, 2, 0x7FFF, blod=True))
                else:
                    sheet.write(count, 0, i, set_Style('宋体', 12, 8, 2, 0x7FFF, blod=True))
                    sheet.write(count, 1, d1[i], set_Style('宋体', 12, 2, 2, 0x7FFF, blod=True))  # row, column, value
                    sheet.write(count, 2, default[i] + '(default)', set_Style('宋体', 12, 2, 2, 0x7FFF, blod=True))
            else:
                sheet.write(count, 0, i, set_Style('宋体', 12, 8, 2, 0x7FFF, blod=True))
                sheet.write(count, 1, default[i] + '(default)', set_Style('宋体', 12, 2, 2, 0x7FFF, blod=True))  # row, column, value
                sheet.write(count, 2, d2[i], set_Style('宋体', 12, 2, 2, 0x7FFF, blod=True))

            count += 1

    for i in range(3):  # ncol:列数
        sheet.col(i).width = 256 * width  # 设置宽度
    # if not report_path:
    #     report_path = ''
    # print(report_path)
    if not os.path.exists(report_path + workload_name):
        os.mkdir(report_path + workload_name)
    workbook.save(report_path + workload_name + '/' + f + st + '_compare.xls')


if __name__ == '__main__':
    main()
    # print(l1, l2, all)
