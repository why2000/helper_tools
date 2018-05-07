# -*- coding:utf-8 -*-
'''
    本模块提供与数据处理、生成、备份的相关函数
'''
import re
import os
import sys
import csv
import xlrd
import time
import shutil
import codecs
import random
import chardet
import numpy as np
from .. import helper
from copy import deepcopy
try:
    import cPickle as pickle
except:
    import pickle


def knowledge_transfer(knowledge_path='../../database/knowledge/', main_path="../../database/main-data/", main_filename='main_data.txt', knowledge_filename='knowledge.xlsx'):
    '''
        本函数用于基于knowledge文件生成全新的主数据文件
        注：调用此函数会完全清除主数据文件中的数据
        [knowledge_path](str): knowledge文件所在目录
        [main_path](str): 主数据文件生成目录
        [main_filename](str): 主数据文件文件名
        [knowledge_filename](str): knowledge文件文件名
    '''
    '''
        knowledge已作废，无效
    '''
    try:
        knowledge_data = xlrd.open_workbook(str(knowledge_path+knowledge_filename))
    except:
        print("Knowledge file '" + knowledge_path + "' not found")
    else:
        main_file = open(str(main_path+main_filename), "w")
        knowledge_table = knowledge_data.sheets()[0]
        knowledge_nrows = knowledge_table.nrows
        knowledge_ncols = knowledge_table.ncols
        for i_xlsx in range(1, knowledge_nrows):
            row_values = knowledge_table.row_values(i_xlsx)
            while '' in row_values:
                row_values.remove('')
            # 主问题与大类的对应在另外文件里有代码直接用
            main_que = row_values[0].strip()
            modified_row = [main_que] + [x.replace('*', '').replace('|', '').strip() for x in row_values[7:]]
            for sentence in modified_row[1:]:
                main_row = [sentence.strip(), main_que]
                main_file.write('||'.join(main_row)+'\n')
            if not i_xlsx % 1000:
                print(str(int(i_xlsx/1000))+'000 lines Finished')
    finally:
        if main_file:
            main_file.close()
        if knowledge_data:
            knowledge_data.release_resources()
            del knowledge_data
def data_expander(daily_base_path = '../../database/daily-data/',main_path = '../../database/main-data/',others_path = '../../database/others/strategy/',main_filename = 'main_data.txt', strategy_filename = 'strategy_data.txt',readed_filename = 'news_readed.txt',repeat=True, strict=True):
    '''
        本函数用于利用新的对话文件扩充主数据文件
        注：对话文件中的策略问题（无对应主问题的对话）保存在database/others/strategy.txt内
        [daily_base_path](str): 每日对话文件所在目录
        [main_path](str): 主数据文件所在目录
        [others_path](str): 其他数据文件（用于策略问题）所在目录
        [main_filename](str): 主数据文件文件名
        [strategy_filename](str): 策略数据文件文件名
        [readed_filename](str): 用于记录已读取对话的文件的文件名
        [repeat](bool): 是否允许重复数据（默认为是）
        [strict](bool): 严格模式：排除所有不含有中文的问题（默认为真）
    '''
    if repeat:
        name_repeat = 'repeat'
    else:
        name_repeat = ''
    try:
        with open(daily_base_path+readed_filename+name_repeat, 'r') as readed_file:
            news_readed = list(map(lambda x: x.strip(), readed_file.readlines()))
    except:
        news_readed = []
    if not os.path.exists(main_path+main_filename+name_repeat):
        with open(main_path+main_filename+name_repeat,'w') as buf_main_file:
            pass
    sub_que_readed = set([line[0] for line in helper.file_tools.read_txt_as_csv(main_path+main_filename+name_repeat, divider='||')])
    readed_file = open(daily_base_path+readed_filename , 'a+')
    main_file = open(main_path+main_filename+name_repeat, "a+")
    strategy_file = open(others_path+strategy_filename, "a+")
    all_news = os.listdir(daily_base_path)
    for one_news in all_news:
        if one_news in news_readed:
            continue
        if not one_news.endswith('.xlsx'):
            continue
        readed_file.write(one_news+'\n')
        news_path = daily_base_path+one_news
        try:
            news_data = xlrd.open_workbook(str(news_path))
        except:
            print('Error: file damaged: "'+news_path+'"')
        else:
            buf = ''
            buf_sub = ''
            news_table = news_data.sheets()[0]
            news_nrows = news_table.nrows
            news_ncols = news_table.ncols
            for i_xlsx in range(1, news_nrows):
                row_values = news_table.row_values(i_xlsx)
                sub_que = row_values[7].strip()
                sub_que = helper.file_tools.simbol_killer(helper.file_tools.html_killer(sub_que))
                if not repeat:
                    if sub_que in sub_que_readed:
                        continue
                # if buf_sub == sub_que:
                #     if sub_que in sub_que_readed:
                #         print(buf+" Already in !")
                #     print(buf+" Same !")
                buf_sub = sub_que
                sub_que_readed.add(sub_que)
                main_class = row_values[4].strip().split('#')[0]
                if not row_values[10]:
                    continue
                else:
                    main_que = row_values[10].strip()
                if strict:
                    if not re.search(u"[\u4e00-\u9fa5]", sub_que):
                        continue
                if row_values[9].strip() == '是':
                    # while '' in row_values:
                    #     row_values.remove('')
                    strategy_row = '||'.join(row_values[3:])+'\n'
                    strategy_row = helper.file_tools.simbol_killer(helper.file_tools.html_killer(strategy_row))
                    strategy_file.write(strategy_row)
                    continue
                # 主问题与大类的对应在另外文件里有代码直接用
                main_que = row_values[10].strip()
                if helper.file_tools.simbol_killer(helper.file_tools.num_killer(sub_que.strip())) == '':
                    continue
                main_row = [sub_que.strip(), main_que.strip(), main_class.strip()]
                main_row_write = '||'.join(main_row)
                main_row_write = re.sub(r' +',' ',main_row_write)
                # if buf == main_row_write:
                #     if sub_que in sub_que_readed:
                #         print(buf+" Already in !")
                #     print(buf+" Same !")
                #     print(main_row_write)
                #     print(main_que)
                #     print(sub_que)
                buf = main_row_write
                main_file.write(main_row_write+'\n')
                # if not i_xlsx % 1000:
                #     print(str(int(i_xlsx/1000))+'000 lines Finished')
            print("One news Finished: "+one_news)
            if news_data:
                news_data.release_resources()
                del news_data
    readed_file.close()
    main_file.close()


