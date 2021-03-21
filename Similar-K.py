# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 15:13:00 2021
相似K线
从4127只股票历史数据中查找相似K线，并统计，预测5日后涨幅

@author: 86518
"""


# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 13:29:03 2021

@author: 86518
"""


import tensorflow as tf
import pandas as pd
from pandas import DataFrame
import tushare as ts
import time
import numpy as np
import matplotlib.pyplot as plt

path2 = 'C:\\Users\\86518\\Desktop\\lianghua\\data\\k-data\\'
path_train = 'C:\\Users\\86518\\Desktop\\lianghua\\data\\train.xlsx'
data_list=[-1,1.15,-1.85,0.86,3.21,0.03,4.07,1.54]

similar_list=[]
similar_v=[]
change_5day=[]
S_V=1
prediction=0
def data_compare(data1,data2): 
    res=(data1-data2)*(data1-data2)
    res=np.mean(res)
    return res
    
    
def data_find(data1):
    global prediction
    l1=len(data1)
    data1=np.array(data1)
    code = pd.read_excel(path_train,header = 0)
    for row in code.itertuples():
        print(prediction)
        ts_code=getattr(row, 'ts_code')
        print(ts_code)
        file=path2+ts_code+'.xlsx'
        data_base = pd.read_excel(file,header = 0)
        L=len(data_base)
        if L<l1:continue
        for i in range(L-l1-7):          
            data2=data_base.iloc[i:i+l1,8:9]
            data2=data2.values
            data2=np.ravel(data2)
            
            data_5day=data_base.iloc[i+l1+1:i+l1+6,8:9]
            data_5day=data_5day.values
            data_5day=data_5day.sum()
            res=data_compare(data1,data2)
            # print(res)
            if res<S_V:
                similar_list.append(data2)
                similar_v.append(res)
                change_5day.append(data_5day)
                prediction=np.mean(change_5day)
                


data_find(data_list)
num=len(similar_v)
print(num)

show_num=9
if show_num>num:
    show_num=num
    
for i in range(show_num):
    plt.plot(np.arange(len(data_list)), data_list,color='#00E5EE',linewidth=1)
    plt.plot(np.arange(len(similar_list[i])), similar_list[i],color='r',linewidth=1)
    # print(similar_v[i])

plt.show()

    
    