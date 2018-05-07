# -*- coding:utf-8 -*-
'''
本模块用于与每周简报相关的操作
'''
import re
import os
import sys
import csv
import xlrd
import codecs
import random
import chardet
import numpy as np
from .. import helper
from copy import deepcopy
from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.font_manager import _rebuild
from palettable.colorbrewer.qualitative import Dark2_7
#from markdown2pdf import convert_md_2_pdf as markdown2pdf
_rebuild()
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def build_weekly_brief(group_name='贝贝组', pre_path='../../document/weekly_brief/2017.2.26-2017.3.4/', last_week_time=[]):
    '''
        本函数用于生成每周简报的markdown文件
        [group_name](str): 组名（如：贝贝组）
        [pre_path](str): 组员报告文件及所在位置
        注：组长点评置于组员报告文件所在目录下的'Analysis'文件夹下，命名为'组长点评.md'
    '''
    briefs = os.listdir(pre_path)
    period=pre_path.split('/')[-2]
    people = {}
    if os.path.exists(pre_path+'Analysis') == False:
        os.mkdir(pre_path+'Analysis')
    for brief in briefs:
        if brief.startswith('.') == False and os.path.isdir(pre_path+brief) == False:
            file = codecs.open(pre_path+brief,'r', encoding='utf-8')
            content = file.readlines()
            # print(x)
            for line in content:
                if line.startswith('-'):
                    line='*'+line[1:]
                if line.startswith('# 每周周报 —'):
                    content_type = '姓名'
                    name_flag = 1
                elif line.startswith('* 汇报人'):
                    continue
                elif line.startswith('* 本周日期'):
                    content_type = '本周日期'
                elif line.startswith('* 本周工作时间'):
                    content_type = '本周工作时间'
                elif line.startswith('* 本周工作的主要内容'):
                    content_type = '本周工作的主要内容'
                elif line.startswith('* 本周学习的主要内容'):
                    content_type = '本周学习的主要内容'
                elif line.startswith('* 本周主要解决的问题及解决方法'):
                    content_type = '本周主要解决的问题及解决方法'
                elif line.startswith('* 本周尚未解决的问题'):
                    content_type = '本周尚未解决的问题'
                elif line.startswith('* 本周帮助PAIR解决的问题'):
                    content_type = '本周帮助PAIR解决的问题'
                elif line.startswith('* 下周主要工作目标'):
                    content_type = '下周主要工作目标'
                elif line.startswith('# '):
                    break
                #前两个只会执行一次，所以可以在内部初始化变量，后面就不行了
                if content_type == '姓名':
                    if name_flag == 1:
                        name=line.lstrip('# 每周周报 — ').rstrip('\n').strip()
                        people[name]={}
                    name_flag = 0
                elif content_type == '本周日期':
                    date = {}
                    buf_date = []
                    buf_date = line.lstrip('* 本周日期：').rstrip('\n').strip().split('~')
                    date['start'] = buf_date[0]
                    date['end'] = buf_date[-1]
                    people[name]['date'] = date
                elif content_type == '本周工作时间':
                    people[name]['time']=int(re.sub(r'\D', "", line))
                elif content_type == '本周工作的主要内容':
                    if '本周工作的主要内容' not in people[name].keys():
                        #如果要保留第一行（带星号的行）则这个地方的↓引号改成line即可，下面同理
                        people[name]['本周工作的主要内容'] = ''
                    else:
                        people[name]['本周工作的主要内容'] += line
                elif content_type == '本周学习的主要内容':
                    if '本周学习的主要内容' not in people[name].keys():
                        people[name]['本周学习的主要内容'] = ''
                    else:
                        people[name]['本周学习的主要内容'] += line
                elif content_type == '本周主要解决的问题及解决方法':
                    if '本周主要解决的问题及解决方法' not in people[name].keys():
                        people[name]['本周主要解决的问题及解决方法'] = ''
                    else:
                        people[name]['本周主要解决的问题及解决方法'] += line
                elif content_type == '本周尚未解决的问题':
                    if '本周尚未解决的问题' not in people[name].keys():
                        people[name]['本周尚未解决的问题'] = ''
                    else:
                        people[name]['本周尚未解决的问题'] += line
                elif content_type == '本周帮助PAIR解决的问题':
                    if '本周帮助PAIR解决的问题' not in people[name].keys():
                        people[name]['本周帮助PAIR解决的问题'] = ''
                    else:
                        people[name]['本周帮助PAIR解决的问题'] += line
                elif content_type == '下周主要工作目标':
                    if '下周主要工作目标' not in people[name].keys():
                        people[name]['下周主要工作目标'] = ''
                    else:
                        people[name]['下周主要工作目标'] += line

    labels = [name for name in people.keys()]
    #每个标签占多大，会自动去算百分比
    sizes_now = [people[name]['time'] for name in people.keys()]
    sizes_last = sizes_now
    #将某部分爆炸出来， 使用括号，将第一块分割出来，数值的大小是分割出来的与其他两块的间隙
    # explode = (0.05,0,0)
    # cmap=plt.get_cmap('Pastel1')

    #**************
    '''
    这里用来生成两幅图
    '''
    title_pie = group_name+'成员本周工作时间情况'
    helper.draw_tools.draw_pie(title_pie,labels, sizes_now, output_path=pre_path+'Analysis/time_pie_graph.jpg')
    title_bar = group_name+'成员本周与上周工作时间对比图'
    other_sizes = sizes_now
    sub_labels = ['上周','本周']
    helper.draw_tools.draw_bar(title_bar, labels, sizes_last, 
        other_sizes=other_sizes, sub_labels=sub_labels, 
        output_path=pre_path+'Analysis/time_bar_graph.jpg')
    # *************
    if not os.path.exists(pre_path+'Analysis/组长点评.md'):
        open(pre_path+'Analysis/组长点评.md', 'w', encoding='utf-8')
    with codecs.open(pre_path+'Analysis/组长点评.md','r',encoding='utf-8') as dp:
        conclu=dp.read()
    with codecs.open(pre_path+'Analysis/group_weekly_brief.md','w+',encoding='utf-8') as gwb:
        gwb.write('# '+group_name+'每周周报\n\n\
## 本周日期：{}\n\
{}\n\
## 本周工作时间统计：\n\
!['+group_name+'成员本周与上周工作时间对比图](./time_bar_graph.jpg)\n\n\
!['+group_name+'成员本周工作时间饼图](./time_pie_graph.jpg)\n\
## 本周工作的主要内容：\n\
{}\n\
## 本周主要解决的问题及解决方法：\n\
{}\n\
## 本周尚未解决的问题：\n\
{}\n\
## 下周主要工作目标：\n\
{}\n'.format(period,conclu,'\n'.join(['### '+x+'\n```\n'+people[x]['本周工作的主要内容'].strip('\n')+'\n```' for x in people.keys() if '本周工作的主要内容' in people[x].keys()]),\
        '\n'.join(['### '+x+'\n```\n'+people[x]['本周主要解决的问题及解决方法'].strip('\n')+'\n```' for x in people.keys() if '本周主要解决的问题及解决方法' in people[x].keys()]),\
        '\n'.join(['### '+x+'\n```\n'+people[x]['本周尚未解决的问题'].strip('\n')+'\n```' for x in people.keys() if '本周尚未解决的问题' in people[x].keys()]),\
        '\n'.join(['### '+x+'\n```\n'+people[x]['下周主要工作目标'].strip('\n')+'\n```' for x in people.keys() if '下周主要工作目标' in people[x].keys()])))
    # markdown2pdf(pre_path+'Analysis/group_weekly_brief.md', output=pre_path+'Analysis/group_weekly_brief.pdf', theme=solarized-dark)