def data_backup(main_path='../../database/main-data/', main_filename='main_data.txt', max_num=7):
    '''
        本函数用于备份数据文件
        [main_path](str): 数据文件所在的目录
        [main_filename](str): 数据文件的文件名
        [max_num](int): 最大备份数（默认为7）
    '''
    backup_names = [backup_name for backup_name in os.listdir(main_path) if backup_name.startswith(main_filename+'.backup') ]
    backup_names.sort(key=lambda x: x.lstrip(main_filename+'.backup'))
    backup_names.reverse()
    main_file = main_path+main_filename
    backup_file = main_file + '.backup' + str(time.time())
    shutil.copy2(main_file, backup_file)
    if len(backup_names) > max_num:
        # print(backup_names)
        for i in range(1, len(backup_names)-max_num+2):
            # print(i)
            # print(backup_names[-i])
            del_file = main_path + backup_names[-i]
            os.remove(del_file)

    
def data_revert(times=1, main_path='../../database/main-data/', main_filename='main_data.txt'):
    '''
        本函数用于将数据文件回溯至以前的版本
        [times](int): 回溯版本数(0为不回朔)
        [main_path](str): 数据文件所在的目录
        [main_filename](str): 数据文件的文件名
    '''
    now_file = main_path+main_filename
    data_backup(main_path=main_path, main_filename=main_filename)
    backup_names = [backup_name for backup_name in os.listdir(main_path) if backup_name.startswith(main_filename+'.backup')]
    backup_names.sort(key=lambda x: x.lstrip(main_filename+'.backup'))
    backup_names.reverse()
    backup_file = main_path+backup_names[times]
    shutil.copyfile(backup_file, now_file)

def clean_readed_list(daily_path='../../database/daily-data/',readed_filename = 'news_readed.txt'):
    '''
        本函数用于清除已读取的对话列表
        [daily_path](str): 对话文件所在文件夹
        [readed_filename](str): 已读取列表文件的文件名
    '''
    readed_file = daily_path+readed_filename
    if os.path.exists(readed_file):
        os.remove(readed_file)
    return None

def clean_main_data(main_path='../../database/main-data/',main_filename='main_data.txt',
daily_path='../../database/daily-data/',readed_filename = 'news_readed.txt'):
    '''
        本函数用于清除主数据文件（不会清除其备份）
        [main_path](str): 数据文件所在的目录
        [main_filename](str): 数据文件的文件名
        [daily_path](str): 对话文件所在文件夹
        [readed_filename](str): 已读取列表文件的文件名
    '''
    clean_readed_list(daily_path, readed_filename)
    main_file = main_path+main_filename
    if os.path.exists(main_file):
        os.remove(main_file)
    return None

