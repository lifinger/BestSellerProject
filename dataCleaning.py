# -*- coding: utf-8 -*-
import pandas as pd
import os


"""得到产品的单价以及该产品在此类产品中的价格层次，低中高-012"""
def productUnitPrice(categories):
    def unit_type(row):
    # assign the cloth to cheap, medium, expensive accoding to its price
        c = row["大类名称"]
        df_c = grouped_cate.loc[c]
        price = row["unitPrice"]
        if price < df_c.loc[0.3][0]:
            flag = 0
        elif price < df_c.loc[0.7][0]:
            flag = 1
        else:
            flag = 2
        row["type"] = flag
        return row
    data = pd.read_csv("./data/rawdata_online.csv")
    data = data[data["大类名称"].isin(categories)]
    df = data[["15位产品号", "销售数量", "大类名称","实际付款金额(几件的和)"]]
    df = df[df["销售数量"]==1]

    df_cate = df[["大类名称","实际付款金额(几件的和)"]]
    grouped_cate = df_cate.groupby("大类名称").quantile([0.3,0.7])



    grouped = df[["15位产品号","实际付款金额(几件的和)"]].groupby("15位产品号").mean()
    grouped = grouped.rename(index=str,columns = {"实际付款金额(几件的和)":"unitPrice"})
    grouped["15位产品号"] = grouped.index

    joined1 = pd.merge(left=grouped,right=df[["15位产品号","大类名称"]].drop_duplicates(),on="15位产品号",how="left")
    joined = joined1.apply(unit_type,axis=1)

    joined.to_csv("./data/product_price.csv",index=False)

"""
在通过louvain得到每一类产品的group类别后，
并且分离出产品的单价以及价格层次后，
将用户购买历史的records与以上两个表格进行合并。
得到统一的大表。
"""
def generateTable(path,categories):
    """这里有一点问题，很多重复值，待审查，目前直接将union.drop_duplicates()"""
    def _eliminate_small_group(df,threshold=100):
        df = df.groupby("group").filter(lambda x: len(x["group"]) > threshold)
        return df
    # clean and tidy rawdata
    raw = pd.read_csv("./data/rawdata_online.csv")
    user = raw[["VIP_ID","性别","vip等级","注册渠道"]].drop_duplicates()
    data = pd.read_csv("./data/rawdata_censored.csv",index_col=0)
    # censored 数据里面是有duplicate的数据的，我们目前认为这些重复的数据是正常的。
    df_price = pd.read_csv("./data/product_price.csv")

    del(df_price["大类名称"])
    joined = pd.merge(left=data,right=df_price,on="15位产品号",how="left")

    # read all sub-group files
    categories.remove("Acc")
    subpath = os.path.join(path,"Acc")
    file = os.path.join(subpath,"group_with_id_Acc.csv")
    df_tot = pd.read_csv(file,index_col=0)
    df_tot["group"] = df_tot["group"].apply(lambda x: "Acc" + "_" + str(x))
    for cate in categories:
        subpath = os.path.join(path,cate)
        file = os.path.join(subpath,"group_with_id_"+cate+".csv")
        if os.path.exists(file):
            df_sub = pd.read_csv(file,index_col=0)
            df_sub["group"] = df_sub["group"].apply(lambda x:cate + "_"+str(x))
            df_tot = pd.concat([df_tot,df_sub],ignore_index=True)

    # 由于只考虑了部分categories，所以这里产品的数量由7w->1.9w
    df_tot = _eliminate_small_group(df_tot,threshold=100)


    df = pd.merge(left=joined,right=df_tot,on="15位产品号",how="inner")
    union = pd.merge(left=df,right=user,on="VIP_ID",how="inner")
    cols = ["VIP_ID","性别","vip等级","注册渠道","15位产品号","销售数量","unitPrice","type","group","大类名称"]
    union = union[cols]
    union.to_csv("./data/rawdata_union.csv")
    return df


"""通过用户对每个community的购买记录，将每个用户转换成一个向量"""
def generateVector(union):
    grouped = union.groupby("VIP_ID")
    df = pd.DataFrame()
    i = 0
    for group in grouped:
        i +=1
        if i%100 == 0:
            print i
        uid = group[0]
        user_df = group[1]
        user_group_df = user_df[["销售数量","group"]].groupby("group").count().transpose()
        user_group_df.index = [uid]
        df = pd.concat([df,user_group_df])
    df = df.fillna(0)
    return df


    pass
if __name__ == "__main__":
    categories = ["Acc", "Blazer", "Dress", "JLACC", "Knit", "Leather", "Outwear", "Pants Denim", \
                  "Pants Non Denim", "Polo", "Shirt", "Skirt", "Sweat", "Top Jersey", "Top Woven"]
#    productUnitPrice(categories)
#     df = generateTable("./result_dim_200/",categories)
#
#     union = pd.read_csv("./data/rawdata_union.csv",index_col=0)
#     df = generateVector(union)
#     df.to_csv("./data/rawdata_userVector.csv")


