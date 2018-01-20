# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import networkx as nx
import community
import matplotlib.pyplot as plt
import os
import time

class Partition:
    def __init__(self,path,category):
        print ("partition for the category:",category)
        print time.ctime()
        print "\n"
        self._path = os.path.join(path,category)
        self._category = category
        self.mat, self.id = self.load_data()


    def load_data(self):
        # 读取相似度矩阵和商品列表
        # def _mat_process(mat):
        #     mat[np.argwhere(np.isnan(mat))] = 0
        #     bins = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
        #     for threshold in bins:
        #         mat[np.argwhere(mat<threshold)] = 10*threshold
        #     return mat
        matPath = os.path.join(self._path, "similarityMat_" + self._category + ".npy")
        idPath = os.path.join(self._path, "productID_" + self._category + ".csv")
        mat = np.load(matPath)
        id = pd.read_csv(idPath)
        return mat,id

    def partition(self):
        graph = nx.from_numpy_matrix(self.mat)
        subgraphs = community.best_partition(graph)
        index_with_group = pd.DataFrame({"group":subgraphs.values()})
        id_with_group = pd.concat([self.id,index_with_group],axis=1)
        id_with_group.to_csv(self._path+"/group_with_id_"+self._category+".csv")




if __name__ == "__main__":
    # 由于当尺寸超过3000时，louvain速度极慢，这里只尝试一部分类别的衣服。
    categories = ["Acc", "Blazer", "JLACC", "Knit", "Leather", \
                  "Polo", "Sweat", "Top Woven", "Outwear", "Skirt"]

    for c in categories:
        sample = Partition("./result_dim_200/",c)
        sample.partition()


