import os
import pandas as pd
from matplotlib import pyplot as plt
try:
    import cPickle as pickle
except:
    import pickle


def update_class(data_src = '../../database/main-data/main_data.txt',class_model = '../../database/others/main-to-class/class.model'):
    with open(data_src, 'r') as f:
        try:
            with open(class_model, 'rb') as f2:
                dict_class = pickle.load(f2)
        except:
            dict_class = {}
        finally:
            g = [x.split('\n')[0].split('||')[2] for x in f.readlines()]
            for classes in g:
                row = classes.split('-')
                dic_now = dict_class
                for x in range(0, len(row)):
                    if row[x] not in dic_now.keys():
                        dic_now[row[x]] = {}
                    dic_now = dic_now[row[x]]
    with open(class_model, 'wb') as f3:
        pickle.dump(dict_class, f3)


def load_class(class_model = '../../database/others/main-to-class/class.model'):
    '''
        本函数用于
    '''
    with open(class_model, 'rb') as f:
        classes = pickle.load(f)
    return classes


def get_num_of_data(filepath = '../../database/daily-data/'):
    num = 0
    pathDir = os.listdir(filepath)
    for allDir in pathDir:
        if allDir.split('.')[1] == 'xlsx':
            try:
                with open(filepath+allDir, 'rb') as f:
                    num += len(f.readlines())
            except:
                print(allDir)
    return num


def analyze_data(filename='../../database/main-data/main_data.txt',max=200,min=5,
                top_filepath='top.txt',bottom_filepath='bottom.txt'):
    '''

    '''
    with open(filename, 'r') as f:
        g = [x.split('\n')[0].split('||')[2] for x in f.readlines()]
        h = list(set(g))
        total = []
        for item in h:
            total.append(item+','+str(g.count(item)))
        top_class=[]
        bottom_class=[]
        for arow in total:
            if int(arow.split(',')[1]) >= max:
                top_class.append(arow)
            if int(arow.split(',')[1]) <= min:
                bottom_class.append(arow)
        with open(top_filepath,'w') as f1:
            f1.write('\n'.join(top_class))
        with open(bottom_filepath,'w') as f2:
            f2.write('\n'.join(bottom_class))


def analyze_data_to_img(filename='database/main-data/main_data.txt'):
    with open(filename, 'r') as f:
        g = [x.split('\n')[0].split('||')[2] for x in f.readlines()]
        h = list(set(g))
        total = []
        for item in h:
            total.append(g.count(item))
    df=pd.DataFrame()
    df["数据分布箱型图"]=total
    plt.boxplot(x=df.values,labels=df.columns,whis=1.5)
    plt.show()


# analyze_data_to_img()