import codecs
import pandas as pd
import numpy as np
import re
import os
import sys
try:
    import cPickle as pickle
except:
    import pickle



def load_test(filename='../../database/test_train/test_data.txt.model'):
    '''
        用作加载测试字典，加快测试速度，字典格式：
        key：客户问题  value：[主问题，分类]
    '''
    f = open(filename, 'rb')
    data = pickle.load(f)
    return data


def load_train(filename='../../database/test_train/train_data.txt.model'):
    '''
        用作加载测试字典，加快测试速度，字典格式：
        key：客户问题  value：[主问题，分类]
    '''
    f = open(filename, 'rb')
    data = pickle.load(f)
    return data


def load_main2class(filename='../../database/others/main-to-class/main_to_class.txt.model'):
    '''
        用作加载主问题到分类的字典，加快测试速度，字典格式：
        key：主问题  value：分类
    '''
    f = open(filename, 'rb')
    data = pickle.load(f)
    return data


def test(result_list, test_way=1, top_num=1):
    '''
        测试函数：
        result_list为用户输入的预测结果list，数据格式为n*2，每一行为客户问题以及预测的主问题（类别）
        test_way为测试方式，默认为1->主问题预测，还可以为(2～5)->问题类别预测
        top_num为给出的候选个数
        返回值为dict形式，格式为：
        主问题：[问题类别，测试数量，top1正确数量，top1正确率, ...]   2n+2
        总结果：[测试数量，top1正确数量，top1正确率，...]            2n+1
    '''
    n = min(top_num, len(result_list[0])-1)                         # 候选集长度
    dic_main2class = load_main2class()                              # 主问题到类别的字典
    dic_test = load_test()                                          # 用来比对的字典
    test_result = {}                                                # test_result为测试的结果字典，用于绘制饼图
    test_result['total_result'] = [0 for x in range(0,2*n+1)]       # total_result为总的测试统计
    data_length = len(result_list)                                  # 测试总数
    test_result['total_result'][0] = data_length
    for x in range(0, data_length):
        if test_way == 1:
            if result_list[x][0] not in test_result.keys():
                new_main_que = dic_test[result_list[x][0]][0]       # 添加新的主问题
                test_result[new_main_que] = [0 for y in range(0, 2*n+2)]
                test_result[new_main_que][0] = dic_main2class[new_main_que]
                test_result[new_main_que][1] = 1
            else:
                test_result[dic_test[result_list[x][0]][0]][1] += 1
            for y in range(1, n+1):
                if dic_test[result_list[x][0]][0] in topn_predict(result_list[x],y): # 预测对
                    test_result[dic_test[result_list[x][0]][0]][2*y] += 1
                    test_result['total_result'][2*y-1] += 1
        else:
            pass
    for x in range(1, n+1):
        test_result['total_result'][2*x] = test_result['total_result'][2*x-1]*1.0/test_result['total_result'][0]
    for x in test_result.keys():
        if x != 'total_result':
            for y in range(1, n+1):
                test_result[x][2*y+1] = test_result[x][2*y]*1.0/test_result[x][1]    
    return test_result


def topn_predict(predict_list, n):
    '''
    辅助测试函数，获取用户提供的list中置信度最高的n个预测
    '''
    return [predict_list[x] for x in range(1, n+1)]

# # 以下是zzy的代码

# def match_directly(query):
#     df = pd.read_excel('../source/knowledge_for_matching.xlsx')
#     for i in range(df.shape[0]):
#         droped_line= df.iloc[i].dropna()
#         for j in range(3,len(droped_line)):
#             cell = droped_line[j]
#             pattern = re.compile(cell)
#             match = pattern.match(query)
#             if match:
#                 return df.iloc[i][0]
#     return None


# def ljzzy():
#     dft= pd.read_excel('../test/test_2017-12-21_processed.xlsx')
#     f = codecs.open("result.txt", 'w+',encoding='utf-8')
#     wrong_add=False
#     wrong_question_set = []
#     sentencesNum = 0
#     correctPrediction = 0
#     top3correctPrediction = 0
#     top5correctPrediction = 0

#     print(u"Start checking!\n-----------------------------------------------------------", file=f)

