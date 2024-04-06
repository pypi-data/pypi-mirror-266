'''
Date         : 2024-04-04 16:14:14
Author       : BDFD,bdfd2005@gmail.com
Github       : https://github.com/bdfd
LastEditTime : 2024-04-04 17:33:31
LastEditors  : <BDFD>
Description  : 
FilePath     : \execdata\graph\_linear_regression_type_graph.py
Copyright (c) 2024 by BDFD, All Rights Reserved. 
'''
from tabulate import tabulate
import matplotlib.pyplot as plt


def discrete_feature_graph(df, target_feature, numerical_features):
    # suitable for continous value prediction like linear regression model
    # Numerical variables are usually of 2 type
    # 1. Continous variable and Discrete Variables
    discrete_feature_list = [
        feature for feature in numerical_features if len(df[feature].unique()) < 25]
    print("Discrete Variables Count: {}".format(len(discrete_feature_list)))
    for feature in discrete_feature_list:
        dataset = df.copy()
        dataset.groupby(feature)[target_feature].median().plot.bar()
        plt.xlabel(feature)
        plt.ylabel(target_feature)
        plt.title(feature)
        plt.show()
    return discrete_feature_list
