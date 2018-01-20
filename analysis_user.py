# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

"""使用keyword作为人群分割的字段，然后观察不同人群的向量distribution"""
def dist_group(df,keyword,cols,threshold=100):
    plt.figure(1)
    grouped = df.groupby(keyword)
    categories = df[keyword].drop_duplicates().tolist()
    n = len(cols)
    width = 0.95/len(categories)
    X = np.arange(n)+1
    dic = {"性别":"gender","vip等级":"vipLevel",\
           "准会员":"associate","金卡会员":"gold","银卡会员":"silver","普通会员":"general",\
           "注册渠道":"registration-channel","POS":"POS","官网":"official-website","微购物":"wei-shopping","数云淘宝":"taobao","门店":"physical store"}
    j=0
    legendName =[]
    for c in categories:
        group = grouped.get_group(c)
        if len(group) > threshold:
            num_people = len(group)
            group = group[cols].mean()
            plt.bar(X + width*j,group.values,width=width,edgecolor="white")
            j+=1
            legendName.append(dic[c]+"&"+str(num_people))
            legend = group.index.tolist()
    plt.legend([dic[keyword] +"-"+ c for c in legendName])
    plt.xticks(X,legend,rotation=60)
    plt.show()

if __name__ == "__main__":
    cols = ['Acc_0', 'Acc_1', 'Acc_3', 'Blazer_0', \
            'Blazer_1', 'Blazer_3', 'Blazer_4', 'JLACC_1', \
            'Knit_0', 'Knit_1', 'Knit_3', 'Knit_5', 'Leather_1',\
            'Outwear_0', 'Outwear_1', 'Outwear_2', 'Polo_0', 'Polo_1', \
            'Polo_2', 'Skirt_0', 'Skirt_1', 'Skirt_2', 'Sweat_0',\
            'Sweat_2', 'Top Woven_0', 'Top Woven_1', 'Top Woven_2', \
            'Top Woven_3']

    df = pd.read_csv("./data/rawdata_userVector.csv")
    dist_group(df,"性别",cols)
