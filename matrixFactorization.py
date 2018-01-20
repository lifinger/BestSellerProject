# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib
import networkx as nx
from sklearn.decomposition import NMF
import scipy as sp
import time
import os
import community

class mf:
    def __init__(self,rawdata_path,categories,save_path="./result_dim_200/"):
        self._rawdata_path = rawdata_path
        self._categories = categories
        self._save_path = save_path

        self.df = self.load_data()
        self.G, self.uid,self.pid,self.A = self.build_graph()

        self.W,self.H = self.nmf()

    def load_data(self):
        try:
            df = pd.read_csv("./data/rawdata_censored.csv")
        except:
            data = pd.read_csv(self._rawdata_path)
            data = data[data["大类名称"].isin(self._categories)]
            df = data[["VIP_ID", "15位产品号", "销售数量", "大类名称"]]
            df = df[df["销售数量"] > 0]
            df.to_csv("./data/rawdata_censored.csv")
        return df

    def build_graph(self):
        print "\ngraph construction..."
        print time.ctime()
        G = nx.Graph()
        G.add_nodes_from(self.df["VIP_ID"].values, bipartite=0)
        G.add_nodes_from(self.df["15位产品号"], bipartite=1)
        G.add_weighted_edges_from([(r["VIP_ID"], r["15位产品号"], r["销售数量"]) for _, r in self.df.iterrows()])
        # uid = {n for n, d in G.nodes(data=True) if d['bipartite'] == 0}
        # pid = set(G) - uid
        # A = nx.algorithms.bipartite.biadjacency_matrix(G, row_order=uid)
        uid = list(self.df["VIP_ID"].drop_duplicates().values)
        pid = list(self.df["15位产品号"].drop_duplicates().values)
        A = nx.algorithms.bipartite.biadjacency_matrix(G,row_order=uid)
        return G,uid,pid,A

    def nmf(self):
        try:
            W = np.load(self._save_path + "/user-feature.npy")
            H = np.load(self._save_path + "/product-feature.npy")
        except:
            print "\nnon negative matrix factorization"
            print time.ctime()
            nmf = NMF(n_components=200)
            W = nmf.fit_transform(self.A)  # user - feature matrix
            H = nmf.components_  # product - feature matrix
            np.save(self._save_path + "/user-feature.npy", W)
            np.save(self._save_path + "/product-feature.npy", H)
        return W,H

    def execute(self):
        print "\ncompute dot product similarity..."
        product = pd.DataFrame({"15位产品号": self.pid, "feature": self.H.T.tolist()})
        product["feature"] = product["feature"].apply(lambda f: np.array(f))
        joined = pd.merge(left=product, right=self.df[["15位产品号", "大类名称"]].drop_duplicates(), how="inner", on="15位产品号")
        grouped = joined.groupby("大类名称")
        for category in self._categories:
            print "calculating for the category:" + category
            print time.ctime()
            sample_group = grouped.get_group(category)
            features = np.vstack(sample_group["feature"].values)
            similarityMat = sp.spatial.distance.cdist(features, features, lambda u,v: np.dot(u,v))
            # 保存产品id以及相似度矩阵
            path = self._save_path + category
            if not os.path.exists(path):
                os.mkdir(path)
            np.save(os.path.join(path,"similarityMat_"+category+".npy"), similarityMat)
            sample_group[["15位产品号"]].to_csv(os.path.join(path,"productID_"+category+".csv"), index=False)

if __name__ == "__main__":
    rawdata_path = "./data/rawdata_online.csv"
    categories = ["Acc", "Blazer", "Dress", "JLACC", "Knit", "Leather", "Outwear", "Pants Denim", \
                  "Pants Non Denim", "Polo", "Shirt", "Skirt", "Sweat", "Top Jersey", "Top Woven"]
    mf = mf(rawdata_path,categories=categories)
    mf.execute()