#     standard_ques_list = dft[u'标准问题'].dropna()
#     query_list = dft[u'问题']
#     counter = 0
#     for key_num in standard_ques_list.keys():
#         real_answer = standard_ques_list[key_num]
#         query = query_list[key_num]
#         print(real_answer,query)
#         sentencesNum += 1
#         similarity_top_list = []
#         wrong_question_set.append([])
#         wrong_question_set[counter].append(key_num)
#         result_direct = match_directly(query)
#         if result_direct != None:
#             top3correctPrediction += 1
#             top5correctPrediction += 1
#             correctPrediction +=1
#     #                 print result_direct,str(sentence).strip()
#             print(u'-----------------------------------------------------------', file=f)
#             print(u'本次结果为直接正则匹配得来，本次的问题为：{},匹配得到的主问题为：{}'.format(query,result_direct), file=f)
#             print(u'在前5列表中的共有：{} 个，共判断了 {} 个，正确率为：{}'.format(top5correctPrediction, sentencesNum, top5correctPrediction/sentencesNum), file=f)
#             print(u'在前3列表中的共有：{} 个，共判断了 {} 个，正确率为：{}'.format(top3correctPrediction, sentencesNum, top3correctPrediction/sentencesNum), file=f)
#             print(u'截至目前完全正确 ：{} 个，共判断了 {} 个，正确率为：{}'.format(correctPrediction, sentencesNum, correctPrediction/sentencesNum), file=f)
#             print(u'-----------------------------------------------------------', file=f)
#             print(u'\n\n\n', file=f)
#         else:
#             judgeIftheMainQuesPredictedIsCorrect(query, real_answer, counter, f, 1)
#         if counter%500 == 0:
#             pd.DataFrame(wrong_question_set).to_csv('wrong_ques_list.csv')
#         counter += 1
#         print(u"现在是第：",counter,u"个问题系", file=f)

#     print(u"正确率是："+str(correctPrediction/sentencesNum), file=f)
#     print(u"正确预测在前3中的概率是："+str(top3correctPrediction/sentencesNum), file=f)
#     print(u"正确预测在前5中的概率是："+str(top5correctPrediction/sentencesNum), file=f)
#     pd.DataFrame(wrong_question_set).to_csv('wrong_ques_list.csv')


# #Here is the test part of the algorithm,it can 
# #test the correct rate of the statistics way and the tf-idf way.
# #method: 0->statistic method 1->tf-idf method
# #Since the statistic method is deleted,you can only chose 1 to use tf-idf way.
# def judgeIftheMainQuesPredictedIsCorrect(question, real_answer, position, f, method):
#     global correctPrediction     #总共进行判定中完全正确的个数
#     global sentencesNum          #总共进行判断的句子数
#     global top3correctPrediction #正确结果在预测的前三中的个数
#     global top5correctPrediction #正确结果在预测的前五中的个数
#     global wrong_add             #一个判断是否要讲错误项输出到一个表格中的flag
#     global wrong_question_set    #用于记录判断错误的问题的数组
    
#     if method==0:#statistic method
#         similarity_top_list=getSimilarityStati(question)
#     elif method==1:#tf-idf method
#         similarity_top_list=getSimilarityTfIdf(question)
    
#     if len(similarity_top_list)!=0:
        
#         mostSimilarSentence=similarity_top_list[-1]

#         if  mostSimilarSentence == real_answer:
#             correctPrediction += 1
#         if real_answer in similarity_top_list[-3:]:
#             top3correctPrediction+=1
#         if real_answer in similarity_top_list[-5:]:
#             top5correctPrediction+=1

#         if wrong_add == True and real_answer not in similarity_top_list:
#             wrong_question_set[position].append(question)

# #     print mostSimilarSentence,real_answer,question,position
#     print(u'-----------------------------------------------------------', file=f)
#     print(u"similarity_top_list:", file=f)
#     print(cCode.str(similarity_top_list), file=f)
#     print(u"mostSimilarSentence:",mostSimilarSentence,u":standardSentenceTable:",real_answer,u"current question:",question, file=f)
#     print(u'在前5列表中的共有：{} 个，共判断了 {} 个，正确率为：{}'.format(top5correctPrediction, sentencesNum, top5correctPrediction/sentencesNum), file=f)
#     print(u'在前3列表中的共有：{} 个，共判断了 {} 个，正确率为：{}'.format(top3correctPrediction, sentencesNum, top3correctPrediction/sentencesNum), file=f)
#     print(u'截至目前完全正确 ：{} 个，共判断了 {} 个，正确率为：{}'.format(correctPrediction, sentencesNum, correctPrediction/sentencesNum), file=f)
#     print(u'-----------------------------------------------------------', file=f)
#     print(u'\n\n\n', file=f)


# # query = #u"刚才付过款商品想拍结果拍成请问您那里发货时发可以吗"#"免费试用要付钱吗"
# def getSimilarityTfIdf(query):
#     loc=[]
#     top5listbyTfIdf=[]
#     word_list = query_arrange_priority(query)
#     scoreNarrayQues = np.zeros(weightQues.shape[0])
    
#     for word in word_list:#查看个次的各toplic加分，加起来
#         if word !='' and word in wordsQues:          
#             iQues = wordsQues.index(word)
#             real_weight = map(lambda (a,b):a/b, zip(weightQues[:,iQues],key_word_num))
#             scoreNarrayQues += weightQues[:,iQues]
#     locQues = np.argsort(-scoreNarrayQues)
# #     print real_weight
    
# #     print weightQues[:,iQues]
#     if len(locQues)!=0 :
#         for i in range(5):
#             top5listbyTfIdf.append(df[u'问题'][locQues[i]])# index_list[loc[i]])
#         top5listbyTfIdf.reverse()
#         return top5listbyTfIdf
#     else:
#         return top5listbyTfIdf
# # print cCode.str(getSimilarityTfIdf(query))