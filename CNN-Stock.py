# -*- coding: utf-8 -*-
"""


使用卷积网络对历史股票数据学习，然后预测

@author: 86518
"""

import tensorflow as tf
import pandas as pd
from pandas import DataFrame
import tushare as ts
import time
import numpy as np

tf.reset_default_graph()
BATCH_SIZE=128
path_train='C:\\Users\\86518\\Desktop\\lianghua\\data\\test.xlsx'
path2 = 'C:\\Users\\86518\\Desktop\\lianghua\\'

#使用个人Tushare code
mytoken = '*****'

capacity=100000
data_list=[]
vol_list=[]
lable_list=[]
memory_dd = np.zeros((capacity,10,4,1),dtype=float)
memory_vv = np.zeros((capacity,10,1),dtype=float)
memory_rr = np.zeros((capacity,1),dtype=float)
mun=0
pro = ts.pro_api()

# df = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
code = pd.read_excel(path_train,header = 0)

for row in code.itertuples():
    # print(getattr(row, 'ts_code'))
    data = ts.pro_bar(ts_code=getattr(row, 'ts_code'), adj='qfq', start_date='20100101', end_date='20210316')
    data = pd.DataFrame(data)
    L=len(data)
    if L<12:continue
    for i in range(L-11):
        dd=data.iloc[i:i+10,2:6]
        vv=data.iloc[i:i+10,9:10]
        r0=data.iloc[i+10:i+11,8:9]
        if r0.iloc[0,0]>0.2:r=1
        else:r=0
        dd=dd.values
        dd=dd/dd[0][0]
        dd = dd[:,:,np.newaxis]
        vv=vv.values
        vv=vv/vv[0]
        # print(dd)
        memory_dd[mun,:,:,:]=dd
        memory_vv[mun,:,:]=vv
        memory_rr[mun,:]=r
        mun+=1
print(mun)
print(memory_dd[0,:,:,:])
print(memory_vv[0,:,:])
print(memory_rr[0,:])

S_D = tf.placeholder(tf.float32, shape=[None,10,4,1], name='dd')
S_V = tf.placeholder(tf.float32, shape=[None,10,1], name='vv')
S_R = tf.placeholder(tf.float32, shape=[None,1], name='rr')

class Actor(object):
    def __init__(self):
        self.sess = tf.Session() 
        self.a = self.build_net(S_D,S_V)
    def learn(self): 
        # Minimize the mean squared errors.
        loss = tf.reduce_mean(tf.square(S_R-self.a)) #计算平均误差
        optimizer = tf.train.GradientDescentOptimizer(0.0001) #设置梯度下降优化参数，学习率等
        train = optimizer.minimize(loss)#处理梯度计算和参数更新两个操作
        
        # Before starting, initialize the variables. We will 'run' this first.
        init = tf.global_variables_initializer()
        
        # Launch the graph.
        # sess = tf.Session()
        self.sess.run(init)
        
        # Fit the line.
        for step in range(150000):
            indices = np.arange(mun)
            indx = np.random.choice(indices, size=BATCH_SIZE)
            data_dd = memory_dd[indx,:,:,:]      
            
            data_vv = memory_vv[indx,:,:]    
            
            data_rr = memory_rr[indx,:] 
                        
            self.sess.run(train,feed_dict={S_D:data_dd,S_V:data_vv,S_R:data_rr})
            if step % 50 == 0:
                print(step, self.sess.run(loss,feed_dict={S_D:data_dd,S_V:data_vv,S_R:data_rr}))
        
    def build_net(self,dd,vv):
        n_l1 = 164
        FD2=128
        FV2=64
        init_w = tf.random_normal_initializer(0., 0.01)
        init_b = tf.constant_initializer(0.01)
        d_conv1 = tf.layers.conv2d(inputs=dd, filters=16, kernel_size=3, strides=1,padding='valid',name='dcon1', activation=tf.nn.relu, kernel_initializer=init_w, bias_initializer=init_b)
        d_conv2 = tf.layers.conv2d(inputs=d_conv1, filters=32, kernel_size=2, strides=1,padding='valid',name='dcon2', activation=tf.nn.relu, kernel_initializer=init_w, bias_initializer=init_b)     
        d_f = tf.layers.flatten(d_conv2,name='dfla')
        d_f=tf.layers.dense(d_f,FD2, name='fid', activation=tf.nn.relu,kernel_initializer=init_w, bias_initializer=init_b)
        
        v_conv1 = tf.layers.conv1d(inputs=vv, filters=16, kernel_size=3, strides=1,padding='valid',name='vcon1', activation=tf.nn.relu, kernel_initializer=init_w, bias_initializer=init_b)
        v_conv2 = tf.layers.conv1d(inputs=v_conv1, filters=32, kernel_size=2, strides=1,padding='valid',name='vcon2', activation=tf.nn.relu, kernel_initializer=init_w, bias_initializer=init_b)     
        v_f = tf.layers.flatten(v_conv2,name='vfla')
        v_f=tf.layers.dense(v_f,FV2, name='fiv', activation=tf.nn.relu,kernel_initializer=init_w, bias_initializer=init_b)  
        

        w1_d = tf.get_variable('w1_d', [FD2, n_l1], initializer=init_w)
        w1_v = tf.get_variable('w1_v', [FV2, n_l1], initializer=init_w)
        b1 = tf.get_variable('b1', [1, n_l1], initializer=init_b)
        net = tf.nn.relu(tf.matmul(d_f, w1_d) + tf.matmul(v_f, w1_v) + b1)
        l1 = tf.layers.dense(net,100,activation=tf.nn.relu, kernel_initializer=init_w, bias_initializer=init_b,name='l1')
        actions = tf.layers.dense(l1,1,activation=tf.nn.sigmoid, kernel_initializer=init_w, bias_initializer=init_b,name='a')
        return actions
    
    def save(self,path):
        saver = tf.train.Saver()
        saver.save(self.sess, path, write_meta_graph=True)

    def restore(self,path):
        saver = tf.train.Saver()
        saver.restore(self.sess,path)     


actor = Actor()
actor.learn()
# path_save = './log/'
# actor.save(path_save)
        