def test_train_split(main_path='../../database/main-data/', main_filename='main_data.txt',test_train_path='../../database/test_train/',test_rate=0.3, strict=True, seed=9481, symmetrical = True):
    '''
        本函数用于分割主数据文件（速度很快），将主数据文件按指定比例随机分割为测试文件和训练文件
        [main_path](str): 数据文件所在的目录
        [main_filename](str): 数据文件的文件名
        [test_train_path](str): 测试及训练文件生成在的目录
        [test_rate](float): 测试文件内容占主文件内容的比例（缺省为0.3，即30%）
        [symmetrical](bool): 是否要求测试集与训练集对称（即每个主问题同时出现在两个中）
    '''
    if not symmetrical:
        main_file = main_path+main_filename
        main_text = helper.file_tools.read_txt_as_csv(main_file,divider='||')
        # print(main_text[0])
        main_line_num = len(main_text)
        test_num = int(1.0*main_line_num*test_rate)
        train_num = main_line_num - test_num
        # print('Start choose')
        test_text, train_text = helper.random_tools.random_choose(main_text, num=test_num,sort=False, split=True,seed=seed)
    else:
        test_text = []
        train_text = []
        too_few = 1
        not_mind = 1
        ori_dict = data_to_dict(main_path, main_filename, dump = False)
        main_dict = {}
        for sub_que in ori_dict.keys():
            main_que = ori_dict[sub_que][0]
            if main_que in main_dict.keys():
                main_dict[main_que].append([sub_que, main_que, ori_dict[sub_que][1]])
            else:
                main_dict[main_que] = [[sub_que, main_que, ori_dict[sub_que][1]]]
        for main_que in main_dict.keys():
            not_mind += 1
            if len(main_dict[main_que]) < 8:
                too_few += 1
            if len(main_dict[main_que]) < 4:
                test_buf = [main_dict[main_que][0]]
                train_buf = main_dict[main_que][0:]
            else:
                main_line_num = len(main_dict[main_que])
                test_num = int(1.0*main_line_num*test_rate)
                train_num = main_line_num - test_num
                main_buf = main_dict[main_que]
                test_buf, train_buf = helper.random_tools.random_choose(main_buf, num=test_num, sort=False, split=True,seed=seed)
            # print("test_buf:")
            # print(test_buf)
            # print("train_buf:")
            # print(train_buf)
            test_text.extend(test_buf)
            train_text.extend(train_buf)
        too_few_test = 1
        not_mind_test = 1
        for test_content in test_text:
            main_que = test_content[1]
            # print("test_content:")
            # print(test_content)
            # print("main_que:")
            # print(main_que)
            if len(main_dict[main_que]) < 8:
                too_few_test += 1
            not_mind_test += 1
    # print("too_few:")
    # print(too_few)
    # print("all_class:")
    # print(not_mind)
    # print("few_rate:")
    # print(too_few/not_mind)
    # print("too_few_test:")
    # print(too_few_test)
    # print("all_class_test:")
    # print(not_mind_test)
    # print("few_rate_test:")
    # print(too_few_test/not_mind_test)
    test_filename = test_train_path+'test_data.txt'
    train_filename = test_train_path+'train_data.txt'
    with open(test_filename,'w') as test_file:
        test_file.write('\n'.join((['||'.join(text) for text in test_text]))+'\n')
    with open(train_filename,'w') as train_file:
        train_file.write('\n'.join((['||'.join(text) for text in train_text]))+'\n')


def dict_reverse(ori_dict, place = 1):    
    main_dict = {}
    for sub_que in ori_dict.keys():
        main_que = ori_dict[sub_que][0]
        if main_que in main_dict.keys():
            main_dict[main_que].append([sub_que, main_que, ori_dict[sub_que][place]])
        else:
            main_dict[main_que] = [[sub_que, main_que, ori_dict[sub_que][place]]]
    return main_dict


def data_to_dict(data_path='../../database/main-data/', data_filename='main_data.txt', dump=True, dump_path='',dump_filename=''):
    '''
        本函数用于将数据文件转化为dict并利用pickle.dump生成model文件以保存（同时可以返回所得字典）
        [data_path](str): 待转化数据文件所在的目录
        [data_filename](str): 待转化数据文件的文件名
        [dump](bool): 是否生成model文件（缺省为是）
        [dump_path](str): dump所得文件的目录
        [dump_filename](str): dump所得文件的文件名
    '''
    if not dump_path:
        dump_path = data_path
    if not dump_filename:
        dump_filename = data_filename+'.model'
    data_file = data_path+data_filename
    data_text = helper.file_tools.read_txt_as_csv(data_file,divider='||')
    data_dict = helper.dict_tools.list_to_dict(data_text)
    if dump:
        dump_file = open(dump_path + dump_filename,'wb')
        pickle.dump(data_dict, dump_file)
        if dump_file:
            dump_file.close()
    return data_dict

def main_to_class(main_path='../../database/main-data/',main_filename='main_data.txt',
                  class_path='../../database/others/main-to-class/',class_filename='main_to_class.txt.model'):
    '''
        本函数用于生成按大类分类的数据文件
        [main_path](str): 主数据文件所在的目录
        [main_filename](str): 主数据文件的文件名
        [class_path](str): 大类数据文件所生成的目录
        [class_filename](str): 大类数据文件的文件名
    '''
    main_file = main_path+main_filename
    class_file = class_path+class_filename
    dic = {}
    with open(main_file, 'r') as f:
        data = f.readlines()
        for x in data:
            row = x.split('\n')[0].split('||')
            dic[row[1]] = row[2]
    with open(class_file, 'wb') as f1:
        pickle.dump(dic, f1)
    return dic
    # print(dic)

